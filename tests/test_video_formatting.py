import cv2
import os
from mtcnn import MTCNN
import numpy as np
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import crop

from rich import print
from rich.panel import Panel

def detect_face(frame):
    detector = MTCNN()
    faces = detector.detect_faces(frame)
    if len(faces) > 0:
        x, y, width, height = faces[0]['box']
        return x, y, width, height
    return None

def convert_video_aspect_ratio_with_face_detection(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv')):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, f"9_16_{filename}")

            clip = VideoFileClip(input_file)
            if clip.size[0] > clip.size[1]:  # Landscape
                new_width = int(clip.h * 9 / 16)
                new_height = clip.h
            else:  # Portrait
                new_width = clip.w
                new_height = int(clip.w * 9 / 16)

            # Correctly access the first frame
            first_frame = next(iter(clip.iter_frames()))

            # Detect face in the first frame
            face_box = detect_face(first_frame)
            if face_box:
                x, y, width, height = face_box
                # Adjust cropping to center the face
                x_center_offset = (new_width - clip.w) / 2 + (width - x) / 2
                y_center_offset = (new_height - clip.h) / 2 + (height - y) / 2
            else:
                x_center_offset = (new_width - clip.w) / 2
                y_center_offset = (new_height - clip.h) / 2

            cropped_clip = clip.fx(crop, width=new_width, height=new_height, x_center=x_center_offset, y_center=y_center_offset)
            cropped_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')

            print(Panel(f"Converted {filename} to aspect ratio 9:16 and saved as {output_file}", border_style="bold green"))

input_folder = "Extracted Segments"
output_folder = "Extracted Segments Formatted"

convert_video_aspect_ratio_with_face_detection(input_folder, output_folder)
