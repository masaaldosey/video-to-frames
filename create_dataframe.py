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
    start_list = [S_P, S_C, S_D, S_H1, S_R, S_H2]
    end_dictionary = {"start_preparation": E_P, "start_clipping": E_C, 
                        "start_dissection": E_D, "start_haemostasis_1": E_H1, 
                        "start_retrieval": E_R, "start_haemostasis_2": E_H2}

    # dataframe for all videos of the form `video_id`|`path_to_frame`|`timestamp_of_frame`|`phase_label` 
    test_df = pd.DataFrame(columns=[
        "video_idx", "image_path", "time", "class"])
    
    # list of directories containing the frames of each video
    videos = [folder for folder in img_base_path.iterdir() if folder.is_dir()]
    # videos = os.listdir(img_base_path)

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
        vid_df["video_idx"] = int(img_list[0].split('/')[0])

        # reading in `.csv` file containing the time-stamps of different phases for current video
        with open(csv_path / f"{img_list[0].split('/')[0]}.csv", "r") as file:
            columns = file.readline().strip().split(',')
            values = [float(val_str) if val_str else None for val_str in file.readline().split(',')]
        # creating a dictionary of `phase`:`time-stamp`
        phase_times = {}
        for col in range(2, len(columns)):
            phase_times[columns[col]] = values[col]
        
        print(f'\nOriginal phase times:\n{phase_times}\n')
        
        for start_time in start_list:
            if start_time == S_P:
                last_seen = start_time

            elif phase_times[start_time]:
                end_lastseen = end_dictionary[last_seen]
                delta = (phase_times[start_time] - phase_times[end_lastseen]) / 2
                phase_times[start_time] = phase_times[start_time] - delta
                phase_times[end_lastseen] = phase_times[end_lastseen] + delta
                last_seen = start_time      
        
        print(f'\nUpdated phase times:\n{phase_times}\n')

        # iterating over frames
        for j in range(len(img_list)):
            img_timestamp = img_list[j].split(videos[i]+"/"+videos[i]+"_")[1].split(".png")[0]
            vid_df.at[j, "time"] = float(img_timestamp)
            
            # assigning `pre-preparation` frames 
            if (img_timestamp < phase_times[S_P]):
                vid_df.at[j, "class"] = 0
            
            elif phase_times[S_P] <= img_timestamp <= phase_times[E_P]:
                vid_df.at[j, "class"] = 1
            
            elif phase_times[S_C] and (phase_times[S_C] <= img_timestamp <= phase_times[E_C]):
                vid_df.at[j, "class"] = 2
            
            elif phase_times[S_D] and (phase_times[S_D] <= img_timestamp <= phase_times[E_D]):
                vid_df.at[j, "class"] = 3
            
            elif phase_times[S_H1] and (phase_times[S_H1] <= img_timestamp <= phase_times[E_H1]):
                vid_df.at[j, "class"] = 4
            
            elif phase_times[S_R] and (phase_times[S_R] <= img_timestamp <= phase_times[E_R]):
                vid_df.at[j, "class"] = 5
            
            elif phase_times[S_H2] and (phase_times[S_H2] <= img_timestamp <= phase_times[E_H2]):
                vid_df.at[j, "class"] = 6
            
            else:
                vid_df.at[j, "class"] = 7


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