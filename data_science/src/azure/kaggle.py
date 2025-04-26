from data_science.src.azure.extract_frames import FrameExtractor
from data_science.src.azure.analyze_shoplifting import ShopliftingAnalyzer
import pickle
import pandas as pd

def exctract_kaggle_frames(n):
    FrameExtractor(every_n_frames=n).process_directory("/home/yonatan.r/Desktop/CS/final_project/DCSASS Dataset/Shoplifting/Shoplifting001_x264.mp4/", f"/home/yonatan.r/Desktop/CS/final_project/kaggle_frames_{n}")


def generate_kaggle_results():
    analyzer = ShopliftingAnalyzer()
    kaggle_results = analyzer.analyze_all_videos("/home/yonatan.r/Desktop/CS/final_project/kaggle_frames_8")

    # Pickle the dictionary and save it to a file
    with open('kaggle_results_8_frames.pkl', 'wb') as f:
        pickle.dump(kaggle_results, f)

def validate_results():
    # Load dictionary from pickle file
    with open('kaggle_results_8_frames.pkl', 'rb') as f:
        video_dict = pickle.load(f)

    # Load CSV file
    data = pd.read_csv('/home/yonatan.r/Desktop/CS/final_project/Shoplifting.csv')

    # Filter CSV data to include only rows with video names present in the pickle dictionary
    data_filtered = data[data.iloc[:, 0].isin(video_dict.keys())]

    # Convert filtered CSV data to dictionary for quick lookup
    csv_label_dict = dict(zip(data_filtered.iloc[:, 0], data_filtered.iloc[:, 2]))

    # Initialize counters
    correct_yes = []
    correct_no = []
    false_positive = []
    false_negative = []

    # Evaluate scenarios
    for video, result in video_dict.items():
        prediction = result.get('conclusion')
        actual = csv_label_dict.get(video)

        if prediction == "Yes" and actual == 1:
            correct_yes.append(video)
        elif prediction == "No" and actual == 0:
            correct_no.append(video)
        elif prediction == "Yes" and actual == 0:
            false_positive.append(video)
        elif prediction == "No" and actual == 1:
            false_negative.append(video)

    # Display results
    print(f"Correct (Yes & 1): {len(correct_yes)}")
    print("Videos:", correct_yes)

    print(f"Correct (No & 0): {len(correct_no)}")
    print("Videos:", correct_no)

    print(f"False Positives (Yes & 0): {len(false_positive)}")
    print("Videos:", false_positive)

    print(f"False Negatives (No & 1): {len(false_negative)}")
    print("Videos:", false_negative)

if __name__ == "__main__":
    validate_results()