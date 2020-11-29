import pandas as pd
import os
import csv
from pathlib import Path
from tqdm import tqdm
import numpy as np


def sort_bytime(fname):
    """Function to sort the frames by time-stamp

    :param fname: relative path of the frame
    :return: time-stamp of the frame
    """
    return(fname.split('_')[2].split('.png')[0])


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
    # List of start times of various phases except `start_preparation`
    start_times = [S_P, S_C, S_D, S_H1, S_R, S_H2]
    # Dictionary where `key:value` = `start_*:end_*`
    end_times = {"start_preparation": E_P, "start_clipping": E_C, 
                        "start_dissection": E_D, "start_haemostasis_1": E_H1, 
                        "start_retrieval": E_R, "start_haemostasis_2": E_H2}

    # dataframe for all videos of the form `video_id`|`path_to_frame`|`timestamp_of_frame`|`phase_label` 
    test_df = pd.DataFrame(columns=[
        "video_idx", "image_path", "time", "class"])
    
    # list of directories containing the frames of each video
    videos = [folder for folder in img_base_path.iterdir() if folder.is_dir()]

    # iterating over each video directory
    for i in tqdm( range(0, len(videos)) ):
        # temporary dataframe for current video
        vid_df = pd.DataFrame()
        # path to frames of current video 
        img_path_for_vid = img_base_path / f"{videos[i]}"
        # list of frames of current video
        img_list = img_path_for_vid.glob('*.png')
        # extracting relative path for frames and converting it to `str`
        img_list = [str(i.relative_to(img_base_path)) for i in img_list]
        # sorting the frames by their time-stamp
        img_list = sorted(img_list, key=sort_bytime)
      
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

        for start_time in start_times:
            if start_time == S_P:
                # last_seen = start_time
                last_seen = end_times[start_time]

            elif phase_times[start_time]:
                # end_lastseen = end_times[last_seen]
                delta = (phase_times[start_time] - phase_times[last_seen]) / 2
                phase_times[start_time] = phase_times[start_time] - delta
                phase_times[last_seen] = phase_times[last_seen] + delta
                last_seen = end_times[start_time]      
        
        print(f'\nUpdated phase times:\n{phase_times}\n')

        # iterating over frames
        for j in range(len(img_list)):
            img_timestamp = float(img_list[j].split('_')[2].split('.png')[0])
            vid_df.at[j, "time"] = img_timestamp
            
            # `pre-preparation = 0` frames 
            if (img_timestamp < phase_times[S_P]):
                vid_df.at[j, "class"] = 0
            # `preparation = 1` frames
            elif phase_times[S_P] <= img_timestamp <= phase_times[E_P]:
                vid_df.at[j, "class"] = 1
            # `clipping = 2` frames
            elif phase_times[S_C] and (phase_times[S_C] <= img_timestamp <= phase_times[E_C]):
                vid_df.at[j, "class"] = 2
            # `dissection = 3` frames
            elif phase_times[S_D] and (phase_times[S_D] <= img_timestamp <= phase_times[E_D]):
                vid_df.at[j, "class"] = 3
            # `haemostasis_1 = 4` frames
            elif phase_times[S_H1] and (phase_times[S_H1] <= img_timestamp <= phase_times[E_H1]):
                vid_df.at[j, "class"] = 4
            # `retrieval = 5` frames
            elif phase_times[S_R] and (phase_times[S_R] <= img_timestamp <= phase_times[E_R]):
                vid_df.at[j, "class"] = 5
            # `haemostasis_2 = 6` frames
            elif phase_times[S_H2] and (phase_times[S_H2] <= img_timestamp <= phase_times[E_H2]):
                vid_df.at[j, "class"] = 6
            # `end_operation = 7` frames
            else:
                vid_df.at[j, "class"] = 7

        # printing #frames and
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
    # Formatting to display all columns of the dataframe
    pd.set_option('display.max_columns', None)
    root_dir = "/home/prabhat/Videos"
    write_pkl(root_dir)