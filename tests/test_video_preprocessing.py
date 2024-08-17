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
    audio_file = "extracted_audio.wav"
    command = f"ffmpeg -i \"{video_file}\" -ab 160k -ac 2 -ar 44100 -vn {audio_file}"
    subprocess.call(command, shell=True)
    return audio_file

def transcribe_audio_with_whisper(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result["text"]

def preprocessing_input():
    choice = Prompt.ask("Choose your preprocessing input option", choices=["Download a new video", "Transcribe an existing video"])

    if choice == "Download a new video":
        video_url = input("Enter the YouTube video URL: ")
        video_file = download_youtube_video(video_url)
        audio_file = extract_audio_from_video(video_file)
        transcript = transcribe_audio_with_whisper(audio_file)

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
        transcript = transcribe_audio_with_whisper(audio_file)

        with open("transcript.txt", "w") as file:
            file.write(transcript)
        print(Panel("Saved Transcript ✅", border_style="bold green"))

    print(Panel(f"{transcript}", border_style="bold", title="Transcript"))


preprocessing_input()


