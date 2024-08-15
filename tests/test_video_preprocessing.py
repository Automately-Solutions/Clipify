import os
import nltk
import subprocess
import speech_recognition as sr
from pydub import AudioSegment

from rich.traceback import install
install(show_locals=True)

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

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        transcript = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        transcript = "Google Speech Recognition could not understand audio"
    except sr.RequestError:
        transcript = "Could not request results from Google Speech Recognition service"
    return transcript

def process_transcript(transcript):
    sentences = nltk.sent_tokenize(transcript)
    return sentences

# Example usage
video_url = input("Enter the YouTube video URL: ")
video_file = download_youtube_video(video_url)
audio_file = extract_audio_from_video(video_file)
transcript = transcribe_audio(audio_file)
processed_transcript = process_transcript(transcript)

# Output the processed transcript
for i, sentence in enumerate(processed_transcript):
    print(f"{i+1}: {sentence}")

