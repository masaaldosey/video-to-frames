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
    # path to save dataframe file
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
    # change naming - phase_start_list
    phase_start_list = [S_P, S_C, S_D, S_H1, S_R, S_H2, E_O]
    # Dictionary where `key:value` = `start_*:end_*`
    # change naming - start_endphase_dict
    start_endphase_dict = {S_P: E_P, S_C: E_C, 
                        S_D: E_D, S_H1: E_H1, 
                        S_R: E_R, S_H2: E_H2}

    # dataframe for all videos of the form `video_id`|`path_to_frame`|`timestamp_of_frame`|`phase_label` 
    test_df = pd.DataFrame(columns=[
        "video_idx", "image_path", "time", "class"])
    
    # list of directories containing the frames of each video
    videos = sorted( [folder for folder in img_base_path.iterdir() if folder.is_dir()] )


    # counter for total number of frames
    total_frames = 0

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
        # creating a dictionary of `key:value` = `phase:time-stamp`
        phase_times = {}
        for col in range(2, len(columns)):
            phase_times[columns[col]] = values[col]
        
        # accounting for delta between phase change
        print(f'\nOriginal phase times:\n{phase_times}\n')
        for phase in phase_start_list:
            if phase == S_P:
                # phase_end = phase_start
                phase_end = start_endphase_dict[phase]
            
            elif phase == E_O:
                phase_times[phase_end] = phase_times[E_O] 

            elif phase_times[phase]:
                # end_lastseen = start_endphase_dict[phase_end]
                delta = (phase_times[phase] - phase_times[phase_end]) / 2
                phase_times[phase] = phase_times[phase] - delta
                phase_times[phase_end] = phase_times[phase_end] + delta
                phase_end = start_endphase_dict[phase]  
        print(f'\nUpdated phase times:\n{phase_times}\n')

        # iterating over frames and fetching timestamps of each
        frame_timestamps = []
        for j in range(len(img_list)):
            img_timestamp = float(img_list[j].split('_t')[1].split('.png')[0])
            frame_timestamps.append(img_timestamp)
        
        # list of img_timestamps and concatenate with vid_df as a column
        vid_df["time"] = frame_timestamps

        # assigning class label to each frame
        vid_df["class"] = None
        # pre-preparation = 0
        vid_df["class"].loc[vid_df["time"] < phase_times[S_P]] = 0
        phase_list = [[S_P, E_P], [S_C, E_C], [S_D, E_D], [S_H1, E_H1], [S_R, E_R], [S_H2, E_H2]]
        # counter of class labels (preparation=1, clipping=2, dissection=3, haemostasis1=4, retrieval=5, haemostasis2=6)
        class_num = 1
        for start, end in phase_list:
            vid_df["class"].loc[(phase_times[start] <= vid_df["time"]) & ( vid_df["time"] < phase_times[end])] = class_num
            class_num += 1
        # assigning extra-frames to last surgical phase
        # assumes all previous frames are assigned to one of the above mentioned phases
        vid_df.loc[vid_df["class"].isna()] = vid_df["class"].max()
        
        # printing video summary to terminal
        print(f'number of frames: {len(vid_df["image_path"])}')
              
        print(
            f"len(img_list): {len(img_list)} - vid_df.shape[0]:{vid_df.shape[0]}"
        )
        test_df = test_df.append(vid_df, ignore_index=True, sort=False)


    # printing entire dataset summary to terminal
    print("DONE")
    print(f'test_df shape: {test_df.shape}')
    print(f'columns of test_df: {test_df.columns}')
    print(f'total number of frames in dataset: {test_df.shape[0]}')
    print(f'frames in each class: \n{test_df.groupby("class").count()["time"]}')
    # test_df.groupby(["class", "video_idx"]).count()
    test_df.to_csv(out_path / "test.csv")
    # test_df.to_pickle(out_path / "MITI_split_250px_25fps.pkl")


if __name__ == "__main__":
    # Formatting to display all columns of the dataframe
    pd.set_option('display.max_columns', None)
    root_dir = "/home/prabhat/Videos"
    write_pkl(root_dir)