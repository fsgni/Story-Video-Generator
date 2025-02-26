import subprocess
from pathlib import Path

def add_subtitles(video_file: str, srt_file: str, output_file: str):
    """为视频添加字幕"""
    subprocess.run([
        'ffmpeg', '-y',
        '-i', video_file,
        '-vf', f'subtitles={srt_file}:force_style=\'FontName=Yu Gothic,FontSize=20,PrimaryColour=&HFFFFFF&,Outline=1,Shadow=1,BorderStyle=3,MarginV=30\'',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'copy',
        output_file
    ])

if __name__ == "__main__":
    # 输入视频
    video_file = "output/お菓子の森の秘密星に願いを込めてなど_audio.mp4"
    # 字幕文件
    srt_file = "output/お菓子の森の秘密星に願いを込めてなど.srt"
    # 输出文件
    output_file = "output/お菓子の森の秘密星に願いを込めてなど_final.mp4"
    
    add_subtitles(video_file, srt_file, output_file) 