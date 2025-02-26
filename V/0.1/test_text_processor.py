from text_processor import TextProcessor
from pathlib import Path
import os
from dotenv import load_dotenv
import warnings

# 忽略特定警告
warnings.filterwarnings("ignore", category=UserWarning)

def process_text_files(input_dir, output_dir):
    """处理文本文件"""
    processor = TextProcessor()
    
    # 创建输出目录（如果不存在）
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 创建输入目录（如果不存在）
    input_path = Path(input_dir)
    input_path.mkdir(parents=True, exist_ok=True)
    
    # 获取输入目录中的所有txt文件
    txt_files = list(input_path.glob("*.txt"))
    
    if not txt_files:
        print(f"在 {input_dir} 中没有找到txt文件")
        return
    
    # 处理每个文件
    for txt_file in txt_files:
        print(f"\n处理文件: {txt_file.name}")
        
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                text = f.read()
            
            sentences = processor.process_japanese_text(text)
            
            if sentences:
                output_file = output_path / txt_file.name
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(sentences))
                print(f"分句结果已保存到: {output_file}")
            else:
                print(f"处理失败: {txt_file.name}")
                
        except Exception as e:
            print(f"处理文件 {txt_file.name} 时出错: {e}")

if __name__ == "__main__":
    input_directory = "input_texts"
    output_directory = "output_texts"
    process_text_files(input_directory, output_directory)
    
    # 如果想使用 OpenAI API，取消下面这行的注释
    # process_text_files(input_directory, output_directory, "openai") 