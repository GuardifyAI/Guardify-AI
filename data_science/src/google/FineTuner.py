import data_science.src.utils as utils
from typing import Tuple, Dict
import os
import json
from data_science.src.google.GoogleClient import GoogleClient
utils.load_env_variables()

class FineTuner:
    google_client = GoogleClient(
        project=os.getenv("GOOGLE_PROJECT_ID"),
        location=os.getenv("GOOGLE_PROJECT_LOCATION"),
        service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
    )

    @staticmethod
    def extract_frames_for_all_videos_in_folder(
            every_n_frames: int,
            input_folder_path: str,
            output_folder_path: str) -> None:
        return utils.extract_frames_for_all_videos_in_folder(every_n_frames, input_folder_path, output_folder_path)

    @staticmethod
    def extract_unified_response_from_pickle(pickle_path: str) -> Tuple[str, str]:
        obj = utils.load_pickle_object(pickle_path)
        # return the response of the first iteration
        return obj['video_identifier'], obj['iteration_results'][0]['full_response']

    @staticmethod
    def extract_analysis_response_from_pickle(pickle_path: str) -> Tuple[str, str]:
        obj = utils.load_pickle_object(pickle_path)
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
                    file_uri = f"gs://{frames_bucket}/{path}/{video_name}/{i}.png"
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

FineTuner.add_analysis_responses_to_jsonl(jsonl_path="/home/yonatan.r/PycharmProjects/Guardify-AI/data_science/src/google/tuning_jsons/ben_gurion_data.jsonl",
                                          pickles_folder="/home/yonatan.r/PycharmProjects/Guardify-AI/analysis_results/bengurion-agentic",
                                          frames_bucket="ben_gurion_shop_frames")
