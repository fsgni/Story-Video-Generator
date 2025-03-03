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
        You are tasked with analyzing a story and extracting key elements.
        
        Analyze the following story and extract these elements in valid JSON format:
        {
            "setting": {
                "culture": "the specific cultural background of the story",
                "location": "the specific location where the story takes place",
                "era": "the specific time period or era of the story",
                "style": "the overall visual style that would suit this story"
            },
            "characters": {
                "character_name": {
                    "appearance": "brief visual description",
                    "role": "character's role in the story",
                    "voice_type": "child/adult/elderly",
                    "gender": "male/female"
                }
            }
        }
        
        Be accurate and specific. If the story doesn't explicitly mention certain elements, make reasonable inferences based on the context.
        Your response must be ONLY valid JSON without any explanations or apologies.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise cultural and historical analyzer that can identify elements from any culture or time period. Always return valid JSON."},
                    {"role": "user", "content": analysis_prompt + "\n\nSTORY TEXT:\n" + story_text}
                ],
                response_format={"type": "json_object"}  # 强制返回JSON格式
            )
            
            # 解析响应
            response_content = response.choices[0].message.content
            print(f"GPT Response: {response_content}")
            
            try:
                analysis_result = json.loads(response_content)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                print(f"原始响应: {response_content}")
                # 尝试修复常见的JSON错误
                fixed_content = response_content.replace("'", "\"")
                try:
                    analysis_result = json.loads(fixed_content)
                except:
                    # 如果仍然失败，使用默认值
                    analysis_result = {
                        "setting": {
                            "culture": "Universal",
                            "location": "Story World",
                            "era": "Story Time",
                            "style": "Realistic"
                        },
                        "characters": {}
                    }
            
            # 确保返回基本结构
            self.core_elements = {
                "setting": {
                    "culture": analysis_result.get("setting", {}).get("culture", "Universal"),
                    "era": analysis_result.get("setting", {}).get("era", "Story Time"),
                    "style": analysis_result.get("setting", {}).get("style", "Realistic")
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
            self.story_era = setting.get("era", "Story Time")
            self.story_location = setting.get("location", "Story World")
            
            print(f"分析结果 - 地点: {self.story_location}, 时代: {self.story_era}")
            
            return self.core_elements
            
        except Exception as e:
            print(f"分析故事时出错: {e}")
            import traceback
            traceback.print_exc()
            
            # 使用通用的默认值
            self.story_era = "Story Time"
            self.story_location = "Story World"
            # 提供默认值而不是空对象
            self.core_elements = {
                "setting": {
                    "culture": "Universal",
                    "era": "Story Time",
                    "style": "Realistic"
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
            prompt = f"""
            Create a detailed visual scene description based on this text:
            
            "{context}"
            
            Your description should be set in {self.story_location} during {self.story_era}.
            
            Format your response as a single paragraph with this structure:
            [Setting], [Character details], [Action/Expression], [Environment details]
            
            Your response must be a creative scene description only, without any explanations, apologies, or refusals.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative scene description generator that can visualize any setting or time period without limitations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            scene = response.choices[0].message.content.strip()
            
            # 检查是否包含拒绝或道歉的词语
            refusal_phrases = ["I'm sorry", "I cannot", "I apologize", "I'm unable", "I can only"]
            if any(phrase in scene for phrase in refusal_phrases):
                print(f"检测到拒绝回应: {scene}")
                # 创建一个通用的场景描述
                scene = f"[{self.story_location}, {self.story_era}], [Characters from the story], [Engaged in meaningful interaction], [In a detailed environment that reflects the story's setting]"
            
            return f"{scene}, masterpiece, best quality,"
        except Exception as e:
            print(f"生成场景描述时出错: {e}")
            # 返回一个通用的场景描述
            return f"[{self.story_location}, {self.story_era}], detailed scene, masterpiece, best quality,"
    
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

