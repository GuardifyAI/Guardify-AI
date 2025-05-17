from GoogleClient import GoogleClient
import os
from data_science.src.azure.utils import load_env_variables
load_env_variables()
from ShopliftingAnalyzer import ShopliftingAnalyzer
from PipelineManager import PipelineManager

def main():
    # Initialize GoogleClient
    google_client = GoogleClient(
        project=os.getenv("GOOGLE_PROJECT_ID"),
        location=os.getenv("GOOGLE_PROJECT_LOCATION"),
        service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
    )
    shoplifting_analyzer = ShopliftingAnalyzer(detection_strictness=0.5)

    pipeline_manager = PipelineManager(google_client, shoplifting_analyzer)
    pipeline_manager.analyze_all_videos_in_bucket("guardify-videos")

if __name__ == "__main__":
    main()

