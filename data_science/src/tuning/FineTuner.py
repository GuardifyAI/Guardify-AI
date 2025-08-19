import utils.env_utils as env_utils
from typing import Tuple, Dict
import os
import json
from google_client.google_client import GoogleClient
env_utils.load_env_variables()
import pickle

class FineTuner:
    google_client = GoogleClient(
        project=os.getenv("GOOGLE_PROJECT_ID"),
        location=os.getenv("GOOGLE_PROJECT_LOCATION"),
        service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
    )

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
    def extract_analysis_response_from_all_pickles_in_folder(folder_path: str) -> Dict:
        """
        Extracts analysis responses from all pickle files in the specified folder.

        Args:
            folder_path (str): Path to the folder containing pickle files.

        Returns:
            Dict: Dict containing video identifier and analysis response.
        """
        results = dict()
        for filename in os.listdir(folder_path):
            if filename.endswith('.pkl'):
                full_path = os.path.join(folder_path, filename)
                video_identifier, analysis_response = FineTuner.extract_analysis_response_from_pickle(full_path)
                results[video_identifier] = analysis_response
        return results

    @staticmethod
    def add_analysis_responses_to_jsonl(jsonl_path: str, pickles_folder: str, frames_bucket: str):
        """
        For each analysis response in the pickles folder, appends a formatted row to the jsonl file.

        Args:
            jsonl_path: Path to the .jsonl file.
            pickles_folder: Path to the folder containing analysis pickles.
            frames_bucket: Name of the frames bucket.
        """
        # Get {video_identifier: analysis_response} dict
        results = FineTuner.extract_analysis_response_from_all_pickles_in_folder(pickles_folder)
        some_text_variable = "stam"

        with open(jsonl_path, "a") as f:
            for video_identifier, analysis_response in results.items():
                video_name = utils.get_video_name_without_extension(video_identifier)
                path = f"ben_gurion_frames/{video_name}"
                num_frames = FineTuner.google_client.num_of_files_in_bucket_path(frames_bucket, path)
                for i in range(num_frames):
                    # Construct file URI for the frame
                    file_uri = f"gs://{frames_bucket}/{path}/{i}.png"
                    data_row = FineTuner._construct_data_row(file_uri=file_uri,
                                                             input_text=some_text_variable,
                                                             output_text=analysis_response.replace('\n', ''))
                    f.write(data_row)

    @staticmethod
    def _construct_data_row(file_uri: str, input_text: str, output_text: str) -> str:
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
                            "text": input_text
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
            extract_frames(every_n_frames, video_path, output_subfolder)

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

FineTuner.add_analysis_responses_to_jsonl(jsonl_path="/home/yonatan.r/PycharmProjects/Guardify-AI/data_science/src/google/tuning_jsons/ben_gurion_new_data.jsonl",
                                          pickles_folder="/home/yonatan.r/PycharmProjects/Guardify-AI/analysis_results/bengurion-agentic",
                                          frames_bucket="ben-gurion-shop-frames")
