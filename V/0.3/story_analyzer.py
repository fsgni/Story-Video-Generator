from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from pathlib import Path

class StoryAnalyzer:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.chunk_size = 2000
        self.model = "gpt-4o-mini"  # 严格使用 gpt-4o-mini
        # 存储角色和场景特征
        self.characters = {}
        self.scene_types = {}
    
    def analyze_story(self, story_text: str) -> Dict:
        """分析整个故事，提取角色和场景信息"""
        analysis_prompt = """
        分析这个故事，返回JSON：
        {
            "characters": {
                "角色名": {
                    "appearance": "外貌特征（英文）",
                    "personality": "性格特征（英文）",
                    "role": "角色身份（英文）"
                }
            },
            "scene_types": {
                "场景类型": {
                    "description": "场景描述（英文）",
                    "elements": ["关键元素1", "关键元素2"]
                }
            }
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "返回JSON格式分析"},
                    {"role": "user", "content": analysis_prompt + "\n" + story_text}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            story_analysis = json.loads(content)
            
            # 保存角色和场景特征
            self.characters = story_analysis["characters"]
            self.scene_types = story_analysis["scene_types"]
            
            return story_analysis
            
        except Exception as e:
            print(f"分析故事时出错: {e}")
            return {"characters": {}, "scene_types": {}}
    
    def generate_scene_prompt(self, sentences: List[str]) -> str:
        """根据上下文生成场景提示词"""
        context = "\n".join(sentences)
        
        prompt = f"""
        基于这些句子生成场景描述：
        {context}
        
        可用的角色描述：
        {json.dumps(self.characters, ensure_ascii=False, indent=2)}
        
        可用的场景类型：
        {json.dumps(self.scene_types, ensure_ascii=False, indent=2)}
        
        请生成一个详细的英文场景描述，包括：
        1. 出现的角色及其状态
        2. 场景环境细节
        3. 关键动作或事件
        4. 氛围和光线
        
        不要包含风格相关的描述。
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "生成简洁的英文场景描述"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"生成场景描述时出错: {e}")
            return "scene with characters"
    
    def identify_key_scenes(self, sentences: List[str]) -> List[Dict]:
        """识别需要生成图像的关键场景"""
        try:
            key_scenes = []
            current_scene = None
            current_start_time = 0.0
            
            for i in range(0, len(sentences)):
                sentence = sentences[i]
                duration = self.get_sentence_duration(sentence)
                
                if current_scene is None:
                    current_scene = {
                        "scene_id": len(key_scenes) + 1,
                        "start_index": i,
                        "sentences": [sentence],
                        "duration": duration,
                        "start_time": current_start_time,
                        "end_time": current_start_time + duration,
                        "image_file": f"scene_{len(key_scenes) + 1:03d}.png"
                    }
                elif current_scene["duration"] + duration <= 10:
                    current_scene["sentences"].append(sentence)
                    current_scene["duration"] += duration
                    current_scene["end_time"] = current_scene["start_time"] + current_scene["duration"]
                else:
                    # 结束当前场景
                    current_scene["end_index"] = i - 1
                    current_scene["prompt"] = self.generate_scene_prompt(current_scene["sentences"])
                    key_scenes.append(current_scene)
                    
                    # 开始新场景
                    current_start_time = current_scene["end_time"]
                    current_scene = {
                        "scene_id": len(key_scenes) + 1,
                        "start_index": i,
                        "sentences": [sentence],
                        "duration": duration,
                        "start_time": current_start_time,
                        "end_time": current_start_time + duration,
                        "image_file": f"scene_{len(key_scenes) + 1:03d}.png"
                    }
            
            # 处理最后一个场景
            if current_scene:
                current_scene["end_index"] = len(sentences) - 1
                current_scene["prompt"] = self.generate_scene_prompt(current_scene["sentences"])
                key_scenes.append(current_scene)
            
            return key_scenes
            
        except Exception as e:
            print(f"识别关键场景时出错: {e}")
            return []
    
    def get_sentence_duration(self, sentence: str) -> float:
        """获取句子的音频时长"""
        # 从音频信息文件中读取时长
        audio_info_file = "output/audio/お菓子の森の秘密星に願いを込めてなど_audio_info.json"
        try:
            with open(audio_info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            
            # 查找对应的音频信息
            for audio in info['audio_files']:
                if audio['sentence'] == sentence:
                    return audio['duration']
            
            print(f"未找到句子的时长信息: {sentence}")
            return 2.0  # 默认时长
        except Exception as e:
            print(f"读取音频信息时出错: {e}")
            return 2.0  # 默认时长
    
    def generate_final_prompts(self, key_scenes: List[Dict]) -> List[str]:
        """生成最终的图像提示词"""
        prompts = []
        
        for scene in key_scenes:
            prompt = scene['prompt']
            prompts.append(prompt)
        
        return prompts

def test_story_analysis():
    """测试故事分析功能"""
    print("开始分析故事...")
    analyzer = StoryAnalyzer()
    
    # 读取故事文本
    input_file = "output_texts/お菓子の森の秘密星に願いを込めてなど.txt"
    print(f"读取文件: {input_file}")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            story_text = f.read()
        print(f"成功读取文件，长度: {len(story_text)} 字符")
    except Exception as e:
        print(f"读取文件失败: {e}")
        return
    
    # 1. 分析故事
    print("\n1. 开始分析故事结构...")
    story_analysis = analyzer.analyze_story(story_text)
    print("故事分析结果:")
    print(json.dumps(story_analysis, ensure_ascii=False, indent=2))
    
    # 2. 读取分句后的文本
    print("\n2. 读取分句...")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            sentences = [line.strip() for line in f if line.strip()]
        print(f"读取到 {len(sentences)} 个句子")
    except Exception as e:
        print(f"读取分句失败: {e}")
        return
    
    # 3. 识别关键场景
    print("\n3. 识别关键场景...")
    key_scenes = analyzer.identify_key_scenes(sentences)
    print("关键场景:")
    print(json.dumps(key_scenes, ensure_ascii=False, indent=2))
    
    # 4. 生成最终提示词
    print("\n4. 生成最终提示词...")
    prompts = analyzer.generate_final_prompts(key_scenes)
    
    # 保存结果
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 保存分析结果
    with open(output_dir / "story_analysis.json", "w", encoding="utf-8") as f:
        json.dump(story_analysis, f, ensure_ascii=False, indent=2)
    
    # 保存关键场景信息
    with open(output_dir / "key_scenes.json", "w", encoding="utf-8") as f:
        json.dump(key_scenes, f, ensure_ascii=False, indent=2)
    
    # 保存提示词
    with open(output_dir / "image_prompts.txt", "w", encoding="utf-8") as f:
        for i, prompt in enumerate(prompts):
            f.write(f"Scene {i+1}:\n{prompt}\n\n")
    
    print("\n处理完成！结果已保存到 output 目录")
    return story_analysis, key_scenes, prompts

if __name__ == "__main__":
    test_story_analysis() 