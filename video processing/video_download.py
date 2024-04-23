from pytube import YouTube
import subprocess
import os

def run_ffmpeg(video_path, audio_path, output_file_path):
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_file_path
    ]
    # Start the ffmpeg process
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Wait for the process to complete
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("ffmpeg failed:", stderr.decode())
        return False
    else:
        print("ffmpeg completed successfully.")
        return True

def download_and_merge_video_audio(youtube_object, output_path):
    video_stream = youtube_object.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()
    audio_stream = youtube_object.streams.filter(only_audio=True, file_extension='mp4').first()

    video_path = video_stream.download(output_path=output_path, filename='video_temp.mp4')
    audio_path = audio_stream.download(output_path=output_path, filename='audio_temp.mp4')

    # Define output file path
    output_file_path = os.path.join(output_path, f"{youtube_object.title}.mp4")
    
    # Merging video and audio with ffmpeg
    if run_ffmpeg(video_path, audio_path, output_file_path):
        # Clean up the temporary files
        os.remove(video_path)
        os.remove(audio_path)
    else:
        print("Error during merging. Check logs for more details.")

def download(link):
    output_path = "Test Videos"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    youtube_object = YouTube(link)
    stream = youtube_object.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    
    if stream:
        try:
            downloaded_file_path = stream.download(output_path=output_path)
            print("Download completed successfully with audio.")
        except Exception as e:
            print(f"An error occurred during downloading: {e}")
    else:
        print("No single file stream available; downloading and merging video and audio.")
        download_and_merge_video_audio(youtube_object, output_path)

link = input("Enter the YouTube video URL: ")
download(link)
