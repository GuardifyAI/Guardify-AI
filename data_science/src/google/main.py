from GoogleClient import GoogleClient
import os
from data_science.src.utils import load_env_variables
load_env_variables()
from ShopliftingAnalyzer import ShopliftingAnalyzer
from data_science.src.google.AnalysisModel import AnalysisModel
from data_science.src.google.ComputerVisionModel import ComputerVisionModel
from PipelineManager import PipelineManager

def main():
    # Initialize GoogleClient
    google_client = GoogleClient(
        project=os.getenv("GOOGLE_PROJECT_ID"),
        location=os.getenv("GOOGLE_PROJECT_LOCATION"),
        service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
    )
    shoplifting_analyzer = ShopliftingAnalyzer(cv_model=ComputerVisionModel(),
                                               analysis_model=AnalysisModel(),
                                               detection_strictness=0.5)

    pipeline_manager = PipelineManager(google_client, shoplifting_analyzer)
    pipeline_manager.analyze_all_videos_in_bucket(os.getenv("BUCKET_NAME"), export_results=True)

if __name__ == "__main__":
    main()

