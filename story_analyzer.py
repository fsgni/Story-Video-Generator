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
        self.model = "gpt-4o-mini" # 必须使用 gpt-4o-mini 模型 不得擅自修改
        self.core_elements = {}
        self.input_file = None
        self.story_era = None  # 存储分析出的时代背景
        self.story_location = None  # 存储分析出的地点
    
    def analyze_story(self, story_text: str, input_file: str) -> Dict:
        """分析整个故事，提取核心元素和时代背景"""
        self.input_file = input_file
        
        analysis_prompt = """
        Analyze this story and extract the following elements in JSON format:
        {
            "setting": {
                "culture": "cultural background",
                "location": "specific location",
                "era": "specific historical period",
                "style": "overall visual style"
            },
            "characters": {
                "character_name": {
                    "appearance": "visual description",
                    "role": "character role",
                    "voice_type": "child/adult/elderly",
                    "gender": "male/female"
                }
            }
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个精确的文化和历史分析器，能识别和尊重不同文化的元素。"},
                    {"role": "user", "content": analysis_prompt + "\n" + story_text}
                ]
            )
            
            # 解析响应
            analysis_result = json.loads(response.choices[0].message.content)
            
            # 确保返回基本结构
            self.core_elements = {
                "setting": {
                    "culture": analysis_result.get("setting", {}).get("culture", "Unknown Culture"),
                    "era": analysis_result.get("setting", {}).get("era", "Unknown Era"),
                    "style": analysis_result.get("setting", {}).get("style", "Classical Style")
                },
                "characters": analysis_result.get("characters", {}),
                "cultural_elements": analysis_result.get("cultural_elements", {}),
                "narration": analysis_result.get("narration", {})
            }
            
            # 添加语音映射
            if "characters" in analysis_result:
                voice_mapping = self._assign_voices(analysis_result["characters"])
            else:
                voice_mapping = {"narrator": 8}
            
            self.core_elements["voice_mapping"] = voice_mapping
            
            # 保存时代背景信息
            setting = analysis_result.get("setting", {})
            self.story_era = setting.get("era", "Classical Period")
            self.story_location = setting.get("location", "Ancient China")
            
            return self.core_elements
            
        except Exception as e:
            print(f"分析故事时出错: {e}")
            self.story_era = "Classical Period"
            self.story_location = "Ancient China"
            # 提供默认值而不是空对象
            self.core_elements = {
                "setting": {
                    "culture": "Classical Culture",
                    "era": "Classical Period",
                    "style": "Classical Style"
                },
                "characters": {},
                "cultural_elements": {},
                "narration": {"tone": "neutral"},
                "voice_mapping": {"narrator": 8}
            }
            return self.core_elements
    
    def _assign_voices(self, characters: Dict) -> Dict:
        """为角色分配合适的 VOICEVOX 语音ID"""
        voice_mapping = {
            "narrator": 8,  # 默认旁白使用 8 号声音
        }
        
        # VOICEVOX 角色声音映射
        voice_types = {
            "child_female": [3, 4],      # 儿童女声
            "child_male": [2],           # 儿童男声
            "adult_female": [7, 9, 14],  # 成年女声
            "adult_male": [11, 12, 13],  # 成年男声
            "elderly_female": [16],      # 年长女声
            "elderly_male": [17]         # 年长男声
        }
        
        used_voices = set([8])  # 记录已使用的语音ID
        
        for char_name, char_info in characters.items():
            # 根据角色特征选择合适的声音类型
            age = "adult"
            if "voice_type" in char_info:
                if "child" in char_info["voice_type"].lower():
                    age = "child"
                elif "elderly" in char_info["voice_type"].lower():
                    age = "elderly"
            
            gender = char_info.get("gender", "female").lower()
            voice_type = f"{age}_{gender}"
            
            # 从可用声音中选择未使用的声音
            available_voices = voice_types.get(voice_type, [])
            for voice_id in available_voices:
                if voice_id not in used_voices:
                    voice_mapping[char_name] = voice_id
                    used_voices.add(voice_id)
                    break
            
            # 如果没有找到合适的声音，使用默认声音
            if char_name not in voice_mapping:
                voice_mapping[char_name] = 8
        
        return voice_mapping
    
    def generate_scene_prompt(self, sentences: List[str]) -> str:
        """生成场景提示词，使用统一的时代背景"""
        if not self.story_era:
            print("警告：需要先分析故事背景")
            return "error: story not analyzed"

        context = "\n".join(sentences)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"""
                        Create scene descriptions in English only.
                        Use this exact location and era for all scenes:
                        [{self.story_location}, {self.story_era}]
                        
                        Format must be:
                        [{self.story_location}, {self.story_era}], [Character details], [Action/Expression], [Environment]
                    """},
                    {"role": "user", "content": context}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            scene = response.choices[0].message.content.strip()
            return f"{scene}, masterpiece, best quality, photorealistic, cinematic lighting, detailed, 8k uhd"
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
    
    def identify_speakers(self, text: str) -> Dict[str, str]:
        """识别文本中的说话者和对话内容"""
        prompt = """
        分析以下文本，识别每句话的说话者。返回 JSON 格式：
        {
            "sentences": [
                {
                    "text": "原文内容",
                    "speaker": "说话者名称（对于非对话使用 narrator）",
                    "type": "dialogue/narration"
                }
            ]
        }
        注意：
        1. 「」或『』中的内容为对话
        2. 根据上下文判断说话者
        3. 非对话部分的说话者为 narrator
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专注于分析对话和说话者的分析器。"},
                    {"role": "user", "content": prompt + "\n" + text}
                ]
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"识别说话者时出错: {e}")
            return {"sentences": [{"text": text, "speaker": "narrator", "type": "narration"}]}

