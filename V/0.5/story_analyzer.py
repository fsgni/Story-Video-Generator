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
        self.model = "gpt-4o-mini"
        self.core_elements = {}
        self.input_file = None
    
    def analyze_story(self, story_text: str, input_file: str) -> Dict:
        """分析整个故事，提取核心元素"""
        self.input_file = input_file
        analysis_prompt = """
        Analyze this story and extract visual elements. Return in JSON format:
        {
            "setting": {
                "era": "time period and cultural setting (e.g., ancient Japan, modern Tokyo)",
                "style": "overall visual style (e.g., traditional Japanese, rural countryside)"
            },
            "characters": {
                "character_name": {
                    "appearance": "specific visual details (e.g., elderly woman with white hair, wearing traditional kimono)",
                    "role": "character role"
                }
            },
            "locations": {
                "place_name": {
                    "description": "specific visual details (e.g., wooden house with thatched roof, surrounded by pine trees)",
                    "atmosphere": "visual mood (e.g., peaceful countryside, busy marketplace)"
                }
            }
        }
        Note: All descriptions must be in English and focus on visual elements.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专注于提取故事核心元素的分析器。必须返回有效的JSON格式。"},
                    {"role": "user", "content": analysis_prompt + "\n" + story_text}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            print(f"API返回内容: {content}")  # 添加调试输出
            
            try:
                self.core_elements = json.loads(content)
                return self.core_elements
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                print(f"尝试解析的内容: {content}")
                # 如果解析失败，尝试提取可能的JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        self.core_elements = json.loads(json_match.group())
                        return self.core_elements
                    except:
                        pass
                return {"setting": {}, "characters": {}, "locations": {}}
            
        except Exception as e:
            print(f"API调用错误: {e}")
            return {"setting": {}, "characters": {}, "locations": {}}
    
    def generate_scene_prompt(self, sentences: List[str]) -> str:
        """根据上下文和核心元素生成场景提示词"""
        context = "\n".join(sentences)
        
        prompt = f"""
        Generate a detailed visual description in English for this scene.

        Story setting:
        {json.dumps(self.core_elements.get('setting', {}), ensure_ascii=False, indent=2)}

        Available characters:
        {json.dumps(self.core_elements.get('characters', {}), ensure_ascii=False, indent=2)}

        Available locations:
        {json.dumps(self.core_elements.get('locations', {}), ensure_ascii=False, indent=2)}

        Current text:
        {context}

        Requirements:
        1. Start with the time period/setting (e.g., "In ancient Japan...")
        2. Include specific character details from predefined descriptions
        3. Describe the exact location and atmosphere
        4. Include current actions or events
        5. Keep all descriptions in English
        6. Focus only on what's happening in the current scene

        Format: "In [era/setting], [character with details] [specific action] in/at [detailed location]"
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an English-only scene descriptor. Never include Japanese text in your output."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"生成场景描述时出错: {e}")
            return "error generating scene description"
    
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
                    current_scene = self._create_new_scene(i, sentence, duration, current_start_time)
                elif current_scene["duration"] + duration <= 10:
                    self._extend_current_scene(current_scene, sentence, duration)
                else:
                    # 结束当前场景
                    self._finalize_scene(current_scene, i - 1)
                    key_scenes.append(current_scene)
                    
                    # 开始新场景
                    current_start_time = current_scene["end_time"]
                    current_scene = self._create_new_scene(i, sentence, duration, current_start_time)
            
            # 处理最后一个场景
            if current_scene:
                self._finalize_scene(current_scene, len(sentences) - 1)
                key_scenes.append(current_scene)
            
            return key_scenes
            
        except Exception as e:
            print(f"识别关键场景时出错: {e}")
            return []
    
    def _create_new_scene(self, index: int, sentence: str, duration: float, start_time: float) -> Dict:
        """创建新场景"""
        return {
            "scene_id": index + 1,
            "start_index": index,
            "sentences": [sentence],
            "duration": duration,
            "start_time": start_time,
            "end_time": start_time + duration,
            "image_file": f"scene_{index + 1:03d}.png"
        }
    
    def _extend_current_scene(self, scene: Dict, sentence: str, duration: float):
        """扩展当前场景"""
        scene["sentences"].append(sentence)
        scene["duration"] += duration
        scene["end_time"] = scene["start_time"] + scene["duration"]
    
    def _finalize_scene(self, scene: Dict, end_index: int):
        """完成场景处理"""
        scene["end_index"] = end_index
        scene["prompt"] = self.generate_scene_prompt(scene["sentences"])
    
    def get_sentence_duration(self, sentence: str) -> float:
        """获取句子的音频时长"""
        audio_info_file = f"output/audio/{Path(self.input_file).stem}_audio_info.json"
        try:
            with open(audio_info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            
            for audio in info['audio_files']:
                if audio['sentence'] == sentence:
                    return audio['duration']
            
            print(f"未找到句子的时长信息: {sentence}")
            return 2.0
        except Exception as e:
            print(f"读取音频信息时出错: {e}")
            return 2.0

