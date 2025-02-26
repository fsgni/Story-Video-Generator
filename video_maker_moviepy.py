import json
from pathlib import Path
import random
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import numpy as np

def create_video_with_scenes_moviepy(key_scenes_file: str, input_video: str, output_file: str):
    """使用 MoviePy 创建带有场景图片的视频，实现电影般的镜头效果"""
    # 读取场景信息
    with open(key_scenes_file, 'r', encoding='utf-8') as f:
        scenes = json.load(f)
    
    # 加载基础视频
    base_video = VideoFileClip(input_video)
    video_width, video_height = base_video.w, base_video.h
    
    # 创建所有场景的图片剪辑
    clips = [base_video]  # 首先添加基础视频
    
    # 为每个场景设置固定的随机种子，确保效果一致
    random.seed(42)
    
    for scene in scenes:
        try:
            # 获取场景时间信息
            start_time = scene['start_time']
            end_time = scene['end_time']
            duration = end_time - start_time
            
            # 加载图片
            img_path = f"output/images/{scene['image_file']}"
            print(f"处理图片: {img_path}")
            img_clip = ImageClip(img_path).set_duration(duration)
            
            # 随机选择电影效果类型
            # 0=从左到右平移, 1=从右到左平移, 2=从上到下平移, 3=从下到上平移
            # 4=缓慢放大, 5=缓慢缩小
            effect_type = random.randint(0, 5)
            
            # 计算图片和视频的宽高比
            img_aspect = img_clip.w / img_clip.h
            video_aspect = video_width / video_height
            
            # 设置图片尺寸 - 确保图片完全覆盖视频，并且有额外空间用于移动
            # 我们将图片尺寸设置为比视频大10%，这样移动时不会露出黑边
            scale_factor = 1.1  # 比视频大10%
            
            if img_aspect > video_aspect:  # 图片更宽
                # 宽度按比例缩放，确保高度至少覆盖视频
                target_height = video_height * scale_factor
                target_width = target_height * img_aspect
            else:  # 图片更高或相等
                # 高度按比例缩放，确保宽度至少覆盖视频
                target_width = video_width * scale_factor
                target_height = target_width / img_aspect
            
            # 为缩放效果准备参数
            if effect_type == 4 or effect_type == 5:  # 放大或缩小效果
                # 对于缩放效果，我们需要更大的初始图片尺寸
                zoom_scale_factor = 1.2  # 比视频大20%
                
                if img_aspect > video_aspect:  # 图片更宽
                    zoom_height = video_height * zoom_scale_factor
                    zoom_width = zoom_height * img_aspect
                else:  # 图片更高或相等
                    zoom_width = video_width * zoom_scale_factor
                    zoom_height = zoom_width / img_aspect
                
                # 调整图片大小
                img_clip = img_clip.resize(width=zoom_width, height=zoom_height)
                
                # 缩放范围 - 从1.0到1.1或从1.1到1.0
                min_zoom = 1.0
                max_zoom = 1.1
                
                # 定义缩放函数
                if effect_type == 4:  # 缓慢放大
                    def zoom_func(t):
                        # 使用平滑的缓动函数 - 正弦曲线的前四分之一
                        progress = np.sin((t / duration) * np.pi/2)
                        zoom = min_zoom + (max_zoom - min_zoom) * progress
                        return zoom
                else:  # 缓慢缩小
                    def zoom_func(t):
                        # 使用平滑的缓动函数 - 余弦曲线的后四分之一
                        progress = np.cos((t / duration) * np.pi/2 + np.pi/2)
                        zoom = max_zoom - (max_zoom - min_zoom) * progress
                        return zoom
                
                # 定义位置函数
                def move_func(t):
                    # 获取当前缩放比例
                    current_zoom = zoom_func(t)
                    
                    # 计算当前尺寸
                    current_width = zoom_width * current_zoom
                    current_height = zoom_height * current_zoom
                    
                    # 计算位置，保持图片中心对齐视频中心
                    x = (video_width - current_width) / 2
                    y = (video_height - current_height) / 2
                    
                    return (x, y)
                
                # 设置缩放动画
                img_clip = img_clip.resize(lambda t: (zoom_width * zoom_func(t), zoom_height * zoom_func(t)))
            
            else:  # 平移效果
                # 调整图片大小
                img_clip = img_clip.resize(width=target_width, height=target_height)
                
                # 计算移动范围 - 确保移动时不会露出黑边
                # 移动范围是图片尺寸与视频尺寸的差值
                h_move_range = target_width - video_width
                v_move_range = target_height - video_height
                
                # 定义动画函数 - 使用平滑的移动效果
                if effect_type == 0:  # 从左到右平移
                    def move_func(t):
                        # 使用平滑的缓动函数 - 正弦曲线的前四分之一
                        progress = np.sin((t / duration) * np.pi/2)
                        # 从左边开始移动到右边，但确保图片始终覆盖整个视频
                        x = -progress * h_move_range
                        # 垂直居中
                        y = -(target_height - video_height) / 2
                        return (x, y)
                    
                elif effect_type == 1:  # 从右到左平移
                    def move_func(t):
                        # 使用平滑的缓动函数 - 正弦曲线的前四分之一
                        progress = np.sin((t / duration) * np.pi/2)
                        # 从右边开始移动到左边
                        x = -(1 - progress) * h_move_range
                        # 垂直居中
                        y = -(target_height - video_height) / 2
                        return (x, y)
                    
                elif effect_type == 2:  # 从上到下平移
                    def move_func(t):
                        # 使用平滑的缓动函数 - 正弦曲线的前四分之一
                        progress = np.sin((t / duration) * np.pi/2)
                        # 水平居中
                        x = -(target_width - video_width) / 2
                        # 从上边开始移动到下边
                        y = -progress * v_move_range
                        return (x, y)
                    
                else:  # 从下到上平移
                    def move_func(t):
                        # 使用平滑的缓动函数 - 正弦曲线的前四分之一
                        progress = np.sin((t / duration) * np.pi/2)
                        # 水平居中
                        x = -(target_width - video_width) / 2
                        # 从下边开始移动到上边
                        y = -(1 - progress) * v_move_range
                        return (x, y)
                
                # 设置位置
                img_clip = img_clip.set_position(move_func)
            
            # 设置动画和时间
            img_clip = img_clip.set_position(move_func).set_start(start_time)
            
            # 添加到剪辑列表
            clips.append(img_clip)
            print(f"已添加图片: {scene['image_file']} 效果类型: {effect_type}")
            
        except Exception as e:
            print(f"处理图片 {scene.get('image_file', '未知')} 时出错: {e}")
    
    # 合成最终视频
    print(f"合成视频，共 {len(clips)} 个剪辑...")
    final_video = CompositeVideoClip(clips)
    
    # 写入文件
    print(f"写入视频文件: {output_file}")
    final_video.write_videofile(
        output_file,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        fps=24,
        preset='slow',
        bitrate='5000k'
    )
    
    # 关闭所有剪辑
    base_video.close()
    for clip in clips[1:]:
        clip.close()
    
    print("视频创建完成！")

if __name__ == "__main__":
    import sys
    
    # 默认参数
    key_scenes_file = "output/key_scenes.json"
    input_video = "output/base_video.mp4"
    output_file = "output/final_video_moviepy.mp4"
    
    # 如果提供了命令行参数，则使用命令行参数
    if len(sys.argv) > 1:
        key_scenes_file = sys.argv[1]
    if len(sys.argv) > 2:
        input_video = sys.argv[2]
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    
    print(f"使用 MoviePy 创建视频...")
    print(f"场景文件: {key_scenes_file}")
    print(f"输入视频: {input_video}")
    print(f"输出文件: {output_file}")
    
    # 调用函数
    create_video_with_scenes_moviepy(key_scenes_file, input_video, output_file)
    
    print(f"视频创建完成！输出文件: {output_file}") 