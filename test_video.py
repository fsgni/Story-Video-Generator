import os
import json
import subprocess
from pathlib import Path
from video_maker import create_base_video
from video_maker_moviepy import create_video_with_scenes_moviepy
from add_subtitles import add_subtitles

# 输入文件名
input_file = "input_texts/豚.txt"
input_stem = Path(input_file).stem

# 音频信息文件
audio_info_file = f"output/audio/{input_stem}_audio_info.json"

# 创建基础视频 - 使用 FFmpeg
base_video = "output/base_video.mp4"
create_base_video(audio_info_file, base_video)

# 创建带场景的视频 - 使用 MoviePy
final_video = "output/final_video_moviepy.mp4"
create_video_with_scenes_moviepy("output/key_scenes.json", base_video, final_video)

# 添加字幕
srt_file = f"output/{input_stem}.srt"
output_video = f"output/{input_stem}_final.mp4"
add_subtitles(final_video, srt_file, output_video)

print(f"处理完成！最终视频: {output_video}")
