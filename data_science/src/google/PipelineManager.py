from GoogleClient import GoogleClient
from ShopliftingAnalyzer import ShopliftingAnalyzer
import pandas as pd
import datetime
import os

class PipelineManager:
    MAX_API_CALLS = 2

    def __init__(self, google_client: GoogleClient, shoplifting_analyzer: ShopliftingAnalyzer):
        self.google_client = google_client
        self.shoplifting_analyzer = shoplifting_analyzer

    def analyze_all_videos_in_bucket(self, bucket_name: str, max_api_calls_per_video: int = None, export_results: bool = False):
        """
        Analyze all videos in a specified bucket and optionally export results to CSV.

        Args:
            bucket_name (str): Name of the Google Cloud Storage bucket
            max_api_calls_per_video (int, optional): Maximum number of API calls per video. Defaults to None.
            export_results (bool, optional): Whether to export results to CSV. Defaults to False.

        Returns:
            dict: Dictionary containing analysis results for each video
        """
        max_api_calls_per_video = max_api_calls_per_video or self.MAX_API_CALLS
        # Get video URIs and names
        uris, names = self.google_client.get_videos_uris_and_names_from_buckets(bucket_name)

        final_predictions = {}
        for uri, name in zip(uris, names):
            analysis = self.shoplifting_analyzer.analyze_video_from_bucket(uri,
                                                                           max_api_calls=max_api_calls_per_video,
                                                                           pickle_analysis=True)
            final_predictions[name] = analysis

        if export_results:
            self._export_results(final_predictions)

        return final_predictions

    def _export_results(self, final_predictions: dict, labels_csv_path: str = None) -> str:
        """
        Export analysis results to a CSV file.

        Args:
            final_predictions (dict): Dictionary containing analysis results for each video
            labels_csv_path (str, optional): Path to CSV file containing ground truth labels

        Returns:
            str: Path to the exported CSV file
        """
        # Create DataFrame from results
        results_data = []
        for name, analysis in final_predictions.items():
            results_data.append({
                'video_identifier': analysis['video_identifier'],
                'video_name': name,
                'shoplifting_determination': analysis['shoplifting_determination']
            })

        df = pd.DataFrame(results_data)
        match_percentage = None

        # Try to compare with labels if provided
        if labels_csv_path:
            try:
                labels_df = pd.read_csv(labels_csv_path)
                required_columns = ['video_name', 'shoplifting_determination']
                
                if all(col in labels_df.columns for col in required_columns):
                    # Merge predictions with labels
                    merged_df = pd.merge(
                        df,
                        labels_df[required_columns],
                        on='video_name',
                        how='inner',
                        suffixes=('_predicted', '_actual')
                    )
                    
                    # Add correctness column
                    df['prediction_correct'] = merged_df['shoplifting_determination_actual'] == merged_df['shoplifting_determination_predicted']
                    
                    # Calculate match percentage
                    match_percentage = (df['prediction_correct']).mean() * 100
            except:
                pass

        # Create timestamp for unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"shoplifting_analysis_{timestamp}.csv"

        # Create results directory if it doesn't exist
        results_dir = "analysis_results"
        os.makedirs(results_dir, exist_ok=True)

        # Save to CSV
        csv_path = os.path.join(results_dir, csv_filename)
        
        # Write the main results
        df.to_csv(csv_path, index=False)
        
        # Append match percentage if available
        if match_percentage is not None:
            with open(csv_path, 'a') as f:
                f.write(f"\nOverall match percentage: {match_percentage:.2f}%")

        return csv_path