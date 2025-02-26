import json
from pathlib import Path
import subprocess
import os

def create_audio_video(audio_info_file: str, output_file: str, resolution=(1920, 1080)):
    """使用 FFmpeg 创建带音频的视频（不含字幕）"""
    # 读取音频信息
    with open(audio_info_file, 'r', encoding='utf-8') as f:
        info = json.load(f)
    
    # 创建临时文件目录
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # 1. 首先创建黑色背景视频
    width, height = resolution
    duration = info['total_duration']
    
    background_video = temp_dir / "background.mp4"
    subprocess.run([
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f'color=c=black:s={width}x{height}:d={duration}',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        str(background_video)
    ])
    
    # 2. 合并所有音频文件
    audio_path = Path(audio_info_file).parent
    concat_file = temp_dir / "concat.txt"
    
    # 创建音频文件列表
    with open(concat_file, 'w', encoding='utf-8') as f:
        for audio_info in info['audio_files']:
            audio_file = audio_path / audio_info['audio_file']
            f.write(f"file '{audio_file.absolute()}'\n")
    
    merged_audio = temp_dir / "merged.wav"
    subprocess.run([
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',
        str(merged_audio)
    ])
    
    # 3. 合成最终视频
    subprocess.run([
        'ffmpeg', '-y',
        '-i', str(background_video),
        '-i', str(merged_audio),
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        str(output_file)
    ])
    
    # 清理临时文件
    if temp_dir.exists():
        for file in temp_dir.glob("*"):
            file.unlink()
        temp_dir.rmdir()

def format_srt_time(seconds: float) -> str:
    """将秒数转换为 SRT 时间格式 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

if __name__ == "__main__":
    # 音频信息文件路径
    audio_info_file = "output/audio/お菓子の森の秘密星に願いを込めてなど_audio_info.json"
    # 输出视频文件路径
    output_file = "output/お菓子の森の秘密星に願いを込めてなど_audio.mp4"
    
    # 确保输出目录存在
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    create_audio_video(audio_info_file, output_file) 