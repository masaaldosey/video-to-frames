import pandas as pd
import os
import csv
from pathlib import Path
from tqdm import tqdm
import numpy as np


def write_pkl(root_dir):
    print("Writing .csv files...")
    # root path
    root_dir = Path(root_dir)
    # path containing frames for each video
    img_base_path = root_dir / "output"
    # path containing phase time-stamps for each video
    csv_path = root_dir / "csv"
    # path to save `.csv` files
    out_path = root_dir

    # tokens for column names in `.csv` files 
    S_P = "start_preparation"
    E_P = "end_preparation"
    S_C = "start_clipping"
    E_C = "end_clipping"
    S_D = "start_dissection"
    E_D = "end_dissection"
    S_H1 = "start_haemostasis_1"
    E_H1 = "end_haemostasis_1"
    S_R = "start_retrieval"
    E_R = "end_retrieval"
    S_H2 = "start_haemostasis_2"
    E_H2 = "end_haemostasis_2"
    E_O = "end_operation"

    # dataframe for all videos of the form `video_id`|`path_to_frame`|`timestamp_of_frame`|`phase_label` 
    test_df = pd.DataFrame(columns=[
        "video_idx", "image_path", "time", "class"])
    # list of directories containing the frames of each video
    videos = os.listdir(img_base_path)

    # iterating over each video directory
    for i in tqdm( range(0, len(videos)) ):
        # temporary dataframe for current video
        vid_df = pd.DataFrame()
        # path to frames of current video 
        img_path_for_vid = img_base_path / f"{videos[i]}"
        # list of frames of current video
        img_list = sorted(img_path_for_vid.glob('*.png'))
        # extracting relative path for frames and converting it to `str`
        img_list = [str(i.relative_to(img_base_path)) for i in img_list]
        # update the frame paths in `vid_df`
        vid_df["image_path"] = img_list
        # update the video id in `vid_df`
        vid_df["video_idx"] = videos[i]

        # reading in `.csv` file containing the time-stamps of different phases for current video
        with open(csv_path / f"{videos[i]}.csv", "r") as file:
            columns = file.readline().split(',')
            values = [float(val_str) if val_str else None for val_str in file.readline().split(',')]
        # creating a dictionary of `phase`:`time-stamp`
        phase_times = {}
        for col in range(2, len(columns)):
            phase_times[columns[col]] = values[col]
        
        # accounting for delta between phases
        # `end_preparation` and `start_clipping`
        phase_times[E_P] = phase_times[E_P] + 
                            ( (phase_times[S_C] - phase_times[E_P]) / 2) )
        phase_times[S_C] = phase_times[S_C] - 
                            ( (phase_times[S_C] - phase_times[E_P]) / 2 )
        # `end_clipping` and `start_dissection`
        
        for j in range(len(img_list)):
            img_timestamp = img_list[j].split(videos[i]+"/"+videos[i]+"_")[1].split(".png")[0]
            vid_df.at[j, "time"] = float(img_timestamp)
            
            # Dropping frames before `start_preparation` and after `end_operation` 
            if ( (phase_times[S_P] is not None) and (img_timestamp < phase_times[S_O]) ) or ( (phase_times[E_O] is not None) and (img_timestamp > phase_times[E_O]) ) :
                vid_df.drop(j, inplace=True)
        

        print(f'number of frames: {len(vid_df["image_path"])}')
              
        print(
            f"len(img_list): {len(img_list)} - vid_df.shape[0]:{vid_df.shape[0]}"
        )
        test_df = test_df.append(vid_df, ignore_index=True, sort=False)

    print("DONE")
    print(test_df.shape)
    print(test_df.columns)
    test_df.to_csv(out_path / "test.csv")


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    root_dir = "/home/prabhat/Videos"
    write_pkl(root_dir)