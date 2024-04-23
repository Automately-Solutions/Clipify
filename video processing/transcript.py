import subprocess
import speech_recognition as sr

def transcribe_video_with_grouped_timestamps(video_path, output_text_path='grouped_transcript.txt', duration_threshold=20):
    """Converts a video file to a grouped transcript file with fewer timestamps."""
    # Extract audio from video
    audio_path = 'temp_audio.wav'
    command = f'ffmpeg -i "{video_path}" -ab 160k -ar 44100 -vn {audio_path}'
    subprocess.call(command, shell=True)

    # Use speech recognition to transcribe the audio file
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)  # read the entire audio file

    try:
        # Recognize speech using Sphinx with detailed result
        decoder = recognizer.recognize_sphinx(audio, show_all=True)
        if decoder:
            process_grouped_transcript(decoder, output_text_path, duration_threshold)
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))

def process_grouped_transcript(decoder, output_path, duration_threshold):
    """Processes the decoder object, extracting transcripts with grouped timestamps."""
    with open(output_path, 'w') as file:
        # Variables to accumulate text and manage timestamps
        accumulated_text = ''
        last_timestamp = 0

        for segment in decoder.seg():
            start_time = segment.start_frame / 100
            end_time = segment.end_frame / 100
            word = segment.word
            if start_time - last_timestamp > duration_threshold:
                if accumulated_text:
                    file.write(f"{format_time(last_timestamp)}    {accumulated_text.strip()}\n")
                accumulated_text = ''
                last_timestamp = start_time
            accumulated_text += word + ' '

        # Write remaining text if any
        if accumulated_text:
            file.write(f"{format_time(last_timestamp)}    {accumulated_text.strip()}\n")
        print("Grouped transcription with timestamps has been saved to", output_path)

def format_time(seconds):
    """Formats seconds to a string in mm:ss format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

# Example usage
video_path = input("Enter the path to your video file: ")
transcribe_video_with_grouped_timestamps(video_path)
