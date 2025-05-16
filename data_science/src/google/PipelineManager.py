from GoogleClient import GoogleClient
from ShopliftingAnalyzer import ShopliftingAnalyzer

class PipelineManager:
    def __init__(self, google_client: GoogleClient, shoplifting_analyzer: ShopliftingAnalyzer):
        self.google_client = google_client
        self.shoplifting_analyzer = shoplifting_analyzer

    def analyze_all_videos_in_bucket(self, bucket_name: str):
        # Get video URIs and names
        uris, names = self.google_client.get_videos_uris_and_names_from_buckets(bucket_name)

        final_predictions = {}
        for uri, name in zip(uris, names):
            analysis = self.shoplifting_analyzer.analyze_video_from_bucket(uri, pickle_analysis=True)
            final_predictions[name] = analysis

        return final_predictions