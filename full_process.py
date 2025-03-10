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
import time
import shutil

# 设置系统编码为UTF-8，解决Windows命令行的编码问题
if sys.stdout.encoding != 'utf-8':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    elif hasattr(sys.stdout, 'buffer'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='backslashreplace')

def clean_output_directories():
    """清理输出目录中的旧文件"""
    try:
        # 清理图像目录
        image_dir = Path("output/images")
        if image_dir.exists():
            for file in image_dir.glob("*.png"):
                try:
                    file.unlink()
                    print(f"已删除: {file}")
                except Exception as e:
                    print(f"无法删除 {file}: {e}")
        
        # 清理视频目录
        video_dir = Path("output/videos")
        if video_dir.exists():
            for file in video_dir.glob("*.mp4"):
                try:
                    file.unlink()
                    print(f"已删除: {file}")
                except Exception as e:
                    print(f"无法删除 {file}: {e}")
        
        # 清理音频目录
        audio_dir = Path("output/audio")
        if audio_dir.exists():
            for file in audio_dir.glob("*.*"):
                try:
                    file.unlink()
                    print(f"已删除: {file}")
                except Exception as e:
                    print(f"无法删除 {file}: {e}")
        
        # 清理文本目录
        texts_dir = Path("output/texts")
        if texts_dir.exists():
            for file in texts_dir.glob("*.txt"):
                try:
                    file.unlink()
                    print(f"已删除: {file}")
                except Exception as e:
                    print(f"无法删除 {file}: {e}")
        
        # 清理根输出目录中的临时文件
        output_dir = Path("output")
        if output_dir.exists():
            # 清理根目录中的视频文件
            for file in output_dir.glob("*.mp4"):
                try:
                    file.unlink()
                    print(f"已删除: {file}")
                except Exception as e:
                    print(f"无法删除 {file}: {e}")
            
            for file in output_dir.glob("*.srt"):
                try:
                    file.unlink()
                    print(f"已删除: {file}")
                except Exception as e:
                    print(f"无法删除 {file}: {e}")
            
            for file in output_dir.glob("*.json"):
                try:
                    file.unlink()
                    print(f"已删除: {file}")
                except Exception as e:
                    print(f"无法删除 {file}: {e}")
    
        print("输出目录清理完成")
    except Exception as e:
        print(f"清理输出目录时出错: {e}")

def process_story(input_file: str, image_generator_type: str = "comfyui", aspect_ratio: str = None, image_style: str = None, comfyui_style: str = None):
    """
    完整的故事处理流程
    
    Args:
        input_file: 输入文本文件路径
        image_generator_type: 图像生成器类型，可选 "comfyui" 或 "midjourney"
        aspect_ratio: 图像比例，可选值为 "16:9", "9:16" 或 None (默认方形)，仅对midjourney有效
        image_style: 图像风格，例如: 'cinematic lighting, movie quality' 或 'ancient Chinese ink painting style'
        comfyui_style: ComfyUI的风格选项，可选值为 "水墨", "手绘", "古风", "插画", "写实", "电影"
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
    print(f"图像生成器: {image_generator_type}")
    if aspect_ratio and image_generator_type.lower() == "midjourney":
        print(f"图像比例: {aspect_ratio}")
    if image_style:
        print(f"图像风格: {image_style}")
    if comfyui_style and image_generator_type.lower() == "comfyui":
        print(f"ComfyUI风格: {comfyui_style}")
    
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
        
        # 4. 生成图像
        print("\n4. 生成图像...")
        image_files = []
        
        if image_generator_type.lower() == "comfyui":
            # 使用ComfyUI生成图像
            generator = ComfyUIGenerator(style=comfyui_style)
            
            # 打印可用的风格选项
            available_styles = generator.get_available_styles()
            print(f"可用的ComfyUI风格选项: {', '.join(available_styles)}")
            
            for i, scene in enumerate(key_scenes):
                # 确保提取正确的提示词
                if isinstance(scene, dict) and 'prompt' in scene:
                    scene_prompt = scene['prompt']
                else:
                    scene_prompt = str(scene)
                
                # 添加艺术风格
                base_style = story_analysis.get('art_style', '')
                # 如果用户指定了风格，优先使用用户指定的风格，不添加额外风格词汇
                if image_style:
                    # 直接使用场景提示词，不添加基础风格，避免风格混淆
                    scene_prompt = f"{scene_prompt}, {image_style}, detailed facial expressions, dynamic poses, high quality"
                elif base_style:
                    scene_prompt = f"{scene_prompt}, {base_style}, detailed facial expressions, dynamic poses, high quality"
                else:
                    # 如果没有任何风格，添加通用高质量词汇
                    scene_prompt = f"{scene_prompt}, detailed facial expressions, dynamic poses, high quality"
                
                print(f"场景 {i+1} 提示词: {scene_prompt}")
                
                # 使用与key_scenes.json中相同的文件名格式
                image_filename = scene['image_file'] if isinstance(scene, dict) and 'image_file' in scene else f"scene_{i+1:03d}.png"
                
                image_file = generator.generate_image(scene_prompt, image_filename)
                if image_file:
                    image_files.append(image_file)
        else:
            # 使用Midjourney生成图像
            generator = MidjourneyGenerator()
            for i, scene in enumerate(key_scenes):
                # 确保提取正确的提示词
                if isinstance(scene, dict) and 'prompt' in scene:
                    scene_prompt = scene['prompt']
                else:
                    scene_prompt = str(scene)
                
                # 添加艺术风格
                base_style = story_analysis.get('art_style', '')
                # 如果用户指定了风格，优先使用用户指定的风格，不添加额外风格词汇
                if image_style:
                    # 直接使用场景提示词，不添加基础风格，避免风格混淆
                    scene_prompt = f"{scene_prompt}, {image_style}, detailed facial expressions, dynamic poses, high quality"
                elif base_style:
                    scene_prompt = f"{scene_prompt}, {base_style}, detailed facial expressions, dynamic poses, high quality"
                else:
                    # 如果没有任何风格，添加通用高质量词汇
                    scene_prompt = f"{scene_prompt}, detailed facial expressions, dynamic poses, high quality"
                
                print(f"场景 {i+1} 提示词: {scene_prompt}")
                
                # 使用与key_scenes.json中相同的文件名格式
                image_filename = scene['image_file'] if isinstance(scene, dict) and 'image_file' in scene else f"scene_{i+1:03d}.png"
                
                image_file = generator.generate_image(scene_prompt, image_filename, aspect_ratio=aspect_ratio)
                if image_file:
                    image_files.append(image_file)
        
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
    parser.add_argument("--aspect_ratio", choices=["16:9", "9:16"], 
                        help="设置图像比例 (仅对midjourney有效): 16:9 (横屏) 或 9:16 (竖屏)")
    parser.add_argument("--image_style", 
                        help="设置图像风格，例如: 'cinematic lighting, movie quality' 或 'ancient Chinese ink painting style'")
    parser.add_argument("--comfyui_style", 
                        help="设置ComfyUI的风格选项，可选值为 '水墨', '手绘', '古风', '插画', '写实', '电影'")
    args = parser.parse_args()

    # 打印参数信息，便于调试
    print("命令行参数:")
    print(f"  输入文件: {args.input_file}")
    print(f"  图像生成器: {args.image_generator}")
    print(f"  图像比例: {args.aspect_ratio}")
    print(f"  图像风格: {args.image_style}")
    print(f"  ComfyUI风格: {args.comfyui_style}")

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
    result = process_story(input_file, image_generator, args.aspect_ratio, args.image_style, args.comfyui_style) 
    
    if result is None or isinstance(result, str) and result.startswith("错误:"):
        sys.exit(1) 