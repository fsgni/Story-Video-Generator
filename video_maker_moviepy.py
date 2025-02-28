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
            
            # 随机选择电影效果类型 (简化为只有3种效果)
            # 0=缓慢平移, 1=缓慢放大, 2=缓慢缩小
            effect_type = random.randint(0, 2)
            
            # 加载图片
            img_clip = ImageClip(img_path)
            
            # 计算图片和视频的宽高比
            img_aspect = img_clip.w / img_clip.h
            video_aspect = video_width / video_height
            
            # 确保图片覆盖整个视频区域 - 增加到15%的安全边距
            if img_aspect > video_aspect:  # 图片更宽
                # 高度匹配视频，宽度按比例
                img_height = video_height * 1.15  # 增加15%的高度作为安全边距
                img_width = img_height * img_aspect
            else:  # 图片更高或相等
                # 宽度匹配视频，高度按比例
                img_width = video_width * 1.15  # 增加15%的宽度作为安全边距
                img_height = img_width / img_aspect
            
            # 调整图片大小
            img_clip = img_clip.resize(width=img_width, height=img_height)
            
            # 应用效果
            if effect_type == 0:  # 缓慢平移
                # 随机选择平移方向
                pan_direction = random.randint(0, 3)  # 0=左到右, 1=右到左, 2=上到下, 3=下到上
                
                # 计算平移距离 (非常小的移动，只有5%)
                pan_distance = min(img_width, img_height) * 0.05
                
                # 定义位置函数
                def pos_func(t):
                    # 线性移动，确保整个持续时间内都在移动
                    progress = t / duration
                    
                    if pan_direction == 0:  # 从左到右
                        x = -img_width/2 + video_width/2 - pan_distance/2 + progress * pan_distance
                        y = -img_height/2 + video_height/2
                    elif pan_direction == 1:  # 从右到左
                        x = -img_width/2 + video_width/2 + pan_distance/2 - progress * pan_distance
                        y = -img_height/2 + video_height/2
                    elif pan_direction == 2:  # 从上到下
                        x = -img_width/2 + video_width/2
                        y = -img_height/2 + video_height/2 - pan_distance/2 + progress * pan_distance
                    else:  # 从下到上
                        x = -img_width/2 + video_width/2
                        y = -img_height/2 + video_height/2 + pan_distance/2 - progress * pan_distance
                    
                    return (int(x), int(y))
                
            elif effect_type == 1:  # 缓慢放大
                # 从小到大缓慢放大 (从100%到105%)
                start_scale = 1.0   # 修改为从100%开始
                end_scale = 1.05
                
                # 定义缩放函数
                def zoom_func(t):
                    # 线性缩放
                    progress = t / duration
                    return start_scale + (end_scale - start_scale) * progress
                
                # 应用缩放效果
                img_clip = img_clip.resize(lambda t: (int(img_width * zoom_func(t)), 
                                                     int(img_height * zoom_func(t))))
                
                # 定义位置函数 - 保持居中
                def pos_func(t):
                    scale = zoom_func(t)
                    x = -img_width * scale / 2 + video_width / 2
                    y = -img_height * scale / 2 + video_height / 2
                    return (int(x), int(y))
                
            else:  # 缓慢缩小
                # 从大到小缓慢缩小 (从105%到100%)
                start_scale = 1.05
                end_scale = 1.0    # 修改为到100%结束
                
                # 定义缩放函数
                def zoom_func(t):
                    # 线性缩放
                    progress = t / duration
                    return start_scale + (end_scale - start_scale) * progress
                
                # 应用缩放效果
                img_clip = img_clip.resize(lambda t: (int(img_width * zoom_func(t)), 
                                                     int(img_height * zoom_func(t))))
                
                # 定义位置函数 - 保持居中
                def pos_func(t):
                    scale = zoom_func(t)
                    x = -img_width * scale / 2 + video_width / 2
                    y = -img_height * scale / 2 + video_height / 2
                    return (int(x), int(y))
            
            # 设置持续时间和开始时间
            img_clip = img_clip.set_duration(duration).set_start(start_time)
            
            # 设置位置
            img_clip = img_clip.set_position(pos_func)
            
            # 添加淡入淡出效果
            # 计算淡入淡出时间 - 较短场景使用较短的淡入淡出时间
            fade_duration = min(0.5, duration / 10)  # 最长0.5秒，或者场景时长的1/10
            
            # 应用淡入淡出效果
            img_clip = img_clip.fadein(fade_duration).fadeout(fade_duration)
            
            # 添加到剪辑列表
            clips.append(img_clip)
            print(f"已添加图片: {scene['image_file']} 效果类型: {effect_type} 淡入淡出: {fade_duration:.2f}秒")
            
        except Exception as e:
            print(f"处理图片 {scene.get('image_file', '未知')} 时出错: {e}")
            import traceback
            traceback.print_exc()
    
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
        fps=30,  # 使用较高帧率
        preset='slow',
        bitrate='5000k'
    )
    
    # 关闭所有剪辑
    base_video.close()
    for clip in clips[1:]:
        try:
            clip.close()
        except:
            pass
    
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