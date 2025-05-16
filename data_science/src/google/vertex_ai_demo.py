from GoogleClient import GoogleClient
import os
from data_science.src.azure.utils import load_env_variables
load_env_variables()
from ShopliftingAnalyzer import ShopliftingAnalyzer

def main():
    # Initialize GoogleClient
    google_client = GoogleClient(
        project=os.getenv("GOOGLE_PROJECT_ID"),
        location=os.getenv("GOOGLE_PROJECT_LOCATION"),
        service_account_json_path=os.getenv("SERVICE_ACCOUNT_FILE")
    )
    shoplifting_analyzer = ShopliftingAnalyzer(detection_strictness=0.5)
    # Get video URIs and names
    uris, names = google_client.get_videos_uris_and_names_from_buckets("guardify-videos")
    
    final_predictions = {}
    for uri, name in zip(uris, names):
        result = shoplifting_analyzer.analyze_video_from_bucket(uri, pickle_analysis=True)


if __name__ == "__main__":
    main()
    # all_videos_analysis = load_pickle_files_from_directory("/home/yonatan.r/PycharmProjects/SurveillanceAI/data_science/src/")
    # final_predictions = {}
    # for video_uri, video_analysis in all_videos_analysis.items():
    #     final_predictions[video_analysis["video_uri"]] = int(determine_shoplifting_likelihood(video_analysis["analysis"]) > 0.5)
    #
    # df = pd.DataFrame(list(final_predictions.values()), index=final_predictions.keys(), columns=['Prediction'])
    # # Export DataFrame to CSV, including the index
    # csv_file_path = 'output.csv'  # Specify your path and filename
    # df.to_csv(csv_file_path, index=True)  # Include index by setting index=True

