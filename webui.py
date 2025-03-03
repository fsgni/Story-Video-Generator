import os
import gradio as gr
from pathlib import Path
import traceback

# 导入现有功能
from full_process import process_story as full_process

def process_story(text, progress=gr.Progress()):
    """处理故事文本，生成视频"""
    try:
        # 创建所需目录
        for dir_name in ["input_texts", "output"]:
            Path(dir_name).mkdir(exist_ok=True)
        
        # 保存文本到文件
        input_file = "input_texts/story.txt"
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(text)
        
        # 调用完整处理流程
        output_video = full_process(input_file)
        
        # 检查输出视频是否存在
        if output_video and os.path.exists(output_video):
            print(f"视频文件已生成: {output_video}")
            return "处理完成！", output_video
        else:
            # 尝试查找可能的视频文件
            possible_videos = [
                "output/story_final.mp4",
                "output/final_video_moviepy.mp4",
                "output/base_video.mp4"
            ]
            
            for video_path in possible_videos:
                if os.path.exists(video_path):
                    print(f"找到视频文件: {video_path}")
                    return "处理完成！", video_path
            
            return "处理完成，但找不到视频文件。请检查输出目录。", None
    
    except Exception as e:
        error_msg = f"处理过程中出错: {e}"
        print(error_msg)
        traceback.print_exc()
        return error_msg, None

def create_ui():
    """创建 Gradio 界面"""
    with gr.Blocks(title="Story Video Generator") as app:
        gr.Markdown("# Story Video Generator")
        gr.Markdown("TEXT TO VIDEO")
        
        with gr.Row():
            with gr.Column(scale=2):
                # 输入区域
                text_input = gr.Textbox(
                    label="Story Text (Japanese)",
                    placeholder="Enter Japanese story text here...",
                    lines=10
                )
                
                # 提交按钮
                submit_btn = gr.Button("Generate Video", variant="primary")
            
            with gr.Column(scale=3):
                # 输出区域
                output_text = gr.Textbox(label="Processing Result")
                output_video = gr.Video(label="Generated Video")
        
        # 设置提交按钮的动作
        submit_btn.click(
            fn=process_story,
            inputs=[text_input],
            outputs=[output_text, output_video]
        )
        
        # 示例
        gr.Examples(
            examples=[
                ["昔々あるところに、おじいさんとおばあさんが住んでいました。おじいさんは山へ芝刈りに、おばあさんは川へ洗濯に行きました。おばあさんが川で洗濯をしていると、大きな桃が流れてきました。"],
                ["むかしむかし、あるところに小さな村がありました。その村には、不思議な力を持つ少女が住んでいました。彼女の名前はユキといいます。"]
            ],
            inputs=text_input
        )
    
    return app

# 启动 WebUI
if __name__ == "__main__":
    app = create_ui()
    app.launch(share=True)  # share=True 允许通过公共 URL 访问