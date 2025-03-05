import os
from pathlib import Path
from text_processor import TextProcessor
from voice_generator import VoiceVoxGenerator
from story_analyzer import StoryAnalyzer
from image_generator import ComfyUIGenerator
from midjourney_generator import MidjourneyGenerator
from video_maker import create_base_video
from video_maker_moviepy import create_video_with_scenes_moviepy
from generate_srt import generate_srt
from add_subtitles import add_subtitles
import json
import subprocess
import argparse
import sys

def clean_output_directories():
    """清理输出目录中的旧文件"""
    print("=== 清理旧数据 ===")
    
    # 需要清理的目录
    dirs_to_clean = [
        "output/audio",
        "output/images",
        "output/texts",
        "temp",  # 临时文件目录
    ]
    
    # 需要清理的文件
    files_to_clean = [
        "output/base_video.mp4",
        "output/final_video.mp4",
        "output/key_scenes.json",
        "output/*.srt",
        "output/*_final.mp4"
    ]
    
    try:
        # 清理目录中的文件
        for dir_path in dirs_to_clean:
            dir_path = Path(dir_path)
            if dir_path.exists():
                for file in dir_path.glob("*"):
                    try:
                        file.unlink()
                        print(f"已删除: {file}")
                    except Exception as e:
                        print(f"删除文件失败 {file}: {e}")
        
        # 清理特定文件
        for file_pattern in files_to_clean:
            for file in Path().glob(file_pattern):
                try:
                    file.unlink()
                    print(f"已删除: {file}")
                except Exception as e:
                    print(f"删除文件失败 {file}: {e}")
        
        print("清理完成！\n")
        
    except Exception as e:
        print(f"清理过程中出错: {e}")

def process_story(input_file: str, image_generator_type: str = "comfyui"):
    """
    完整的故事处理流程
    
    Args:
        input_file: 输入文本文件路径
        image_generator_type: 图像生成器类型，可选 "comfyui" 或 "midjourney"
    """
    # 检查输入文件是否存在
    full_input_path = input_file
    if not os.path.isabs(input_file):
        # 如果提供的是相对路径，且不包含目录，则假定它位于input_texts目录中
        if not os.path.dirname(input_file):
            full_input_path = os.path.join("input_texts", input_file)
    
    # 验证文件存在
    if not os.path.exists(full_input_path):
        error_msg = f"错误: 找不到输入文件 {full_input_path}"
        print(error_msg)
        return error_msg
    
    # 先清理旧数据
    clean_output_directories()
    
    print("=== 开始处理故事 ===")
    print(f"输入文件: {full_input_path}")
    print(f"图像生成方式: {image_generator_type}")
    
    # 创建所需目录
    for dir_name in ["output", "output/audio", "output/images", "output/texts", "output/videos"]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. 文本处理
        print("\n1. 处理文本...")
        text_processor = TextProcessor()
        try:
            with open(full_input_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            # 尝试使用系统默认编码
            import locale
            system_encoding = locale.getpreferredencoding()
            print(f"UTF-8编码读取失败，尝试使用系统编码: {system_encoding}")
            with open(full_input_path, "r", encoding=system_encoding) as f:
                text = f.read()
        
        if not text.strip():
            error_msg = f"错误: 输入文件 {full_input_path} 为空"
            print(error_msg)
            return error_msg
            
        sentences = text_processor.process_japanese_text(text)
        
        # 保存处理后的文本
        output_text_file = f"output/texts/{Path(full_input_path).name}"
        with open(output_text_file, "w", encoding="utf-8") as f:
            f.write("\n".join(sentences))
        print(f"文本处理完成，已保存到: {output_text_file}")
        
        # 2. 生成语音
        print("\n2. 生成语音...")
        audio_info_file = f"output/audio/{Path(full_input_path).stem}_audio_info.json"
        from test_voice_generator import process_voice_generation
        audio_info = process_voice_generation(output_text_file, "output/audio")
        print(f"语音生成完成，信息已保存到: {audio_info_file}")
        
        # 3. 分析故事和生成场景
        print("\n3. 分析故事和生成场景...")
        analyzer = StoryAnalyzer()
        story_analysis = analyzer.analyze_story(text, full_input_path)
        key_scenes = analyzer.identify_key_scenes(sentences)
        
        # 保存场景信息
        with open("output/key_scenes.json", "w", encoding="utf-8") as f:
            json.dump(key_scenes, f, ensure_ascii=False, indent=2)
        print("场景分析完成，信息已保存")
        
        # 4. 生成图片
        print("\n4. 生成图片...")
        
        # 根据用户选择的图像生成器类型创建相应的生成器
        if image_generator_type.lower() == "midjourney":
            print("使用 Midjourney API 生成图片...")
            image_generator = MidjourneyGenerator()
        else:  # 默认使用 ComfyUI
            print("使用 ComfyUI 生成图片...")
            image_generator = ComfyUIGenerator()
        
        image_generator.generate_images("output/key_scenes.json")
        print("图片生成完成")
        
        # 5. 生成字幕
        print("\n5. 生成字幕...")
        srt_file = f"output/{Path(full_input_path).stem}.srt"
        generate_srt(audio_info_file, srt_file)
        print(f"字幕生成完成: {srt_file}")
        
        # 6. 创建视频
        print("\n6. 创建视频...")
        base_video = "output/base_video.mp4"
        create_base_video(audio_info_file, base_video)

        final_video = "output/final_video_moviepy.mp4"
        create_video_with_scenes_moviepy("output/key_scenes.json", base_video, final_video)
        print("视频创建完成")
        
        # 7. 添加字幕
        print("\n7. 添加字幕...")
        output_video = f"output/{Path(full_input_path).stem}_final.mp4"
        add_subtitles(final_video, srt_file, output_video)
        print(f"最终视频已生成: {output_video}")
        
        print("\n=== 处理完成 ===")
        return output_video
        
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="故事视频生成器")
    parser.add_argument("input_file", nargs="?", help="输入文本文件名称或路径")
    parser.add_argument("--image_generator", choices=["comfyui", "midjourney"], default="comfyui",
                        help="选择图像生成器: comfyui (默认) 或 midjourney")
    parser.add_argument("-g", "--generator", choices=["comfyui", "midjourney"], default="comfyui",
                        help="选择图像生成器: comfyui (默认) 或 midjourney (与--image_generator相同)")
    args = parser.parse_args()

    # 设置图像生成器 (优先使用--image_generator)
    image_generator = args.image_generator
    if args.generator != "comfyui" and args.image_generator == "comfyui":
        image_generator = args.generator

    # 处理输入文件参数
    if args.input_file:
        input_file = args.input_file
    else:
        # 获取 input_texts 目录中的第一个 txt 文件
        input_dir = Path("input_texts")
        if not input_dir.exists():
            print(f"错误：输入目录 {input_dir} 不存在，正在创建...")
            input_dir.mkdir(parents=True)
            print("请在 input_texts 目录中放入文本文件后重试")
            sys.exit(1)
            
        txt_files = list(input_dir.glob("*.txt"))
        
        if not txt_files:
            print("错误：input_texts 目录中没有找到文本文件！")
            print("请在 input_texts 目录中放入文本文件后重试")
            sys.exit(1)
        
        # 使用找到的第一个文件
        input_file = str(txt_files[0])
    
    print(f"使用输入文件: {input_file}")
    
    # 处理函数已经包含文件存在性检查，直接调用
    result = process_story(input_file, image_generator) 
    
    if result is None or isinstance(result, str) and result.startswith("错误:"):
        sys.exit(1) 