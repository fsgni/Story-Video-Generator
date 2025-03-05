import gradio as gr
import os
import subprocess
import glob
import json
import locale
import sys
from pathlib import Path

# 获取系统默认编码
system_encoding = locale.getpreferredencoding()
print(f"系统默认编码: {system_encoding}")

# 示例文本
example_texts = [
    "一只猫在屋顶上晒太阳，它看到了一只飞过的鸟，想要追上去。",
    "In the quiet forest, a small rabbit hopped along the path, searching for carrots hidden beneath the autumn leaves.",
    "The spaceship descended slowly, its lights illuminating the dark surface of the unknown planet."
]

def list_input_files():
    """列出input_texts目录下的所有.txt文件"""
    # 确保目录存在
    os.makedirs("input_texts", exist_ok=True)
    
    files = glob.glob("input_texts/*.txt")
    if not files:
        return ["没有找到文本文件。请在input_texts目录添加.txt文件或直接输入文本。"]
    return [os.path.basename(f) for f in files]

def list_video_files():
    """列出output/videos目录下的所有.mp4文件"""
    # 确保目录存在
    os.makedirs("output/videos", exist_ok=True)
    
    files = glob.glob("output/videos/*.mp4") + glob.glob("output/*.mp4")
    if not files:
        return []
    return [f for f in files]

def process_story(text_input, selected_file, image_generator_type):
    """处理故事，可以是直接输入的文本或选择的文件"""
    if not text_input and not selected_file:
        return "错误: 请输入文本或选择一个文件", None
    
    # 确保input_texts目录存在
    os.makedirs("input_texts", exist_ok=True)
    
    # 如果有直接输入的文本，将其保存到文件
    if text_input:
        with open("input_texts/webui_input.txt", "w", encoding="utf-8") as f:
            f.write(text_input)
        input_file = "webui_input.txt"
    else:
        # 检查选择的文件是否存在
        input_file = selected_file
        full_path = os.path.join("input_texts", input_file)
        if not os.path.exists(full_path):
            return f"错误: 文件 {full_path} 不存在", None
    
    # 构建命令
    cmd = [sys.executable, "full_process.py", input_file, "--image_generator", image_generator_type]
    
    # 运行命令并实时获取输出
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        text=True,
        encoding=system_encoding  # 使用系统默认编码而不是UTF-8
    )
    
    output = ""
    latest_video = None
    
    for line in process.stdout:
        output += line
        yield output, None
    
    process.wait()
    
    if process.returncode != 0:
        output += f"\n处理完成，但存在错误 (返回码: {process.returncode})"
    else:
        output += "\n处理完成！"
        
        # 找到生成的视频文件
        video_files = glob.glob("output/*.mp4") + glob.glob("output/videos/*.mp4")
        if video_files:
            latest_video = max(video_files, key=os.path.getmtime)
            output += f"\n生成的视频: {latest_video}"
            output += f"\n👆 可以在上方的视频播放器中预览，或点击视频下方的下载按钮保存到本地"
    
    yield output, latest_video

def update_video_dropdown():
    """更新视频下拉列表"""
    videos = list_video_files()
    return gr.Dropdown.update(choices=videos, value=videos[0] if videos else None)

# 创建Gradio界面
with gr.Blocks(title="故事视频生成器", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 故事视频生成器")
    gr.Markdown("输入文本或选择已有文件，生成视频。")
    
    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                label="输入故事文本",
                placeholder="在这里输入您的故事...",
                lines=10
            )
            
            with gr.Row():
                refresh_button = gr.Button("刷新文件列表")
                file_dropdown = gr.Dropdown(
                    label="或者选择一个文件",
                    choices=list_input_files(),
                    interactive=True
                )
            
            with gr.Row():
                image_generator = gr.Radio(
                    label="选择图像生成方式",
                    choices=["comfyui", "midjourney"],
                    value="comfyui"
                )
                process_button = gr.Button("开始处理", variant="primary")
        
        with gr.Column(scale=3):
            output_text = gr.Textbox(
                label="处理输出",
                placeholder="处理日志将显示在这里...",
                lines=15
            )
            
            # 视频播放区域
            video_output = gr.Video(
                label="生成的视频",
                interactive=False
            )
    
    # 添加视频文件浏览器部分
    with gr.Row():
        with gr.Column():
            gr.Markdown("## 已生成的视频")
            refresh_videos_button = gr.Button("刷新视频列表")
            video_dropdown = gr.Dropdown(
                label="选择视频文件",
                choices=list_video_files(),
                interactive=True
            )
            selected_video = gr.Video(
                label="选中的视频",
                interactive=False
            )
    
    # 示例
    gr.Examples(
        examples=example_texts,
        inputs=text_input
    )
    
    # 事件处理
    refresh_button.click(list_input_files, outputs=file_dropdown)
    process_button.click(
        process_story, 
        inputs=[text_input, file_dropdown, image_generator], 
        outputs=[output_text, video_output]
    )
    
    # 视频浏览功能
    refresh_videos_button.click(update_video_dropdown, outputs=video_dropdown)
    video_dropdown.change(lambda x: x, inputs=video_dropdown, outputs=selected_video)
    
    gr.Markdown("""
    ## 使用说明
    1. 直接在文本框中输入故事，或选择input_texts目录中的文件
    2. 选择图像生成方式: ComfyUI(本地) 或 Midjourney(API)
    3. 点击"开始处理"按钮
    4. 等待处理完成，查看输出日志
    5. 生成的视频将在处理完成后直接显示在界面上
    6. 您也可以在"已生成的视频"部分浏览和查看所有生成的视频
    7. 视频播放器下方有下载按钮，可以将视频保存到本地
    """)

# 启动服务
if __name__ == "__main__":
    demo.launch()