from AutoEditor.video_builder.video_editor import VideoEditor
import json

video_editor = VideoEditor()  # Vous devez créer une instance de la classe

json_file = "../debug_directory/liked_videos.json"
audio_path = "/Users/evanflament/Desktop/data/audio.m4a"

# Pour lire le fichier json, vous devriez utiliser 'r' (read) et non 'w' (write)
with open(json_file, 'r') as f:
    liked_videos_by_part = json.load(f)

video_editor.process_videos(liked_videos_by_part, audio_path)
