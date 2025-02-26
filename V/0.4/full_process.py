import os
from pathlib import Path
from text_processor import TextProcessor
from voice_generator import VoiceVoxGenerator
from story_analyzer import StoryAnalyzer
from image_generator import ComfyUIGenerator
from video_maker import create_base_video, create_video_with_scenes
from generate_srt import generate_srt
from add_subtitles import add_subtitles
import json

def process_story(input_file: str):
    """完整的故事处理流程"""
    print("=== 开始处理故事 ===")
    
    # 创建所需目录
    for dir_name in ["output", "output/audio", "output/images", "output/texts"]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    # 1. 文本处理
    print("\n1. 处理文本...")
    text_processor = TextProcessor()
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
    sentences = text_processor.process_japanese_text(text)
    
    # 保存处理后的文本
    output_text_file = f"output/texts/{Path(input_file).name}"
    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sentences))
    print(f"文本处理完成，已保存到: {output_text_file}")
    
    # 2. 生成语音
    print("\n2. 生成语音...")
    voice_generator = VoiceVoxGenerator()
    audio_info_file = f"output/audio/{Path(input_file).stem}_audio_info.json"
    from test_voice_generator import process_voice_generation
    audio_info = process_voice_generation(output_text_file, "output/audio")
    print(f"语音生成完成，信息已保存到: {audio_info_file}")
    
    # 3. 分析故事和生成场景
    print("\n3. 分析故事和生成场景...")
    analyzer = StoryAnalyzer()
    story_analysis = analyzer.analyze_story(text, input_file)
    key_scenes = analyzer.identify_key_scenes(sentences)
    
    # 保存场景信息
    with open("output/key_scenes.json", "w", encoding="utf-8") as f:
        json.dump(key_scenes, f, ensure_ascii=False, indent=2)
    print("场景分析完成，信息已保存")
    
    # 4. 生成图片
    print("\n4. 生成图片...")
    image_generator = ComfyUIGenerator()
    image_generator.generate_images("output/key_scenes.json")
    print("图片生成完成")
    
    # 5. 生成字幕
    print("\n5. 生成字幕...")
    srt_file = f"output/{Path(input_file).stem}.srt"
    generate_srt(audio_info_file, srt_file)
    print(f"字幕生成完成: {srt_file}")
    
    # 6. 创建视频
    print("\n6. 创建视频...")
    # 创建基础视频
    base_video = "output/base_video.mp4"
    create_base_video(audio_info_file, base_video)
    
    # 添加图片
    final_video = "output/final_video.mp4"
    create_video_with_scenes("output/key_scenes.json", base_video, final_video)
    print("视频创建完成")
    
    # 7. 添加字幕
    print("\n7. 添加字幕...")
    output_video = f"output/{Path(input_file).stem}_final.mp4"
    add_subtitles(final_video, srt_file, output_video)
    print(f"最终视频已生成: {output_video}")
    
    print("\n=== 处理完成 ===")

if __name__ == "__main__":
    # 获取 input_texts 目录中的第一个 txt 文件
    input_dir = Path("input_texts")
    txt_files = list(input_dir.glob("*.txt"))
    
    if not txt_files:
        print("错误：input_texts 目录中没有找到文本文件！")
        exit(1)
    
    # 使用找到的第一个文件
    input_file = str(txt_files[0])
    print(f"使用输入文件: {input_file}")
    process_story(input_file) 