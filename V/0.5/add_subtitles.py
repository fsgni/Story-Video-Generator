import subprocess
from pathlib import Path

def add_subtitles(video_file: str, srt_file: str, output_file: str):
    """为视频添加字幕"""
    # 使用 UD Digi Kyokasho N-B 字体
    font_name = "UD Digi Kyokasho N-B"
    
    subprocess.run([
        'ffmpeg', '-y',
        '-i', video_file,
        '-vf', f'subtitles={srt_file}:force_style=\'FontName={font_name},FontSize=20,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=1,Shadow=0,BorderStyle=3,MarginV=35,BackColour=&H00000080&\'',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'copy',
        output_file
    ])

def check_font_name():
    """检查系统中的字体名称"""
    try:
        import matplotlib.font_manager as fm
        fonts = [f.name for f in fm.fontManager.ttflist]
        # 查找包含 "Digi" 或 "Kyokasho" 的字体
        digi_fonts = [f for f in fonts if "DIGI" in f.upper() or "KYOKASHO" in f.upper()]
        print("找到的相关字体:")
        for font in digi_fonts:
            print(f"- {font}")
        return digi_fonts
    except Exception as e:
        print(f"检查字体时出错: {e}")
        return []

if __name__ == "__main__":
    # 先检查字体
    print("检查系统字体...")
    available_fonts = check_font_name()
    if available_fonts:
        print("\n使用找到的第一个字体...")
        font_name = available_fonts[0]
    else:
        print("\n未找到 UD Digi Kyokasho N-B 字体，使用默认字体...")
        font_name = "UD Digi Kyokasho N-B"  # 默认名称
    
    # 输入视频
    video_file = "output/final_video.mp4"
    # 字幕文件
    srt_file = "output/豚.srt"
    # 输出文件
    output_file = "output/TESTTEST_final.mp4"
    
    add_subtitles(video_file, srt_file, output_file) 