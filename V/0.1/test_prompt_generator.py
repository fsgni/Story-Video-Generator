from image_generator import PromptGenerator
from pathlib import Path

def test_prompt_generation():
    """测试提示词生成"""
    generator = PromptGenerator()
    
    # 从 output_texts 目录读取处理好的文本
    output_dir = Path("output_texts")
    if not output_dir.exists():
        print("找不到 output_texts 目录")
        return
        
    # 读取所有txt文件
    for txt_file in output_dir.glob("*.txt"):
        print(f"\n处理文件: {txt_file.name}")
        
        try:
            # 读取整个故事
            with open(txt_file, "r", encoding="utf-8") as f:
                sentences = [line.strip() for line in f if line.strip()]
            
            # 生成连贯的提示词序列
            prompts = generator.generate_prompts_for_story(txt_file.name, sentences)
            
            # 显示结果
            for i, (sentence, prompt) in enumerate(zip(sentences, prompts), 1):
                print(f"\n场景 {i}:")
                print(f"原文: {sentence}")
                print(f"提示词: {prompt}")
                print("-" * 50)
                
        except Exception as e:
            print(f"处理文件 {txt_file.name} 时出错: {e}")

if __name__ == "__main__":
    test_prompt_generation() 