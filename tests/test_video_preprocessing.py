import re
from rich.prompt import Prompt
from rich.traceback import install
install(show_locals=True)

from rich import box
from rich import print
from rich.panel import Panel

import os
import subprocess
import whisper

def download_youtube_video(url, output_path='Test Videos'):
    import yt_dlp
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_file = ydl.prepare_filename(info_dict)
    return video_file

def extract_audio_from_video(video_file):
    # Name the audio file based on the video file name and properly escape it
    base_name = os.path.splitext(os.path.basename(video_file))[0]
    audio_file = f"{base_name}.wav"
    escaped_video_file = video_file.replace('"', '\\"')
    escaped_audio_file = audio_file.replace('"', '\\"')
    command = f'ffmpeg -i "{escaped_video_file}" -ab 160k -ac 2 -ar 44100 -vn "{escaped_audio_file}"'
    subprocess.call(command, shell=True)
    return audio_file

def transcribe_audio_with_whisper(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file, word_timestamps=True)
    return result

def split_transcript_by_timestamps(result, interval=60):
    segments = []
    current_segment = []
    last_time = 0

    for segment in result['segments']:
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text']

        if start_time - last_time > interval:
            if current_segment:
                segments.append(current_segment)
            current_segment = [f"{start_time:.2f} - {end_time:.2f}", text]
        else:
            current_segment.append(text)

        last_time = end_time

    if current_segment:
        segments.append(current_segment)

    return segments

def preprocessing_input():
    choice = Prompt.ask("Choose your preprocessing input option", choices=["Download a new video", "Transcribe an existing video"])

    if choice == "Download a new video":
        video_url = input("Enter the YouTube video URL: ")
        video_file = download_youtube_video(video_url)
        audio_file = extract_audio_from_video(video_file)
        result = transcribe_audio_with_whisper(audio_file)
        transcript_groups = split_transcript_by_timestamps(result, interval=30)  # More granular by setting smaller intervals

        for group in transcript_groups:
            print(Panel(f"[bold]{group[0]}[/bold]\n\n{''.join(group[1:])}", border_style="bold", title="Transcript"))

    elif choice == "Transcribe an existing video":
        video_files = os.listdir('Test Videos')
        if not video_files:
            print("No video files found in 'Test Videos' directory.")
            return
        for i, file in enumerate(video_files):
            print(f"{i+1}. {file}")
        file_index = int(input("Choose a video file to transcribe: ")) - 1
        video_file = os.path.join('Test Videos', video_files[file_index])
        audio_file = extract_audio_from_video(video_file)
        result = transcribe_audio_with_whisper(audio_file)
        transcript_groups = split_transcript_by_timestamps(result, interval=30)  # More granular by setting smaller intervals

        for group in transcript_groups:
            print(Panel(f"[bold]{group[0]}[/bold]\n\n{''.join(group[1:])}", border_style="bold", title="Transcript"))

preprocessing_input()



