import subprocess
from pathlib import Path

def add_subtitles(video_file, srt_file, output_file, font_name="UD Digi Kyokasho N-B", font_size=18, font_color="FFFFFF", bg_opacity=0.5):
    """
    为视频添加字幕
    
    参数:
        video_file: 输入视频文件路径
        srt_file: SRT字幕文件路径
        output_file: 输出视频文件路径
        font_name: 字体名称 (默认使用日语数字教科书字体)
        font_size: 字体大小 (默认18，较小)
        font_color: 字体颜色 (默认白色 FFFFFF)
        bg_opacity: 背景透明度 (0-1，0为完全透明，1为不透明)
    """
    # 检查字体是否存在
    font_name = check_font_name(font_name)
    
    # 构建FFmpeg命令
    bg_alpha = int(bg_opacity * 255)  # 将0-1的透明度转换为0-255的alpha值
    
    cmd = [
        'ffmpeg', '-y',
        '-i', video_file,
        '-vf', f"subtitles={srt_file}:force_style='FontName={font_name},FontSize={font_size},PrimaryColour=&H{font_color},BackColour=&H{bg_alpha}000000,BorderStyle=4,Outline=1,Shadow=1,MarginV=30'",
        '-c:v', 'libx264',
        '-c:a', 'copy',
        output_file
    ]
    
    # 执行命令
    subprocess.run(cmd)
    
    return output_file

def check_font_name(font_name="UD Digi Kyokasho N-B"):
    """
    检查系统中是否存在指定字体，如果不存在则返回备选字体
    
    参数:
        font_name: 首选字体名称
    
    返回:
        存在的字体名称
    """
    try:
        import matplotlib.font_manager as fm
        fonts = [f.name for f in fm.fontManager.ttflist]
        
        # 打印所有字体名称，帮助调试
        print("系统中的字体:")
        for font in sorted(fonts):
            if "digi" in font.lower() or "kyokasho" in font.lower() or "教科書" in font:
                print(f"- {font} (可能适合日语)")
            
        # 如果指定字体存在，直接返回
        if font_name in fonts:
            print(f"找到指定字体: {font_name}")
            return font_name
            
        # 查找日语字体
        japanese_fonts = [f for f in fonts if "digi" in f.lower() or "kyokasho" in f.lower() or 
                          "教科書" in f or "gothic" in f.lower() or "mincho" in f.lower() or 
                          "meiryo" in f.lower() or "yu" in f.lower()]
        
        if japanese_fonts:
            print(f"使用日语字体: {japanese_fonts[0]}")
            return japanese_fonts[0]
            
        # 查找备选字体
        if "SimHei" in fonts:
            return "SimHei"
        elif "Microsoft YaHei" in fonts:
            return "Microsoft YaHei"
        elif "Arial" in fonts:
            return "Arial"
        
        # 如果找不到合适的字体，返回系统中的第一个字体
        if fonts:
            return fonts[0]
        
        # 如果实在找不到任何字体，返回原始字体名称
        return font_name
    except Exception as e:
        print(f"检查字体时出错: {e}")
        return font_name

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
    video_file = "output/final_video_moviepy.mp4"
    # 字幕文件
    srt_file = "output/豚.srt"
    # 输出文件
    output_file = "output/TESTTEST_final.mp4"
    
    add_subtitles(video_file, srt_file, output_file) 