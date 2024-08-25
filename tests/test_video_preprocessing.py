import re
from rich.prompt import Prompt
from rich.traceback import install
install(show_locals=True)

from rich import print
from rich.panel import Panel

import os
import subprocess
import whisper
import nltk
from nltk.tokenize import sent_tokenize

# Ensure NLTK resources are downloaded
nltk.download('punkt')

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

        # Create a new segment if the time gap exceeds the interval
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

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"

def find_important_segments(transcript, max_segments=5, min_segment_length=30):
    # Tokenize transcript into sentences
    sentences = sent_tokenize(transcript)
    
    # Simplistic approach to finding "important" segments
    importance_scores = [(i, len(sentence.split())) for i, sentence in enumerate(sentences)]
    
    # Sort sentences by length as a proxy for importance (longer sentences might be more informative)
    importance_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Select the top `max_segments` sentences as important
    important_indices = sorted([i[0] for i in importance_scores[:max_segments]])
    
    # Group important sentences by proximity in the transcript
    segments = []
    current_segment = [important_indices[0]]
    for idx in important_indices[1:]:
        if idx == current_segment[-1] + 1:
            current_segment.append(idx)
        else:
            segments.append(current_segment)
            current_segment = [idx]
    segments.append(current_segment)
    
    # Get the timestamps and ensure each segment is at least `min_segment_length` seconds long
    important_segments = []
    for segment in segments:
        start_time = segment[0] * 5  # Estimate start time based on position (5 sec per sentence as an example)
        end_time = max((segment[-1] + 1) * 5, start_time + min_segment_length)  # Ensure minimum segment length
        important_segments.append((format_time(start_time), format_time(end_time)))
    
    return important_segments

def convert_time_to_seconds(time_str):
    """
    Converts a time string in the format HH:MM:SS or MM:SS to seconds.
    Handles cases where the time string may not include hours.
    """
    parts = time_str.split(':')
    if len(parts) == 3:  # Includes hours
        h, m, s = map(int, parts)
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:  # Excludes hours
        m, s = map(int, parts)
        return m * 60 + s
    else:
        raise ValueError("Invalid time format. Expected HH:MM:SS or MM:SS.")


def extract_video_segments(video_file, start_time, end_time, output_file):
    """
    Extracts a given segment from the main video by using ffmpeg and the start_time and end_time to give accurate output
    """

    # convert the start_time and end_time to seconds
    start_time_seconds = convert_time_to_seconds(start_time)
    end_time_seconds = convert_time_to_seconds(end_time)

    duration = end_time_seconds - start_time_seconds

    command = f'ffmpeg -i "{video_file}" -ss {start_time_seconds} -to {end_time_seconds} -c copy "{output_file}"'

    print(Panel(f"Executing command : {command}", border_style="bold green"))
    subprocess.run(command, shell=True, check=True)

def preprocessing_input():
    choice = Prompt.ask("Choose your preprocessing input option", choices=["Download a new video", "Transcribe an existing video"])

    if choice == "Download a new video":
        video_url = input("Enter the YouTube video URL: ")
        video_file = download_youtube_video(video_url)
        audio_file = extract_audio_from_video(video_file)
        result = transcribe_audio_with_whisper(audio_file)
        transcript = result['text']
        transcript_groups = split_transcript_by_timestamps(result, interval=45)

        important_segments = find_important_segments(transcript, max_segments=2, min_segment_length=45)

        for group in transcript_groups:
            print(Panel(f"[bold]{group[0]}[/bold]\n\n{''.join(group[1:])}", border_style="bold", title="Transcript"))

        print("\n[bold green]Important Segments:[/bold green]")
        for start_time, end_time in important_segments:
            print(f"Segment: {start_time} - {end_time}")
        for start_time, end_time in important_segments:
            output_file = f"Extracted Segments/Extracted_segment_{start_time}_{end_time}.mp4"
            extract_video_segments(video_file, start_time, end_time, output_file)
            print(Panel(f"Extracted Segment from {start_time}-{end_time} and saved as {output_file}", border_style="bold blue"))


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
        transcript = result['text']
        transcript_groups = split_transcript_by_timestamps(result, interval=30)

        important_segments = find_important_segments(transcript, max_segments=2, min_segment_length=30)

        for group in transcript_groups:
            print(Panel(f"[bold]{group[0]}[/bold]\n\n{''.join(group[1:])}", border_style="bold", title="Transcript"))

        print("\n[bold green]Important Segments:[/bold green]")
        for start_time, end_time in important_segments:
            print(f"Segment: {start_time} - {end_time}")
        for start_time, end_time in important_segments:
            output_file = f"Extracted_segment_{start_time}_{end_time}.mp4"
            extract_video_segments(video_file, start_time, end_time, output_file)
            print(Panel(f"Extracted Segment from {start_time}-{end_time} and saved as {output_file}", border_style="bold blue"))

preprocessing_input()
