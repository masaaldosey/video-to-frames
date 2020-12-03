import os, sys
import glob
from tqdm import tqdm
from pathlib import Path

def rename_frames(img_base_dir=None):
    
    # path containing directories (of split frames) for each video
    imgs_base_path = Path(img_base_dir)

    # list of directories containing the frames of each video
    videos = sorted( [folder for folder in imgs_base_path.iterdir() if folder.is_dir()] )

    # iterating over each video directory
    for i in tqdm( range(0, len(videos)) ):
        
        # path to frames of current video 
        img_path_for_vid = imgs_base_path / f"{videos[i]}"
        
        # list of frames of current video
        img_list = sorted( list(img_path_for_vid.glob('*.png')) )
        os.chdir(img_path_for_vid)

        for frame in img_list:
            try:
                new_name = img_path_for_vid.stem + '_f' + format(int(frame.name.split('_f')[1].split('_')[0]), '06d') \
                             + '_t' + format(float(frame.stem.split("_t")[1]), '07.2f') + '.png'
                
                frame.rename(new_name)
            
            except:
                frame.unlink()




if __name__ == "__main__":
    rename_frames(img_base_dir="/home/prabhat/Videos/output")