import os
import subprocess
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import crop

from rich import print
from rich.panel import Panel
from rich.traceback import install
install(show_locals=True)

def convert_video_aspect_ratio(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop over all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv')):  # Add other formats as needed
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, f"9_16_{filename}")

            # Load the video clip
            clip = VideoFileClip(input_file)

            # Calculate the new size to maintain 9:16 aspect ratio
            if clip.size[0] > clip.size[1]:  # Landscape
                new_width = int(clip.h * 9 / 16)
                new_height = clip.h
            else:  # Portrait
                new_width = clip.w
                new_height = int(clip.w * 9 / 16)

            # Calculate the centering offsets
            x_center_offset = (new_width - clip.w) / 2
            y_center_offset = (new_height - clip.h) / 2

            # Crop the clip to the new size and center it
            cropped_clip = clip.fx(crop, width=new_width, height=new_height, x_center=x_center_offset, y_center=y_center_offset)

            # Save the cropped clip
            cropped_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')

            print(Panel(f"Converted {filename} to aspect ratio 9:16 and saved as {output_file}", border_style="bold green"))


input_folder = "Extracted Segments"
output_folder = "Extracted Segments Formatted"

convert_video_aspect_ratio(input_folder, output_folder)
