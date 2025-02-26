import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict
import time

class PromptGenerator:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.chunk_size = 20

    def merge_related_sentences(self, sentences: List[str]) -> List[List[str]]:
        """合并相关的句子为一个场景"""
        merged_scenes = []
        current_scene = []
        
        for sentence in sentences:
            # 如果是新场景的开始（通过某些标记判断）
            if (not current_scene or 
                sentence.startswith('「') or  # 对话开始
                sentence.endswith('。') or    # 句子结束
                len(current_scene) >= 3):     # 最多合并3句
                if current_scene:
                    merged_scenes.append(current_scene)
                current_scene = [sentence]
            else:
                # 继续添加到当前场景
                current_scene.append(sentence)
        
        # 添加最后一个场景
        if current_scene:
            merged_scenes.append(current_scene)
        
        return merged_scenes

    def generate_prompts_for_story(self, story_name: str, sentences: List[str]) -> List[str]:
        """为整个故事生成连贯的提示词序列"""
        # 首先合并相关句子
        merged_scenes = self.merge_related_sentences(sentences)
        all_prompts = []
        
        # 处理每个场景块
        for i in range(0, len(merged_scenes), self.chunk_size):
            chunk = merged_scenes[i:i + self.chunk_size]
            try:
                # 为每个场景块生成提示词
                story_prompt = f"""
                You are a professional prompt engineer for Stable Diffusion. Generate image prompts for these story scenes.
                Each scene might contain multiple sentences that describe the same moment.

                STRICT RULES:
                1. Output ONLY English prompts
                2. Generate EXACTLY ONE prompt per scene group
                3. Format: <visual description>, anime style, high quality, soft lighting
                4. NO Japanese text
                5. NO scene numbers
                6. NO explanations
                7. NO empty lines
                8. Each prompt must be unique and specific to its scene
                9. Combine all sentences in each scene group into one cohesive visual description

                Example format:
                young girl walking in magical forest with glowing butterflies, anime style, high quality, soft lighting
                crystal lake reflecting starry sky with cherry blossoms falling, anime style, high quality, soft lighting

                Input scenes:
                {[' '.join(scene) for scene in chunk]}

                Required prompt count: {len(chunk)}
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": story_prompt}
                    ],
                    temperature=0.6,
                    max_tokens=4000,
                    presence_penalty=0.2,  # 稍微增加以减少重复
                    frequency_penalty=0.2
                )
                
                result = response.choices[0].message.content.strip()
                
                if not result:
                    raise Exception("Empty response from API")
                
                # 处理返回的提示词，过滤掉非英文提示词和重复提示词
                chunk_prompts = []
                used_prompts = set()  # 用于检测重复
                for p in result.split('\n'):
                    p = p.strip()
                    # 只保留有效的英文提示词且不重复
                    if (p and "anime style" in p and 
                        not any(ord(c) > 127 for c in p) and 
                        p not in used_prompts):
                        chunk_prompts.append(p)
                        used_prompts.add(p)
                
                # 确保提示词数量匹配
                if len(chunk_prompts) < len(chunk):
                    print(f"警告：块 {i//self.chunk_size + 1} 提示词数量不足")
                    # 为缺失的场景生成更有意义的提示词
                    for scene_sentences in chunk[len(chunk_prompts):]:
                        # 使用场景中的第一句话作为提示词基础
                        scene_text = ' '.join(scene_sentences)[:50]
                        new_prompt = f"emotional scene with {scene_text.lower()}..., anime style, high quality, soft lighting"
                        chunk_prompts.append(new_prompt)
                
                all_prompts.extend(chunk_prompts[:len(chunk)])
                
            except Exception as e:
                print(f"处理块 {i//self.chunk_size + 1} 时出错: {e}")
                # 生成更有意义的后备提示词
                for scene_sentences in chunk:
                    scene_text = ' '.join(scene_sentences)[:50]
                    all_prompts.append(f"emotional anime scene with {scene_text.lower()}..., high quality, soft lighting")
        
        return all_prompts

def save_prompts_to_file(merged_scenes: List[List[str]], prompts: List[str], output_file: str):
    """保存原文和提示词到文件"""
    with open(output_file, "w", encoding="utf-8") as f:
        for i, (scene_sentences, prompt) in enumerate(zip(merged_scenes, prompts), 1):
            f.write(f"Scene {i}:\n")
            f.write("原文:\n")
            for sentence in scene_sentences:
                f.write(f"  {sentence}\n")
            f.write(f"Prompt: {prompt}\n")
            f.write("-" * 50 + "\n\n")

def generate_images(text_file: str, output_dir: str) -> List[str]:
    """为整个故事生成图像"""
    prompt_generator = PromptGenerator()
    
    # 读取文本文件
    with open(text_file, "r", encoding="utf-8") as f:
        sentences = [line.strip() for line in f if line.strip()]
    
    # 获取故事名称
    story_name = os.path.basename(text_file)
    
    # 合并句子并生成提示词
    merged_scenes = prompt_generator.merge_related_sentences(sentences)
    prompts = prompt_generator.generate_prompts_for_story(story_name, sentences)
    
    # 保存提示词到文件
    output_txt = os.path.join(output_dir, f"{os.path.splitext(story_name)[0]}_prompts.txt")
    save_prompts_to_file(merged_scenes, prompts, output_txt)
    
    # 生成图像文件路径（不输出到终端）
    output_files = []
    for i, _ in enumerate(prompts):
        output_file = os.path.join(output_dir, f"image_{i:03d}.png")
        output_files.append(output_file)
    
    return output_files 