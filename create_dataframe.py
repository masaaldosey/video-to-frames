import pandas as pd
import os
from pathlib import Path
from tqdm import tqdm
import numpy as np


def write_pkl(root_dir):
    print("writing_pkl...")
    root_dir = Path(root_dir)
    img_base_path = root_dir / "output"
    csv_path = root_dir / "csv"
    out_path = root_dir
    #print(img_base_path, annot_tool_path, annot_timephase_path, out_path)

    class_labels = [
        "Preparation",
        "Clipping",
        "Dissection",
        "Haemostasis1",
        "Retrieval",
        "Haemostasis2",
        "EndOperation",
    ]

    test_df = pd.DataFrame(columns=[
        "video_idx", "image_path", "time", "class"
    ])
    videos = os.listdir(img_base_path)
    for i in tqdm( range(0, len(videos)) ):
        vid_df = pd.DataFrame()
        img_path_for_vid = img_base_path / f"{videos[i]}"
        img_list = sorted(img_path_for_vid.glob('*.png'))
        img_list = [str(i.relative_to(img_base_path)) for i in img_list]
        vid_df["image_path"] = img_list
        vid_df["video_idx"] = videos[i]
        # add image class
        actual_phases = pd.read_csv(csv_path / f"{videos[i]}.csv")
        phase_times = {}
        phase_times["start_preparation"] = float(actual_phases["start_preparation"])
        phase_times["end_preparation"] = float(actual_phases["end_preparation"])
        for i in range(len(img_list)):
            img_time = float(img_list[i][8:14])
            if img_time >= phase_times["start_preparation"] and img_time <= phase_times["end_preparation"] :

                vid_df.at[i, "time"] = img_time
                vid_df.at[i, "class"] = "Preparation"  
                
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