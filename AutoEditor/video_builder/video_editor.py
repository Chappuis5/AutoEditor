import requests
import os
import uuid
import re
import shutil
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.VideoClip import ColorClip
import numpy as np
from pydub import AudioSegment
from moviepy.editor import concatenate_videoclips, VideoFileClip, AudioFileClip, CompositeAudioClip
from PIL import Image
from math import ceil
class VideoEditor:
    def __init__(self):
        self.tmp_dir = '/tmp/video_selection'
        self.final_dir = 'final_video'
        os.makedirs(self.tmp_dir, exist_ok=True)
        os.makedirs(self.final_dir, exist_ok=True)

    @staticmethod
    def sanitize_filename(filename, max_length=255):
        filename = re.sub(r'[\\/*?:"<>|]', '', filename)  # remove special characters
        filename = filename[:max_length]  # truncate to max length
        return filename

    @staticmethod
    def resize_clip(clip, size):
        frames = [np.array(Image.fromarray(frame).resize(size, Image.LANCZOS)) for frame in clip.iter_frames()]
        return ImageSequenceClip(frames, fps=clip.fps)

    def download_video(self, url, output_path):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as file:
                file.write(response.content)
        else:
            print(f"Failed to download video from {url}")

    def trim_video(self, video_path, start_time, end_time, output_path):
        video = VideoFileClip(video_path)
        trimmed = video.subclip(start_time, end_time)
        trimmed.write_videofile(output_path, codec='libx264')

    def concatenate_videos(self, videos, output_path):
        if not videos:
            return
        clips = [VideoFileClip(video) for video in videos]
        if len(clips) == 1:
            clips[0].write_videofile(output_path, codec='libx264')
            clips[0].close()
            return
        first_clip_size = clips[0].size
        clips = [self.resize_clip(clip, first_clip_size) if clip.size != first_clip_size else clip for clip in clips]
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(output_path, codec='libx264')
        for clip in clips:
            clip.close()
        final_clip.close()

    def trim_and_concatenate(self, liked_videos_by_part, audio_path):
        final_parts_paths = []
        audio_duration = AudioFileClip(audio_path).duration
        print(f"Audio duration: {audio_duration}")
        total_video_duration = 0
        for part, videos in liked_videos_by_part.items():
            part_videos_paths = []
            part_duration = videos[0]['part_duration'] if videos else 0
            video_duration_per_part = part_duration / len(videos)
            video_duration_per_part = ceil(video_duration_per_part * 1000) / 1000  # round up to nearest millisecond
            for video in videos:
                output_path = os.path.join(self.tmp_dir, f"{uuid.uuid4()}.mp4")
                self.download_video(video['url'], output_path)
                video_clip = VideoFileClip(output_path)
                actual_video_duration = video_clip.duration
                print(f"Actual video duration: {actual_video_duration}")
                start_time = 0
                intended_end_time = min(video['duration'], video_duration_per_part)
                end_time = min(intended_end_time, actual_video_duration)
                print(f"Intended video duration: {intended_end_time}, Actual video duration after trimming: {end_time}")
                trimmed_video_clip = video_clip.subclip(start_time, end_time)
                trimmed_output_path = os.path.join(self.tmp_dir, f"{uuid.uuid4()}_trimmed.mp4")
                trimmed_video_clip.write_videofile(trimmed_output_path, codec='libx264')
                total_video_duration += end_time - start_time
                part_videos_paths.append(trimmed_output_path)
            concatenated_output_path = os.path.join(self.tmp_dir, f"{uuid.uuid4()}_concatenated.mp4")
            self.concatenate_videos(part_videos_paths, concatenated_output_path)
            final_parts_paths.append(concatenated_output_path)
        final_video_path = os.path.join(self.tmp_dir, "final.mp4")
        self.concatenate_videos(final_parts_paths, final_video_path)
        print(f"Final video duration: {VideoFileClip(final_video_path).duration}")
        return final_video_path

    def add_audio(self, audio_path, video_path):
        if audio_path.endswith('.m4a'):
            audio = AudioSegment.from_file(audio_path)
            audio_path_wav = os.path.splitext(audio_path)[0] + '.wav'
            audio.export(audio_path_wav, format="wav")
            audio_path = audio_path_wav
        audio = AudioFileClip(audio_path)
        video_clip = VideoFileClip(video_path)
        if video_clip.duration < audio.duration:
            # Calculate remaining time
            remaining_time = audio.duration - video_clip.duration
            # Generate a black clip to fill the remaining time
            black_clip = ColorClip(video_clip.size, col=np.array([0, 0, 0]), duration=remaining_time)
            # Concatenate original video with black clip
            video_clip = concatenate_videoclips([video_clip, black_clip])
            # Print a message indicating that a black screen was added and its length
            print(f"A black screen of {remaining_time} seconds was added at the end of the video.")
        final_clip = video_clip.set_audio(audio)
        output_path = os.path.join(self.final_dir, f'{uuid.uuid4()}_final_video_with_audio.mov')
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        return output_path

    def process_videos(self, liked_videos_by_part, audio_path):
        try:
            video_path = self.trim_and_concatenate(liked_videos_by_part, audio_path)
            final_video_path = self.add_audio(audio_path, video_path)
        except Exception as e:
            print(f"Error occurred while processing videos: {e}")
        finally:
            shutil.rmtree(self.tmp_dir)
            print("Temporary directory deleted.")
        return final_video_path