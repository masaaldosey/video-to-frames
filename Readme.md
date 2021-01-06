# Video-to-Frames

Simple python script to extract and store individual frames of a given video. If you have multiple videos for frame extraction, store them under a common `source directory` and then run the script as is. 

The extracted frames will be stored under a separate `output directory`. In case of multiple videos, the script creates a separate folder for each video in the `output directory`.

## Setup
1. Clone the repository using `git`.
2. Install `ffmpeg` on your system by running the following command:

    ```bash
    sudo apt-get update && install ffmpeg
    ```

## Usage
Change the following under `main` in `split_video.py`:
1. `output_path`: path to store extracted frames of each video,
2. `input_path`: path containing the videos to extract frames from,
2. `pattern`: extension of the video files - `.mp4`, `.mkv` etc. 

---

<br>

## TO DO
- In case of multiple video extraction, add a boilerplate which enables creation of a dataframe containing details of extracted frames.

