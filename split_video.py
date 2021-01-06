import os, sys
import glob
from tqdm import tqdm
from pathlib import Path


def videos_to_imgs(output_path=None,
                   input_path=None,
                   pattern='*.mp4'):
    """Function to split an input video into frames. It saves the frames with
    a naming convention `videoname_f000000_t0000.00.png` where - second term represents 
    the frame number and the third term represents its corresponding time-stamp. This function scales down
    the video to a `250x250` resolution and also saves a `.txt` file containing time-stamps of the extracted
    frames for additional use by the user. User can put multiple videos in a directory under `input_path` and
    the extracted frames for each video will be stored in its own separate directory under `output_path`.

    Args:
        output_path (Path): Absolute path to the directory to store the extracted frames. Defaults to None.
        input_path (Path): Absolute path to the directory which contains the videos to extract frames from. Defaults to None.
        pattern (str, optional): Extension of the video files to extract frames from. Defaults to `*.mp4`.
    """

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

        print(f'Start Writing time-stamps for Video {i+1}')
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
                (key, val) = line.strip().split(',')
                times_dict[val] = f'{float(key):.2f}'
        print(f'End Writing time-stamps for Video {i+1}')

        # Adding time-stamp corresponding to each frame in its name
        frames = list(out_folder.glob('*.png'))
        frames.sort()
        os.chdir(out_folder)
        # Rename loop. 
        for frame in frames:
            try:
                # vidname_f000000_t0000.00.png
                new_name = (file_name + '_f' + format(int(frame.name.split('_')[1].split('.')[0]), '06d') + 
                            '_t' + format(float(times_dict[frame.stem.split("_")[1]]), '07.2f') + '.png') 

                frame.rename(new_name)

            except:
                frame.unlink()
        
        # Print to terminal after completion of extracting each video
        print(f'Done extracting: {i+1}')
        print(f'Number of frames extracted from Video {i+1}: {len(frames)}')


if __name__ == "__main__":
    # Change `output_path` and `input_path` accordingly
    videos_to_imgs(output_path='/home/prabhat/Videos/output',
                    input_path='/home/prabhat/Videos/input', 
                    pattern='*.mp4')