import os, sys
import glob
import decimal
from tqdm import tqdm
from pathlib import Path


def videos_to_imgs(output_path=None,
                   input_path=None,
                   pattern="*.mp4"):

    output_path = Path(output_path)
    input_path = Path(input_path)

    # Getting all the videos present at the input path
    videos = list(input_path.glob(pattern))
    # Sorting the videos by their name
    videos.sort()
    # Make a separate directory to store outputs
    output_path.mkdir(exist_ok=True)

    for i, video_path in enumerate(tqdm(videos)):
        # Extracting the filename for a video without the suffix
        file_name = video_path.stem
        # Make a separate folder to store frames of each video s
        out_folder = output_path / file_name
        out_folder.mkdir(exist_ok=True)

        # Writing time-stamps of each frame to `.txt` file
        os.system(
            f'ffprobe {video_path} -select_streams v -show_entries frame=coded_picture_number,pkt_pts_time -of csv=p=0:nk=1 -v 0 > {out_folder/file_name}.txt'
        )
        # Extracting frames from each video in PNG format 
        os.system(
            f'ffmpeg -i {video_path} -vf "scale=250:250" -start_number 0 {out_folder/file_name}_%d.png'
        )

        # Reading in the time-stamps `.txt` file and creating a dictionary {frame_number : time-stamp}
        times_dict = {}
        with open(f'{out_folder/file_name}.txt') as file:
            for line in file:
                (key, val) = line.strip().split(",")
                times_dict[val] = key
        
        # Adding time-stamp corresponding to each frame in its name
        frames = list(out_folder.glob("*.png"))
        frames.sort()
        os.chdir(out_folder)
        # Renaming loop
        for frame in frames:
            try:
                os.rename( frame.name, file_name+'_'+f'{times_dict[frame.stem.split("_")[1]]}'+'.png' )
            except:
                os.remove(frame.name)
        # Print to terminal after completion of extracting each video
        print("Done extracting: {}".format(i + 1))


if __name__ == "__main__":
    videos_to_imgs(output_path="/home/prabhat/Videos/output",
                    input_path="/home/prabhat/Videos/input", 
                    pattern="*.mp4")