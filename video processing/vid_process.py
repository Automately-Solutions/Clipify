from moviepy.editor import VideoFileClip

def convert_aspect_ratio(input_path, output_path):
    # Load the video file
    clip = VideoFileClip(input_path)

    # Calculate new dimensions
    width, height = clip.size
    # Target aspect ratio is 9:16
    new_height = width * 16 // 9
    new_width = height * 9 // 16

    if new_height > height:
        # Crop width to maintain aspect ratio, then resize to make sure no black areas
        new_clip = (clip.crop(x1=(width - new_width) // 2, x2=(width + new_width) // 2)
                    .resize(newsize=(width, new_height)))
    else:
        # Crop height to maintain aspect ratio, then resize
        new_clip = (clip.crop(y1=(height - new_height) // 2, y2=(height + new_height) // 2)
                    .resize(newsize=(new_width, height)))

    # Write the output video file
    new_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

# Example usage
convert_aspect_ratio('input_video.mp4', 'output_video.mp4')
