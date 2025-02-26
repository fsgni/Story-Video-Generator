import json
from pathlib import Path
import subprocess
import os
from shutil import copy2

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

def create_video_with_images(key_scenes_file: str, base_video: str, output_file: str):
    """使用图片创建最终视频"""
    # 读取场景信息
    with open(key_scenes_file, 'r', encoding='utf-8') as f:
        scenes = json.load(f)
    
    # 创建临时文件列表
    with open('temp_files.txt', 'w', encoding='utf-8') as f:
        for scene in scenes:
            # 每个场景的图片显示时长
            duration = scene['end_time'] - scene['start_time']
            # 图片文件路径
            image_file = f"output/images/{scene['image_file']}"
            # 写入文件列表
            f.write(f"file '{image_file}'\n")
            f.write(f"duration {duration}\n")
    
    # 使用 ffmpeg 合成视频
    subprocess.run([
        'ffmpeg', '-y',
        '-i', base_video,  # 输入基础视频（带音频和字幕）
        '-f', 'concat',
        '-i', 'temp_files.txt',  # 图片序列
        '-filter_complex', 
        '[1:v]scale=1920:1080,format=yuva420p[fg];'  # 缩放图片
        '[0:v][fg]overlay=0:0:enable=\'between(t,{start_time},{end_time})\'[out]',  # 叠加图片
        '-map', '[out]',  # 使用合成后的视频流
        '-map', '0:a',    # 使用原始音频流
        '-c:v', 'libx264',
        '-c:a', 'copy',
        output_file
    ])

def create_merged_audio(audio_info_file: str, output_file: str):
    """合并所有音频文件"""
    # 读取音频信息
    with open(audio_info_file, 'r', encoding='utf-8') as f:
        info = json.load(f)
    
    # 创建临时文件目录
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # 创建音频文件列表
    concat_file = temp_dir / "concat.txt"
    audio_path = Path("output/audio")  # 修正音频文件路径
    
    with open(concat_file, 'w', encoding='utf-8') as f:
        for audio_info in info['audio_files']:
            audio_file = audio_path / audio_info['audio_file']
            f.write(f"file '{audio_file.absolute()}'\n")
    
    # 合并音频文件
    subprocess.run([
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',
        output_file
    ], check=True)  # 添加 check=True 来捕获错误
    
    # 清理临时文件
    concat_file.unlink()
    temp_dir.rmdir()

def create_base_video(audio_info_file: str, output_file: str, resolution=(1920, 1080)):
    """创建基础黑色背景视频"""
    # 确保输出目录存在
    output_path = Path(output_file).parent
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. 首先合并音频
    merged_audio = output_path / "merged.wav"
    print("合并音频文件...")
    create_merged_audio(audio_info_file, merged_audio)
    
    # 2. 读取音频信息获取总时长
    with open(audio_info_file, 'r', encoding='utf-8') as f:
        info = json.load(f)
    duration = info['total_duration']
    width, height = resolution
    
    # 3. 创建带音频的黑色背景视频
    print("创建基础视频...")
    subprocess.run([
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f'color=c=black:s={width}x{height}:d={duration}',
        '-i', str(merged_audio),  # 使用合并后的音频
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',
        output_file
    ])
    
    # 清理临时文件
    merged_audio.unlink()

def create_video_with_scenes(key_scenes_file: str, base_video: str, output_file: str, batch_size=10):
    """分批处理场景生成视频"""
    # 读取场景信息
    with open(key_scenes_file, "r", encoding="utf-8") as f:
        scenes = json.load(f)
    
    # 确保输出目录存在
    output_path = Path(output_file).parent
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 创建临时目录
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # 复制基础视频作为第一个临时文件
    current_video = temp_dir / "temp_0.mp4"
    copy2(base_video, current_video)
    
    # 分批处理场景
    for batch_idx in range(0, len(scenes), batch_size):
        batch_scenes = scenes[batch_idx:batch_idx + batch_size]
        
        # 创建 ffmpeg 滤镜命令
        filter_complex = []
        filter_complex.append("[0:v]format=yuva420p[base]")
        
        # 为每个场景添加图片叠加
        for i, scene in enumerate(batch_scenes):
            # 添加图片输入流
            filter_complex.append(f"[{i+1}:v]format=rgba,scale=1920:1080[img{i}]")
            
            # 在正确的时间点叠加图片
            start_time = scene["start_time"]
            end_time = scene["end_time"]
            if i == 0:
                filter_complex.append(
                    f"[base][img{i}]overlay=0:0:enable='between(t,{start_time},{end_time})'[v{i}]"
                )
            else:
                filter_complex.append(
                    f"[v{i-1}][img{i}]overlay=0:0:enable='between(t,{start_time},{end_time})'[v{i}]"
                )
        
        # 构建 ffmpeg 命令
        next_video = temp_dir / f"temp_{batch_idx + batch_size}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", str(current_video),  # 输入上一个临时视频
        ]
        
        # 添加这一批的图片输入
        for scene in batch_scenes:
            cmd.extend(["-i", f"output/images/{scene['image_file']}"])
        
        # 添加滤镜复杂度和输出选项
        cmd.extend([
            "-filter_complex", ";".join(filter_complex),
            "-map", f"[v{len(batch_scenes)-1}]",  # 使用最后一个视频流
            "-map", "0:a",  # 使用原始音频
            "-c:v", "libx264",
            "-c:a", "copy",
            str(next_video)
        ])
        
        print(f"处理第 {batch_idx+1} 到 {batch_idx+len(batch_scenes)} 个场景...")
        subprocess.run(cmd, check=True)
        
        # 更新当前视频文件
        current_video = next_video
    
    # 最后一个临时文件就是最终结果
    copy2(current_video, output_file)
    
    # 清理临时文件
    for file in temp_dir.glob("*.mp4"):
        file.unlink()
    temp_dir.rmdir()

if __name__ == "__main__":
    # 音频信息文件路径
    audio_info_file = "output/audio/お菓子の森の秘密星に願いを込めてなど_audio_info.json"
    base_video = "output/base_video.mp4"
    final_video = "output/final_video.mp4"
    
    # 1. 创建基础视频
    print("创建基础视频...")
    create_base_video(audio_info_file, base_video)
    
    # 2. 添加场景图片
    print("\n添加场景图片...")
    create_video_with_scenes(
        "output/key_scenes.json",
        base_video,
        final_video,
        batch_size=10  # 每次处理10个场景
    )
    
    print("\n处理完成！") 