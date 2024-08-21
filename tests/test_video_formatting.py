import re
from rich.prompt import Prompt
from rich.traceback import install
install(show_locals=True)

from rich import print
from rich.panel import Panel

import os
import subprocess

def convert_video_aspect_ratio(input_path, output_path):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop over each video and convert the aspect ratio to 9:16
    for filename in os.listdir(input_folder):
        if filename.endswith(('.mp4', '.mov')):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_path, f"9_16_{filename}")

            command = f'ffmpeg -i "{input_file}" -vf "scale=ih*9/16:ih, pad=ih*9/16:ih:(ow-iw)/2:(oh-ih)/2" "{output_file}"'
            subprocess.call(command, shell=True)

            print(Panel(f"Converted {filename} to aspect ratio 9:16 and saved as {output_file}", border_style="bold green"))

input_folder = "Extracted Segments"
output_folder = "Extracted Segments Formatted"

convert_video_aspect_ratio(input_folder, output_folder)
