from GoogleClient import GoogleClient
from ShopliftingAnalyzer import ShopliftingAnalyzer
import pandas as pd
import datetime
import os

class PipelineManager:
    def __init__(self, google_client: GoogleClient, shoplifting_analyzer: ShopliftingAnalyzer):
        self.google_client = google_client
        self.shoplifting_analyzer = shoplifting_analyzer

    def analyze_all_videos_in_bucket(self, bucket_name: str, export_results: bool = False):
        """
        Analyze all videos in a specified bucket and optionally export results to CSV.

        Args:
            bucket_name (str): Name of the Google Cloud Storage bucket
            export_results (bool, optional): Whether to export results to CSV. Defaults to False.

        Returns:
            dict: Dictionary containing analysis results for each video
        """
        # Get video URIs and names
        uris, names = self.google_client.get_videos_uris_and_names_from_buckets(bucket_name)

        final_predictions = {}
        for uri, name in zip(uris, names):
            analysis = self.shoplifting_analyzer.analyze_video_from_bucket(uri,
                                                                           max_api_calls=2,
                                                                           pickle_analysis=True)
            final_predictions[name] = analysis

        if export_results:
            self._export_results(final_predictions)

        return final_predictions

    def _export_results(self, final_predictions: dict) -> str:
        """
        Export analysis results to a CSV file.

        Args:
            final_predictions (dict): Dictionary containing analysis results for each video

        Returns:
            str: Path to the exported CSV file
        """
        # Create DataFrame from results
        results_data = []
        for name, analysis in final_predictions.items():
            results_data.append({
                'video_uri': analysis['video_identifier'],
                'video_name': name,
                'shoplifting_determination': analysis['shoplifting_determination']
            })

        df = pd.DataFrame(results_data)

        # Create timestamp for unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"shoplifting_analysis_{timestamp}.csv"

        # Create results directory if it doesn't exist
        results_dir = "analysis_results"
        os.makedirs(results_dir, exist_ok=True)

        # Save to CSV
        csv_path = os.path.join(results_dir, csv_filename)
        df.to_csv(csv_path, index=False)

        return csv_path