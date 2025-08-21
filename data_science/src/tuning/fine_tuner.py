import utils.env_utils as env_utils
from typing import Tuple, Dict, Literal
import os
import json
from google_client.google_client import GoogleClient
env_utils.load_env_variables()
import pickle
import cv2
from datetime import datetime
import pandas as pd
from data_science.src.model.agentic.prompt_and_scheme.analysis_prompt import enhanced_prompt

class FineTuner:
    google_client = GoogleClient(
        project=os.getenv("GOOGLE_PROJECT_ID"),
        location=os.getenv("GOOGLE_PROJECT_LOCATION"),
        service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
    )

    @staticmethod
    def make_images_dataset_for_analysis_model(frames_bucket: str,
                                                        input_prompt: str,
                                                        output_jsonl_path: str = None,
                                                        path_prefix_inside_bucket: str = None,
                                                        pickles_folder: str = None,
                                                        csv_path: str = None) -> None:
        """
        Creates a training dataset in JSONL format for Google's analysis model from either pickle files or CSV.
        Exactly one of pickles_folder or csv_path must be provided.

        This function takes analysis responses from either:
        - Pickle files: Each pickle should contain a dictionary with 'video_identifier' and 'iteration_results'
          where the first iteration has an 'analysis_response' field containing a JSON string
        - CSV file: Should have a 'video_identifier' column and additional columns for each analysis field
          (e.g., 'Shoplifting Detected', 'Confidence Level', 'Evidence Tier', etc.)

        The function then creates a JSONL file where each line contains:
        - User role: Image file URI and input prompt
        - Model role: The analysis response

        This format is compatible with Google's training data requirements for fine-tuning analysis models.

        Args:
            frames_bucket (str): Name of the Google Cloud Storage bucket containing frame images.
            input_prompt (str): Input prompt to the model to be included in the JSONL file.
            output_jsonl_path (str): Path to the output JSONL file.
            path_prefix_inside_bucket (str, optional): Path prefix inside the bucket for the frames.
            pickles_folder (str, optional): Path to the folder containing analysis pickle files.
            csv_path (str, optional): Path to the CSV file containing analysis responses.

        Raises:
            ValueError: If neither or both of pickles_folder and csv_path are provided.
        """
        # Set default output path if none provided
        if output_jsonl_path is None:
            current_date = datetime.now().strftime("%m_%d_%H_%M_%S")
            output_jsonl_path = f"images_dataset_{current_date}.jsonl"

        # Get results using helper function
        results = FineTuner._get_analysis_results_from_source(pickles_folder, csv_path)

        if not results:
            print("Warning: No results found to process")
            return

        with open(output_jsonl_path, "a") as f:
            for video_identifier, analysis_response in results.items():
                video_name = FineTuner.get_video_name_without_extension(video_identifier)
                path_inside_bucket = f"{path_prefix_inside_bucket}/{video_name}" if path_prefix_inside_bucket is not None else video_name
                num_frames = FineTuner.google_client.num_of_files_in_bucket_path(frames_bucket, path_inside_bucket)
                for i in range(num_frames):
                    # Construct file URI for the frame
                    file_uri = f"gs://{frames_bucket}/{path_inside_bucket}/{i}.png"
                    data_row = FineTuner._construct_image_data_row(file_uri=file_uri,
                                                                   input_prompt=input_prompt,
                                                                   output_text=analysis_response.replace('\n', ''))
                    f.write(data_row)

        print(f"Successfully created training dataset with {len(results)} analysis responses in JSONL file: {output_jsonl_path}")

    @staticmethod
    def make_videos_dataset_for_analysis_model(input_prompt: str,
                                                        output_jsonl_path: str = None,
                                                        pickles_folder: str = None,
                                                        csv_path: str = None) -> None:
        """
        Creates a training dataset in JSONL format for Google's analysis model from either pickle files or CSV.
        Exactly one of pickles_folder or csv_path must be provided.

        This function takes analysis responses from either:
        - Pickle files: Each pickle should contain a dictionary with 'video_identifier' and 'iteration_results'
          where the first iteration has an 'analysis_response' field containing a JSON string
        - CSV file: Should have a 'video_identifier' column and additional columns for each analysis field
          (e.g., 'Shoplifting Detected', 'Confidence Level', 'Evidence Tier', etc.)

        The function then creates a JSONL file where each line contains:
        - User role: Video file URI and input prompt
        - Model role: The analysis response

        This format is compatible with Google's training data requirements for fine-tuning analysis models.

        Args:
            input_prompt (str): Input prompt to the model to be included in the JSONL file.
            output_jsonl_path (str): Path to the output JSONL file.
            pickles_folder (str, optional): Path to the folder containing analysis pickle files.
            csv_path (str, optional): Path to the CSV file containing analysis responses.

        Raises:
            ValueError: If neither or both of pickles_folder and csv_path are provided.
        """
        # Set default output path if none provided
        if output_jsonl_path is None:
            current_date = datetime.now().strftime("%m_%d_%H_%M_%S")
            output_jsonl_path = f"videos_dataset_{current_date}.jsonl"

        # Get results using helper function
        results = FineTuner._get_analysis_results_from_source(pickles_folder, csv_path)

        if not results:
            print("Warning: No results found to process")
            return

        with open(output_jsonl_path, "a") as f:
            for video_identifier, analysis_response in results.items():
                # For videos, use the video_identifier directly as the file_uri
                file_uri = video_identifier
                data_row = FineTuner._construct_video_data_row(file_uri=file_uri,
                                                               input_prompt=input_prompt,
                                                               output_text=analysis_response.replace('\n', ''))
                f.write(data_row)

        print(f"Successfully created training dataset with {len(results)} analysis responses in JSONL file: {output_jsonl_path}")

    @staticmethod
    def _get_analysis_results_from_source(pickles_folder: str = None, csv_path: str = None) -> Dict[str, str]:
        """
        Helper function to get analysis results from either pickle files or CSV.
        Exactly one of pickles_folder or csv_path must be provided.

        Args:
            pickles_folder (str, optional): Path to the folder containing analysis pickle files.
            csv_path (str, optional): Path to the CSV file containing analysis responses.

        Returns:
            Dict[str, str]: Dictionary with video_identifier as keys and JSON strings as values.

        Raises:
            ValueError: If neither or both of pickles_folder and csv_path are provided.
        """
        # Validate that exactly one input source is provided
        if (pickles_folder is None and csv_path is None) or (pickles_folder is not None and csv_path is not None):
            raise ValueError("Exactly one of 'pickles_folder' or 'csv_path' must be provided")

        # Get results based on the input source
        if pickles_folder is not None:
            # Extract from pickle files
            results = FineTuner.extract_analysis_responses_from_all_pickles_in_folder(pickles_folder)
            print(f"Loaded {len(results)} responses from pickle files in: {pickles_folder}")
        else:
            # Extract from CSV file
            results = FineTuner.extract_analysis_responses_from_csv(csv_path)
            print(f"Loaded {len(results)} responses from CSV file: {csv_path}")

        return results

    @staticmethod
    def extract_unified_response_from_pickle(pickle_path: str) -> Tuple[str, str]:
        obj = FineTuner.load_pickle_object(pickle_path)
        # return the response of the first iteration
        return obj['video_identifier'], obj['iteration_results'][0]['full_response']

    @staticmethod
    def extract_analysis_response_from_pickle(pickle_path: str) -> Tuple[str, str]:
        obj = FineTuner.load_pickle_object(pickle_path)
        # return the response of the first iteration
        return obj['video_identifier'], obj['iteration_results'][0]['analysis_response']

    @staticmethod
    def extract_analysis_responses_from_all_pickles_in_folder(folder_path: str, export_csv: bool = False) -> Dict:
        """
        Extracts analysis responses from all pickle files in the specified folder.

        Args:
            folder_path (str): Path to the folder containing pickle files.
            export_csv (bool): Whether to export results to CSV. Defaults to False.

        Returns:
            Dict: Dict containing video identifier and analysis response.
        """
        results = dict()
        for filename in os.listdir(folder_path):
            if filename.endswith('.pkl'):
                full_path = os.path.join(folder_path, filename)
                video_identifier, analysis_response = FineTuner.extract_analysis_response_from_pickle(full_path)
                results[video_identifier] = analysis_response

        # Export to CSV if requested
        if export_csv:
            FineTuner._export_results_to_csv(results, folder_path)

        return results

    @staticmethod
    def _export_results_to_csv(results: Dict[str, str], folder_path: str) -> None:
        """
        Helper function to export results dictionary to CSV.

        Args:
            results: Dictionary with video_identifier as keys and JSON strings as values
            folder_path: Path where to save the CSV file
        """
        # Parse JSON strings and create DataFrame
        csv_data = []
        all_json_keys = set()

        # First pass: collect all possible JSON keys
        for video_identifier, json_string in results.items():
            try:
                json_data = json.loads(json_string)
                all_json_keys.update(json_data.keys())
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON for {video_identifier}")
                continue

        # Second pass: create rows with all columns
        for video_identifier, json_string in results.items():
            try:
                json_data = json.loads(json_string)
                row = {'video_identifier': video_identifier}

                # Add all JSON keys as columns
                for key in all_json_keys:
                    row[key] = json_data.get(key, None)

                csv_data.append(row)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON for {video_identifier}")
                continue

        # Create DataFrame and export to CSV
        df = pd.DataFrame(csv_data)
        current_date = datetime.now().strftime("%m_%d_%H_%M_%S")
        csv_filename = f"analysis_responses_{current_date}.csv"
        csv_path = os.path.join(folder_path, csv_filename)
        df.to_csv(csv_path, index=False)
        print(f"CSV exported to: {csv_path}")
        print(f"CSV contains {len(df)} rows and {len(df.columns)} columns")

    @staticmethod
    def extract_analysis_responses_from_csv(csv_path: str) -> Dict[str, str]:
        """
        Reads a CSV file created by _export_results_to_csv and converts it back to the original results format.

        Args:
            csv_path (str): Path to the CSV file to read

        Returns:
            Dict[str, str]: Dictionary with video_identifier as keys and JSON strings as values,
                           in the same format as returned by extract_analysis_responses_from_all_pickles_in_folder
        """
        try:
            # Read the CSV file
            df = pd.read_csv(csv_path)

            if df.empty:
                print(f"Warning: CSV file {csv_path} is empty")
                return {}

            # Check if required column exists
            if 'video_identifier' not in df.columns:
                raise ValueError("CSV must contain 'video_identifier' column")

            results = {}

            # Process each row
            for _, row in df.iterrows():
                video_identifier = row['video_identifier']

                # Create a dictionary from the row data, excluding video_identifier
                json_data = {}
                for column in df.columns:
                    if column != 'video_identifier':
                        value = row[column]

                        # Handle NaN values (convert to None)
                        if pd.isna(value):
                            value = None

                        json_data[column] = value

                # Convert the dictionary back to a JSON string
                json_string = json.dumps(json_data, ensure_ascii=False)
                results[video_identifier] = json_string

            print(f"Successfully loaded {len(results)} entries from CSV: {csv_path}")
            return results

        except FileNotFoundError:
            print(f"Error: CSV file not found: {csv_path}")
            return {}
        except Exception as e:
            print(f"Error reading CSV file {csv_path}: {str(e)}")
            return {}

    @staticmethod
    def _construct_image_data_row(file_uri: str, input_prompt: str, output_text: str) -> str:
        """
        Constructs a single row for the JSONL training dataset in Google's required format.

        Args:
            file_uri (str): Google Cloud Storage URI for the image frame
            input_prompt (str): Input prompt text for the model
            output_text (str): Expected output/analysis response

        Returns:
            str: JSONL row string with user and model roles
        """
        row = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "fileData": {
                                "mimeType": "image/png",
                                "fileUri": file_uri
                            }
                        },
                        {
                            "text": input_prompt
                        }
                    ]
                },
                {
                    "role": "model",
                    "parts": [
                        {
                            "text": output_text
                        }
                    ]
                }
            ]
        }
        data_row = json.dumps(row) + "\n"
        return data_row

    @staticmethod
    def _construct_video_data_row(file_uri: str, input_prompt: str, output_text: str, media_resolution_level: Literal["LOW", "MEDIUM"] = "MEDIUM" ) -> str:
        """
        Constructs a single row for the JSONL training dataset in Google's required format for videos.

        Args:
            file_uri (str): Google Cloud Storage URI for the video file
            input_prompt (str): Input prompt text for the model
            output_text (str): Expected output/analysis response
            media_resolution_level (Literal["LOW", "MEDIUM"]): Media resolution level for the video.
                LOW:
                    Pros: Approximately 4 times faster and more cost-effective tuning.
                    Cons: Lower visual detail, which might be insufficient for tasks requiring fine-grained visual analysis.
                MEDIUM:
                    Pros: Higher visual detail for better performance on visually complex tasks.
                    Cons: Slower and more expensive tuning process.

        Returns:
            str: JSONL row string with user and model roles
        """
        if media_resolution_level not in ["LOW", "MEDIUM"]:
            raise ValueError("media_resolution_level must be either 'LOW' or 'MEDIUM'")
        row = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "fileData": {
                                "mimeType": "video/mp4",
                                "fileUri": file_uri
                            }
                        },
                        {
                            "text": input_prompt
                        }
                    ]
                },
                {
                    "role": "model",
                    "parts": [
                        {
                            "text": output_text
                        }
                    ]
                }
            ],
            "generationConfig": {"mediaResolution": f"MEDIA_RESOLUTION_{media_resolution_level}"}
        }
        data_row = json.dumps(row) + "\n"
        return data_row

    @staticmethod
    def extract_frames_for_all_videos_in_folder(
            every_n_frames: int,
            input_folder_path: str,
            output_folder_path: str,
    ) -> None:
        """
        Extracts frames from all mp4 and avi videos in the input folder.

        Args:
            every_n_frames (int): Number of frames to skip between extractions.
            input_folder_path (str): Path to the folder containing videos.
            output_folder_path (str): Path to the folder where frames will be saved.
        """
        # Get all .mp4 and .avi files in the input folder
        video_files = [
            f for f in os.listdir(input_folder_path)
            if f.lower().endswith(('.mp4', '.avi'))
        ]

        if not video_files:
            print("No video files found in the input folder.")
            return

        for video_file in video_files:
            video_name, _ = os.path.splitext(video_file)
            video_path = os.path.join(input_folder_path, video_file)
            output_subfolder = os.path.join(output_folder_path, video_name)

            print(f"Extracting frames from: {video_file}")
            FineTuner.extract_frames(every_n_frames, video_path, output_subfolder)

    @staticmethod
    def extract_frames(every_n_frames: int, video_path: str, output_folder: str) -> None:
        """
        Legacy method for local file extraction. Kept for backwards compatibility.
        """
        os.makedirs(output_folder, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Cannot open video file: {video_path}")
            return

        frame_idx = 0
        saved_frame_idx = 0
        success, frame = cap.read()

        while success:
            if frame_idx % every_n_frames == 0:
                frame_filename = f"{saved_frame_idx}.png"
                frame_path = os.path.join(output_folder, frame_filename)
                cv2.imwrite(frame_path, frame)
                saved_frame_idx += 1

            frame_idx += 1
            success, frame = cap.read()

        cap.release()
        print(f"Frames extracted for video: {video_path}")

    @staticmethod
    def load_pickle_object(pickle_path: str):
        """
        Load and return a Python object from a pickle file.

        Args:
            pickle_path: Path to the pickle file.

        Returns:
            The object stored in the pickle file.
        """
        with open(pickle_path, 'rb') as f:
            obj = pickle.load(f)
        return obj

    @staticmethod
    def get_video_name_without_extension(video_path_or_uri: str) -> str:
        """
        Extract the video name (without extension) from a file path or URI.

        Args:
            video_path_or_uri (str): The full path or URI of the video file

        Returns:
            str: The video file name without the extension

        Example:
            get_video_name_without_extension("gs://ben_gurion_shop/exit1_20250416231103.mp4")
            # returns "exit1_20250416231103"
        """
        extension = FineTuner.get_video_extension(video_path_or_uri)
        base = os.path.basename(video_path_or_uri)
        if not base.lower().endswith('.' + extension):
            raise ValueError(f"Extension mismatch in: {video_path_or_uri}")
        return base[:-(len(extension) + 1)]

    @staticmethod
    def get_video_extension(video_path_or_uri: str) -> str:
        """
        Extract the video extension from a file path or URI.

        Args:
            video_path_or_uri (str): The full path or URI of the video file

        Returns:
            str: The video extension without the dot (e.g., 'mp4', 'avi')

        Examples:
            get_video_extension('/path/to/video.mp4')
            'mp4'
            get_video_extension('gs://bucket/video.avi')
            'avi'
            get_video_extension('inalid_file')
            raises value error
        """
        extension = os.path.splitext(video_path_or_uri)[1].lower().lstrip('.')
        if not extension:
            raise ValueError(f"Invalid video path in: {video_path_or_uri}")
        return extension

if __name__ == "__main__":
    # FineTuner.make_images_dataset_for_analysis_model(
    #     pickles_folder="/home/yonatan.r/PycharmProjects/Guardify-AI/analysis_results/bengurion-agentic",
    #     frames_bucket="ben-gurion-shop-frames",
    #     input_prompt=enhanced_prompt,
    #     path_prefix_inside_bucket="ben_gurion_frames"
    # )

    FineTuner.make_videos_dataset_for_analysis_model(
        input_prompt=enhanced_prompt,
        csv_path="/home/yonatan.r/Downloads/ben_gurion_data_annotation.csv"
    )
