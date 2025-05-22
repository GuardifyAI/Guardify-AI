from data_science.src.google.AnalysisModel import AnalysisModel
from data_science.src.google.ComputerVisionModel import ComputerVisionModel
import logging
from data_science.src.utils import create_logger, get_video_extension
from vertexai.generative_models import Part
from typing import List, Tuple, Dict
import numpy as np
import pickle
import datetime
import os

class ShopliftingAnalyzer:
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi'}
    VIDEO_MIME_TYPES = {
        "mp4": "video/mp4",
        "avi": "video/x-msvideo",
    }

    def __init__(self, cv_model: ComputerVisionModel, analysis_model: AnalysisModel, detection_strictness: float, logger: logging.Logger = None):
        """
        Initializes the ShopliftingAnalyzer, which coordinates the end-to-end analysis of a single video
        using computer vision and analytical models to detect shoplifting behavior.

        The analyzer iteratively calls GenAI-based components to improve confidence in detection results,
        and evaluates whether the confidence and consistency of results meet criteria to stop further analysis.

        Args:
            cv_model (ComputerVisionModel): The computer vision model for video analysis.
            analysis_model (AnalysisModel): The analysis model for interpreting video observations.
            detection_strictness (float): A threshold between 0 and 1 indicating the minimum required
                                                    confidence level to classify the video as containing shoplifting.
                                                    Higher values make the analyzer stricter (fewer false positives,
                                                    but may miss true positives); lower values make it more sensitive
                                                    (may detect more true positives, but at risk of false positives).
            logger (logging.Logger, optional): A logger instance for logging messages. If None, a default logger is created.
        """
        self.cv_model = cv_model
        self.analysis_model = analysis_model
        self.current_confidence_levels = []
        self.current_shoplifting_detected_results = []
        if detection_strictness < 0 or detection_strictness > 1:
            raise ValueError("Detection strictness must be between 0 and 1.")
        self.shoplifting_detection_threshold = detection_strictness
        if logger is None:
            self.logger = create_logger('ShopliftingAnalyzer', 'shoplifting_analysis.log')

    def analyze_video_from_bucket(self, video_uri: str, max_api_calls: int, pickle_analysis: bool = True) -> Dict:
        """
        Analyzes a video from Google Cloud Storage bucket.

        Args:
            video_uri (str): The GCS URI of the video
            pickle_analysis (bool, optional): Whether to save the analysis results to a pickle file. Defaults to True.
            max_api_calls(int): The maximum number of API calls to make before stopping the analysis.

        Returns:
            Dict: Analysis results including confidence levels, detection results, and model responses
            
        Raises:
            ValueError: If the video URI has an invalid or unsupported extension
        """
        # Validate video extension
        extension = get_video_extension(video_uri)
        if extension not in self.ALLOWED_VIDEO_EXTENSIONS:
            raise ValueError(f"'{extension}' is an unsupported video format. Supported formats are: {self.ALLOWED_VIDEO_EXTENSIONS}")
        video_part = Part.from_uri(uri=video_uri, mime_type=self.VIDEO_MIME_TYPES[extension])
        return self.analyze_video(video_part, video_uri, max_api_calls, pickle_analysis)

    def analyze_local_video(self, video_path: str, max_api_calls: int, pickle_analysis: bool = True) -> Dict:
        """
        Analyzes a local video file for shoplifting activity.

        Args:
            video_path (str): Path to the local video file
            pickle_analysis (bool, optional): Whether to save the analysis results to a pickle file. Defaults to True.
            max_api_calls(int): The maximum number of API calls to make before stopping the analysis.

        Returns:
            Dict: Analysis results including confidence levels, detection results, and model responses

        Raises:
            FileNotFoundError: If the video file doesn't exist
            ValueError: If the file is not a valid video file
        """
        extension = get_video_extension(video_path)
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at path: {video_path}")

        if extension not in self.ALLOWED_VIDEO_EXTENSIONS:
            raise ValueError(f"'{extension}' is an unsupported video format. Supported formats are: {self.ALLOWED_VIDEO_EXTENSIONS}")

        video_part = Part.from_data(
            mime_type=self.VIDEO_MIME_TYPES[extension],
            data=open(video_path, "rb").read()
        )
        return self.analyze_video(video_part, video_path, max_api_calls, pickle_analysis)

    def analyze_video(self, video_part: Part, video_identifier: str, max_api_calls: int, pickle_analysis: bool = True) -> Dict:
        """
        Analyzes a video for shoplifting activity using the provided video Part.

        Args:
            video_part (Part): The video Part object to analyze
            video_identifier (str): Identifier for the video (path or URI)
            pickle_analysis (bool, optional): Whether to save the analysis results to a pickle file. Defaults to True.
            max_api_calls(int): The maximum number of API calls to make before stopping the analysis.

        Returns:
            Dict: Analysis results including confidence levels, detection results, and model responses
        """
        cv_model_responses = []
        analysis_model_responses = []

        while self.should_continue(max_api_calls):
            self.logger.info(f"Sending video '{video_identifier}' to CV model for video description")
            cv_model_response = self.cv_model.analyze_video(video_part)  # Using default prompt
            self.logger.info(f"Sending video '{video_identifier}' to Analysis model for analysis of the video and results generation")
            analysis_model_response, shoplifting_detected, confidence_level = self.analysis_model.analyze_video_observations(
                video_part, cv_model_response)
            self.logger.debug(f"Shoplifting Detected: {shoplifting_detected}")
            self.logger.debug(f"Confidence Level: {confidence_level}")
            self.current_confidence_levels.append(confidence_level)
            self.current_shoplifting_detected_results.append(shoplifting_detected)
            cv_model_responses.append(cv_model_response)
            analysis_model_responses.append(analysis_model_response)
            self.logger.info(f"Finished {len(self.current_confidence_levels)} iterations of analysis for video '{video_identifier}'")

        stats = self.get_detection_stats_for_video()
        shoplifting_probability, shoplifting_determination = self.determine_shoplifting_from_stats(stats)
        analysis = {
            "video_identifier": video_identifier,
            "confidence_levels": self.current_confidence_levels,
            "shoplifting_detected_results": self.current_shoplifting_detected_results,
            "cv_model_responses": cv_model_responses,
            "analysis_model_responses": analysis_model_responses,
            "stats": stats,
            "shoplifting_probability": shoplifting_probability,
            "shoplifting_determination": shoplifting_determination
        }
        if pickle_analysis:
            self.save_analysis_to_pickle(analysis)

        self.current_confidence_levels = []
        self.current_shoplifting_detected_results = []
        self.logger.info(f"Finished analysis for video '{video_identifier}'")
        return analysis

    def should_continue(self, max_api_calls: int) -> bool:
        return (not self.current_confidence_levels or self.current_confidence_levels[-1] < 0.9) and len(
            self.current_confidence_levels) < max_api_calls and not self.has_reached_plateau()

    def has_reached_plateau(self) -> bool:
        if len(self.current_confidence_levels) < 3:
            return False
        return self.current_confidence_levels[-1] == self.current_confidence_levels[-2] == self.current_confidence_levels[-3]

    # TODO: add tests for edge cases
    def get_detection_stats_for_video(self) -> Dict | str:
        if not self.current_confidence_levels or not self.current_shoplifting_detected_results:
            return "Invalid input: One or both lists are empty."

        confidence_levels = np.array(self.current_confidence_levels)
        shoplifting_detected_results = np.array(self.current_shoplifting_detected_results)

        if confidence_levels.shape != shoplifting_detected_results.shape:
            return "Invalid input: The sh2apes of confidence_levels and shoplifting_detected_results do not match."

        true_count = np.sum(shoplifting_detected_results)
        false_count = shoplifting_detected_results.size - true_count

        avg_confidence_true = np.mean(confidence_levels[shoplifting_detected_results]) if true_count else 0
        avg_confidence_false = np.mean(confidence_levels[~shoplifting_detected_results]) if false_count else 0

        max_confidence_true = np.max(confidence_levels[shoplifting_detected_results]) if true_count else 0
        max_confidence_false = np.max(confidence_levels[~shoplifting_detected_results]) if false_count else 0

        return {
            'True Count': int(true_count),
            'False Count': int(false_count),
            'Average Confidence when True': round(float(avg_confidence_true), 4),
            'Average Confidence when False': round(float(avg_confidence_false), 4),
            'Highest Confidence when True': round(float(max_confidence_true), 4),
            'Highest Confidence when False': round(float(max_confidence_false), 4)
        }

    def save_analysis_to_pickle(self, analysis: Dict) -> None:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        pkl_path = f"video_analysis_{current_time}.pkl"

        with open(pkl_path, 'wb') as file:
            pickle.dump(analysis, file)

        self.logger.info(f"Finished with {analysis['video_identifier']}, results saved to {pkl_path}")

    # TODO: make the algorithm better. make it take into account also the False results.
    # TODO: Make this into an AI model that gets results as number and output the prediction
    def determine_shoplifting_from_stats(self, stats: dict) -> Tuple[float, bool]:
        # Calculate the weighted score
        count_weight = 0.5
        average_confidence_weight = 0.3
        highest_confidence_weight = 0.2

        # Normalize count to be between 0 and 1
        # Assuming the maximum expected count can be defined or observed from historical data
        # For demonstration, let's assume a maximum count of 10
        max_expected_count = 10
        normalized_count = stats['True Count'] / (stats["True Count"] + stats["False Count"])
        normalized_count = min(normalized_count, 1)  # Ensure it does not exceed 1

        average_confidence = stats['Average Confidence when True']
        highest_confidence = stats['Highest Confidence when True']

        # Calculate the final score using the specified weights
        final_score = (count_weight * normalized_count) + \
                      (average_confidence_weight * average_confidence) + \
                      (highest_confidence_weight * highest_confidence)
        self.logger.info(f"Final score: {final_score}, shoplifting_determination: {final_score >= self.shoplifting_detection_threshold}")
        # Check if the final score exceeds the threshold
        return final_score, final_score >= self.shoplifting_detection_threshold
