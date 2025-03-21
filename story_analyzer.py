from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from pathlib import Path
import re
import sys
import time
import random
import string
import locale

# 设置系统编码为UTF-8，解决Windows命令行的编码问题
if sys.stdout.encoding != 'utf-8':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    elif hasattr(sys.stdout, 'buffer'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='backslashreplace')

class StoryAnalyzer:
    def __init__(self):
        """初始化故事分析器"""
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-mini" # 必须使用 gpt-4o-mini 模型 不得擅自修改
        self.core_elements = {}
        self.input_file = None
        self.story_era = None  # 存储分析出的时代背景
        self.story_location = None  # 存储分析出的地点
        self.segment_analyses = []  # 存储分段分析结果
        
        # 添加一个列表，用于检测错误的文化背景
        self.incorrect_cultures = ["Japanese", "Chinese", "Korean", "Asian"]
    
    def analyze_story(self, story_text: str, input_file: str) -> Dict:
        """分析故事文本，提取关键信息"""
        self.input_file = input_file
        
        # 检查文本长度，决定是否使用分段处理
        if len(story_text) > 2000:
            print(f"故事较长 ({len(story_text)} 字符)，使用分段处理...")
            analysis_result = self.analyze_story_in_segments(story_text)
        else:
            print(f"故事较短 ({len(story_text)} 字符)，使用单次处理...")
            analysis_result = self._analyze_single_segment(story_text)
        
        # 保存全局文化背景信息，确保所有场景使用一致的背景
        if 'setting' in analysis_result:
            self.global_culture = analysis_result['setting'].get('culture', 'Universal')
            self.global_location = analysis_result['setting'].get('location', 'Story World')
            self.global_era = analysis_result['setting'].get('era', 'Story Time')
            self.global_style = analysis_result['setting'].get('style', 'Realistic')
            
            print(f"全局文化背景: {self.global_culture}")
            print(f"全局地点: {self.global_location}")
            print(f"全局时代: {self.global_era}")
            print(f"全局风格: {self.global_style}")
        
        return analysis_result
    
    def analyze_story_in_segments(self, story_text: str, max_segment_length: int = 800) -> Dict:
        """分段分析故事，处理长文本"""
        print("故事较长，执行分段分析...")
        
        # 将故事分成段落
        paragraphs = story_text.split('\n\n')
        segments = []
        current_segment = ""
        
        for paragraph in paragraphs:
            if len(current_segment) + len(paragraph) < max_segment_length:
                current_segment += paragraph + "\n\n"
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = paragraph + "\n\n"
        
        if current_segment:
            segments.append(current_segment.strip())
        
        print(f"故事被分为 {len(segments)} 个段落进行分析")
        
        # 分析每个段落
        self.segment_analyses = []
        segment_settings = []
        all_characters = {}
        
        for i, segment in enumerate(segments):
            print(f"分析段落 {i+1}/{len(segments)}...")
            segment_result = self._analyze_single_segment(segment, is_segment=True)
            self.segment_analyses.append(segment_result)
            
            # 收集设置信息
            if "setting" in segment_result:
                segment_settings.append(segment_result["setting"])
            
            # 收集角色信息
            if "characters" in segment_result:
                for char_name, char_info in segment_result["characters"].items():
                    if char_name not in all_characters:
                        all_characters[char_name] = char_info
        
        # 整合分析结果
        return self._consolidate_segment_analyses(segment_settings, all_characters)
    
    def _analyze_single_segment(self, text: str, is_segment: bool = False) -> Dict:
        """分析单个文本段落"""
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
                    "gender": "male/female"
                }
            }
        }
        """
        
        if is_segment:
            analysis_prompt += """
            Note: You are analyzing a segment of a larger story, so focus on what's present in this segment.
            If certain elements are unclear from this segment alone, make your best guess based on context.
            """
        
        analysis_prompt += """
        Be accurate and specific. If the story doesn't explicitly mention certain elements, make reasonable inferences based on the context.
        Your response must be ONLY valid JSON without any explanations or apologies.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise cultural and historical analyzer that can identify elements from any culture or time period. Always return valid JSON."},
                    {"role": "user", "content": analysis_prompt + "\n\nSTORY TEXT:\n" + text}
                ],
                response_format={"type": "json_object"}  # 强制返回JSON格式
            )
            
            # 解析响应
            response_content = response.choices[0].message.content
            
            # 修改print语句，确保能够处理所有Unicode字符
            try:
                print(f"GPT Response: {response_content}")
            except UnicodeEncodeError:
                print("GPT Response: [包含无法显示的Unicode字符]")
            
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
            
            # 如果不是分段分析，则设置核心元素
            if not is_segment:
                self._set_core_elements(analysis_result)
            
            # 添加调试信息，打印分析结果中的文化背景
            if 'setting' in analysis_result:
                print(f"分析结果中的文化背景: {analysis_result['setting'].get('culture', '未指定')}")
                print(f"分析结果中的地点: {analysis_result['setting'].get('location', '未指定')}")
                print(f"分析结果中的时代: {analysis_result['setting'].get('era', '未指定')}")
            
            return analysis_result
            
        except Exception as e:
            print(f"分析故事段落时出错: {e}")
            import traceback
            traceback.print_exc()
            
            # 返回默认值
            return {
                "setting": {
                    "culture": "Universal",
                    "location": "Story World",
                    "era": "Story Time",
                    "style": "Realistic"
                },
                "characters": {}
            }
    
    def _consolidate_segment_analyses(self, segment_settings: List[Dict], all_characters: Dict) -> Dict:
        """整合多个段落的分析结果"""
        # 合并设置信息，优先使用出现频率最高的值
        culture_counts = {}
        location_counts = {}
        era_counts = {}
        style_counts = {}
        
        for setting in segment_settings:
            culture = setting.get("culture", "Universal")
            location = setting.get("location", "Story World")
            era = setting.get("era", "Story Time")
            style = setting.get("style", "Realistic")
            
            culture_counts[culture] = culture_counts.get(culture, 0) + 1
            location_counts[location] = location_counts.get(location, 0) + 1
            era_counts[era] = era_counts.get(era, 0) + 1
            style_counts[style] = style_counts.get(style, 0) + 1
        
        # 选择出现频率最高的值
        culture = max(culture_counts.items(), key=lambda x: x[1])[0] if culture_counts else "Universal"
        location = max(location_counts.items(), key=lambda x: x[1])[0] if location_counts else "Story World"
        era = max(era_counts.items(), key=lambda x: x[1])[0] if era_counts else "Story Time"
        style = max(style_counts.items(), key=lambda x: x[1])[0] if style_counts else "Realistic"
        
        # 创建整合的分析结果
        consolidated_result = {
            "setting": {
                "culture": culture,
                "location": location,
                "era": era,
                "style": style
            },
            "characters": all_characters,
            "cultural_elements": {},
            "narration": {"tone": "neutral"}
        }
        
        # 存储设置信息
        self.story_era = era
        self.story_location = location
        
        # 设置核心元素
        self._set_core_elements(consolidated_result)
        
        print(f"整合分析结果 - 文化: {culture}, 地点: {location}, 时代: {era}, 风格: {style}")
        print(f"识别到的角色数量: {len(all_characters)}")
        
        return consolidated_result
    
    def _set_core_elements(self, analysis_result: Dict):
        """设置核心元素和背景信息"""
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
        
        # 保存时代背景信息
        setting = analysis_result.get("setting", {})
        self.story_era = setting.get("era", "Story Time")
        self.story_location = setting.get("location", "Story World")
        
        print(f"分析结果 - 地点: {self.story_location}, 时代: {self.story_era}")
    
    def generate_scene_prompt(self, sentences: List[str]) -> str:
        """生成场景提示词，使用统一的时代背景和风格，确保所有提示词都是英语，并且简洁有效"""
        if not self.story_era or not hasattr(self, 'core_elements'):
            print("警告：需要先分析故事背景")
            return "error: story not analyzed"

        # 优先使用全局文化背景信息
        culture = getattr(self, 'global_culture', self.core_elements.get("setting", {}).get("culture", "Universal"))
        location = getattr(self, 'global_location', self.story_location or "Story World")
        era = getattr(self, 'global_era', self.story_era or "Story Time")
        style = getattr(self, 'global_style', self.core_elements.get("setting", {}).get("style", "Realistic"))
        
        print(f"使用全局文化背景生成提示词: {culture}, {location}, {era}")
        
        # 获取人物特征信息
        characters = self.core_elements.get("characters", {})
        character_descriptions = []
        
        # 从句子中尝试识别出现的角色
        context = "\n".join(sentences)
        mentioned_characters = []
        
        for char_name in characters.keys():
            if char_name.lower() in context.lower():
                mentioned_characters.append(char_name)
        
        # 为提到的角色添加描述
        for char_name in mentioned_characters:
            char_info = characters.get(char_name, {})
            appearance = char_info.get("appearance", "")
            role = char_info.get("role", "")
            gender = char_info.get("gender", "")
            
            # 构建更结构化的角色描述
            char_desc_parts = []
            if role:
                char_desc_parts.append(f"role: {role}")
            if appearance:
                char_desc_parts.append(f"appearance: {appearance}")
            if gender:
                char_desc_parts.append(f"gender: {gender}")
                
            if char_desc_parts:
                char_desc = f"{char_name}: {', '.join(char_desc_parts)}"
                character_descriptions.append(char_desc)
        
        # 将角色描述合并为一个字符串
        character_info = "; ".join(character_descriptions)
        
        context = "\n".join(sentences)
        
        try:
            # 首先确保所有内容都是英语
            translation_prompt = f"""
            Translate the following text to English if it's not already in English.
            For culture, location, era, and style terms, provide the most appropriate English equivalent.
            
            Culture: {culture}
            Location: {location}
            Era: {era}
            Style: {style}
            Context: {context}
            Character Info: {character_info}
            
            Format your response as JSON:
            {{
                "culture": "English translation of culture",
                "location": "English translation of location",
                "era": "English translation of era",
                "style": "English translation of style",
                "context": "English translation of context",
                "character_info": "English translation of character_info"
            }}
            """
            
            translation_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise translator that converts non-English text to English while preserving meaning."},
                    {"role": "user", "content": translation_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                translated_data = json.loads(translation_response.choices[0].message.content)
                culture = translated_data.get("culture", culture)
                location = translated_data.get("location", location)
                era = translated_data.get("era", era)
                style = translated_data.get("style", style)
                context = translated_data.get("context", context)
                character_info = translated_data.get("character_info", character_info)
                
                print(f"翻译后的背景信息 - 文化: {culture}, 地点: {location}, 时代: {era}, 风格: {style}")
                if character_info:
                    print(f"翻译后的角色信息: {character_info}")
            except Exception as e:
                print(f"翻译JSON解析错误: {e}")
                # 继续使用原始值
            
            # 使用翻译后的英语内容生成场景描述 - 修改为更具体的提示词
            prompt = f"""
            Create a DETAILED visual scene description based on this text:
            
            "{context}"
            
            Your description should reflect:
            - Culture: {culture}
            - Location: {location}
            - Time period: {era}
            - Visual style: {style}
            
            Character information to include (DO NOT use character names, only describe their roles and appearances):
            {character_info}
            
            FOCUS ON THESE ELEMENTS BASED ON THE CONTEXT:
            1. GRAND SCENES - For large-scale events, battles, or crowd scenes, focus on the overall atmosphere, scale, and environment (e.g., "vast battlefield with thousands of soldiers", "crowded marketplace bustling with activity")
            2. LANDSCAPE & ENVIRONMENT - Describe natural or architectural elements that define the scene (e.g., "towering castle against stormy sky", "sunlight filtering through ancient forest")
            3. ATMOSPHERIC ELEMENTS - Include lighting, weather, time of day that create mood (e.g., "golden sunset casting long shadows", "misty morning shrouding the mountains")
            4. SPECIFIC CHARACTER EXPRESSIONS - When focusing on individuals, include detailed facial expressions (e.g., "determined gaze", "furrowed brow")
            5. PRECISE BODY LANGUAGE - For character-focused scenes, describe exact poses and gestures (e.g., "hand firmly gripping sword")
            6. DYNAMIC ACTIONS - Show movement and energy appropriate to the scene (e.g., "armies clashing on blood-soaked field", "dancers twirling across marble floor")
            
            Format as: "[Setting/Environment], [Scale and Atmosphere], [Character elements or crowd dynamics if relevant]"
            
            Use 40-50 words maximum. Focus on visually striking and emotionally resonant elements.
            Your response must be in English only.
            IMPORTANT: DO NOT include any character names in your description.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a scene description generator that balances grand scenes with character details. Adapt your focus based on the context - for battles, crowds, or landscapes, emphasize the environment and scale; for intimate moments, focus on character details. Always respond in English only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            scene = response.choices[0].message.content.strip()
            
            # 检查是否包含拒绝或道歉的词语
            refusal_phrases = ["I'm sorry", "I cannot", "I apologize", "I'm unable", "I can only"]
            if any(phrase in scene for phrase in refusal_phrases):
                print(f"检测到拒绝回应: {scene}")
                # 创建一个简洁的通用场景描述
                scene = f"{location} during {era}, {culture} style"
            
            # 构建最终提示词，明确包含背景信息和人物特征，确保全部是英语，但保留更多细节
            # 移除可能导致AI模型混淆的不必要词汇
            scene = re.sub(r'\[|\]|\(|\)', '', scene)  # 移除括号
            scene = re.sub(r',\s*,', ',', scene)  # 移除连续逗号
            scene = re.sub(r'\s+', ' ', scene).strip()  # 规范化空格
            
            # 提取人物特征关键词，用于增强提示词
            character_keywords = ""
            if character_info:
                # 从角色描述中提取关键词
                char_keywords = []
                for desc in character_descriptions:
                    parts = desc.split(":")
                    if len(parts) > 1:
                        # 提取角色特征，不包含角色名
                        char_details = parts[1].strip()
                        # 提取角色的角色类型（如将军、士兵等）
                        role_match = re.search(r'role:\s*([^,]+)', char_details, re.IGNORECASE)
                        role_type = ""
                        if role_match:
                            role_type = role_match.group(1).strip()
                        
                        # 提取最重要的外貌特征词
                        appearance_details = re.sub(r'role:[^,]+,?', '', char_details, flags=re.IGNORECASE).strip()
                        if appearance_details:
                            if role_type:
                                char_keywords.append(f"{role_type} with {appearance_details}")
                            else:
                                char_keywords.append(appearance_details)
                
                if char_keywords:
                    character_keywords = ", ".join(char_keywords)
            
            # 生成详细的最终提示词，包含人物特征但不包含人名
            if character_keywords:
                # 移除风格词汇，让full_process.py控制风格
                final_prompt = f"{culture}, {location}, {era}, {scene}, {character_keywords}"
            else:
                # 移除风格词汇，让full_process.py控制风格
                final_prompt = f"{culture}, {location}, {era}, {scene}"
            
            # 最终检查，确保不会出现错误的文化背景
            final_prompt = self._ensure_correct_culture_background(final_prompt)
            
            return final_prompt
        except Exception as e:
            print(f"生成场景描述时出错: {e}")
            # 返回一个简洁的通用场景描述
            return f"{culture}, {location}, {era}, {style} style, high quality"
    
    def generate_segment_specific_prompt(self, sentences: List[str], segment_index: int = None) -> str:
        """生成基于特定段落分析的场景提示词，为长文本故事的不同段落提供更准确、简洁的场景描述"""
        if not self.segment_analyses:
            # 如果没有分段分析结果，回退到标准方法
            return self.generate_scene_prompt(sentences)
        
        # 尝试确定句子属于哪个段落
        if segment_index is None:
            segment_index = self._find_segment_for_sentences(sentences)
        
        # 如果无法确定或超出范围，使用整合的结果
        if segment_index is None or segment_index >= len(self.segment_analyses):
            return self.generate_scene_prompt(sentences)
        
        # 使用特定段落的分析结果，但文化背景使用全局信息
        segment_analysis = self.segment_analyses[segment_index]
        
        # 强制使用全局文化背景信息
        culture = getattr(self, 'global_culture', self.core_elements.get("setting", {}).get("culture", "Universal"))
        location = getattr(self, 'global_location', self.story_location or "Story World")
        era = getattr(self, 'global_era', self.story_era or "Story Time")
        style = getattr(self, 'global_style', self.core_elements.get("setting", {}).get("style", "Realistic"))
        
        print(f"段落 {segment_index} 使用全局文化背景: {culture}, {location}, {era}")
        
        # 获取人物特征信息
        characters = segment_analysis.get("characters", {})
        character_descriptions = []
        
        # 从句子中尝试识别出现的角色
        context = "\n".join(sentences)
        mentioned_characters = []
        
        for char_name in characters.keys():
            if char_name.lower() in context.lower():
                mentioned_characters.append(char_name)
        
        # 为提到的角色添加描述
        for char_name in mentioned_characters:
            char_info = characters.get(char_name, {})
            appearance = char_info.get("appearance", "")
            role = char_info.get("role", "")
            gender = char_info.get("gender", "")
            
            # 构建更结构化的角色描述
            char_desc_parts = []
            if role:
                char_desc_parts.append(f"role: {role}")
            if appearance:
                char_desc_parts.append(f"appearance: {appearance}")
            if gender:
                char_desc_parts.append(f"gender: {gender}")
                
            if char_desc_parts:
                char_desc = f"{char_name}: {', '.join(char_desc_parts)}"
                character_descriptions.append(char_desc)
        
        # 将角色描述合并为一个字符串
        character_info = "; ".join(character_descriptions)
        
        context = "\n".join(sentences)
        
        try:
            # 翻译和生成场景描述的逻辑与standard方法相同，但生成更简洁的提示词
            translation_prompt = f"""
            Translate the following text to English if it's not already in English.
            For culture, location, era, and style terms, provide the most appropriate English equivalent.
            
            Culture: {culture}
            Location: {location}
            Era: {era}
            Style: {style}
            Context: {context}
            Character Info: {character_info}
            
            Format your response as JSON:
            {{
                "culture": "English translation of culture",
                "location": "English translation of location",
                "era": "English translation of era",
                "style": "English translation of style",
                "context": "English translation of context",
                "character_info": "English translation of character_info"
            }}
            """
            
            translation_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise translator that converts non-English text to English while preserving meaning."},
                    {"role": "user", "content": translation_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                translated_data = json.loads(translation_response.choices[0].message.content)
                culture = translated_data.get("culture", culture)
                location = translated_data.get("location", location)
                era = translated_data.get("era", era)
                style = translated_data.get("style", style)
                context = translated_data.get("context", context)
                character_info = translated_data.get("character_info", character_info)
                
                print(f"段落 {segment_index+1} 翻译后的背景信息 - 文化: {culture}, 地点: {location}, 时代: {era}, 风格: {style}")
                if character_info:
                    print(f"翻译后的角色信息: {character_info}")
            except Exception as e:
                print(f"翻译JSON解析错误: {e}")
                # 继续使用原始值
            
            prompt = f"""
            Create a DETAILED visual scene description based on this text:
            
            "{context}"
            
            Your description should reflect:
            - Culture: {culture}
            - Location: {location}
            - Time period: {era}
            - Visual style: {style}
            
            Character information to include (DO NOT use character names, only describe their roles and appearances):
            {character_info}
            
            FOCUS ON THESE ELEMENTS BASED ON THE CONTEXT:
            1. GRAND SCENES - For large-scale events, battles, or crowd scenes, focus on the overall atmosphere, scale, and environment (e.g., "vast battlefield with thousands of soldiers", "crowded marketplace bustling with activity")
            2. LANDSCAPE & ENVIRONMENT - Describe natural or architectural elements that define the scene (e.g., "towering castle against stormy sky", "sunlight filtering through ancient forest")
            3. ATMOSPHERIC ELEMENTS - Include lighting, weather, time of day that create mood (e.g., "golden sunset casting long shadows", "misty morning shrouding the mountains")
            4. SPECIFIC CHARACTER EXPRESSIONS - When focusing on individuals, include detailed facial expressions (e.g., "determined gaze", "furrowed brow")
            5. PRECISE BODY LANGUAGE - For character-focused scenes, describe exact poses and gestures (e.g., "hand firmly gripping sword")
            6. DYNAMIC ACTIONS - Show movement and energy appropriate to the scene (e.g., "armies clashing on blood-soaked field", "dancers twirling across marble floor")
            
            Format as: "[Setting/Environment], [Scale and Atmosphere], [Character elements or crowd dynamics if relevant]"
            
            Use 40-50 words maximum. Focus on visually striking and emotionally resonant elements.
            Your response must be in English only.
            IMPORTANT: DO NOT include any character names in your description.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a scene description generator that balances grand scenes with character details. Adapt your focus based on the context - for battles, crowds, or landscapes, emphasize the environment and scale; for intimate moments, focus on character details. Always respond in English only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            scene = response.choices[0].message.content.strip()
            
            if any(phrase in scene for phrase in ["I'm sorry", "I cannot", "I apologize", "I'm unable", "I can only"]):
                print(f"检测到拒绝回应: {scene}")
                scene = f"{location} during {era}, {culture} style"
            
            # 清理和简化场景描述，但保留表情、动作和人物特征的细节
            scene = re.sub(r'\[|\]|\(|\)', '', scene)  # 移除括号
            scene = re.sub(r',\s*,', ',', scene)  # 移除连续逗号
            scene = re.sub(r'\s+', ' ', scene).strip()  # 规范化空格
            
            # 提取人物特征关键词，用于增强提示词
            character_keywords = ""
            if character_info:
                # 从角色描述中提取关键词
                char_keywords = []
                for desc in character_descriptions:
                    parts = desc.split(":")
                    if len(parts) > 1:
                        # 提取角色特征，不包含角色名
                        char_details = parts[1].strip()
                        # 提取角色的角色类型（如将军、士兵等）
                        role_match = re.search(r'role:\s*([^,]+)', char_details, re.IGNORECASE)
                        role_type = ""
                        if role_match:
                            role_type = role_match.group(1).strip()
                        
                        # 提取最重要的外貌特征词
                        appearance_details = re.sub(r'role:[^,]+,?', '', char_details, flags=re.IGNORECASE).strip()
                        if appearance_details:
                            if role_type:
                                char_keywords.append(f"{role_type} with {appearance_details}")
                            else:
                                char_keywords.append(appearance_details)
                
                if char_keywords:
                    character_keywords = ", ".join(char_keywords)
            
            # 生成详细的最终提示词，包含人物特征但不包含人名
            if character_keywords:
                # 移除风格词汇，让full_process.py控制风格
                final_prompt = f"{culture}, {location}, {era}, {scene}, {character_keywords}"
            else:
                # 移除风格词汇，让full_process.py控制风格
                final_prompt = f"{culture}, {location}, {era}, {scene}"
            
            # 最终检查，确保不会出现错误的文化背景
            final_prompt = self._ensure_correct_culture_background(final_prompt)
            
            return final_prompt
        except Exception as e:
            print(f"生成段落特定场景描述时出错: {e}")
            return f"{culture}, {location}, {era}, {style} style, high quality"
    
    def _find_segment_for_sentences(self, sentences: List[str]) -> int:
        """尝试确定给定句子属于哪个段落"""
        if not self.segment_analyses:
            return None
        
        # 简单实现：返回第一个段落
        # 在实际应用中，可以实现更复杂的匹配逻辑
        return 0
    
    def identify_key_scenes(self, sentences: List[str]) -> List[Dict]:
        """识别需要生成图像的关键场景，支持分段处理"""
        try:
            key_scenes = []
            current_scene = None
            current_start_time = 0.0
            
            # 为长文本启用分段处理
            use_segments = len(self.segment_analyses) > 0
            current_segment = 0
            segment_boundaries = []
            
            # 如果使用分段，确定大致的段落边界（用于后续场景生成）
            if use_segments:
                total_sentences = len(sentences)
                sentences_per_segment = total_sentences // len(self.segment_analyses)
                for i in range(len(self.segment_analyses)):
                    start_idx = i * sentences_per_segment
                    segment_boundaries.append(start_idx)
                segment_boundaries.append(total_sentences)  # 添加结尾边界
            
            for i in range(0, len(sentences)):
                sentence = sentences[i]
                duration = self.get_sentence_duration(sentence)
                
                # 如果使用分段，检查是否到达新段落
                if use_segments and i >= segment_boundaries[min(current_segment + 1, len(segment_boundaries) - 1)]:
                    current_segment = min(current_segment + 1, len(self.segment_analyses) - 1)
                
                if current_scene is None:
                    current_scene = self._create_new_scene(i, sentence, duration, current_start_time)
                elif current_scene["duration"] + duration <= 10:
                    self._extend_current_scene(current_scene, sentence, duration)
                else:
                    # 结束当前场景
                    self._finalize_scene(current_scene, i - 1, current_segment if use_segments else None)
                    key_scenes.append(current_scene)
                    
                    # 开始新场景
                    current_start_time = current_scene["end_time"]
                    current_scene = self._create_new_scene(i, sentence, duration, current_start_time)
            
            # 处理最后一个场景
            if current_scene:
                self._finalize_scene(current_scene, len(sentences) - 1, current_segment if use_segments else None)
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
    
    def _finalize_scene(self, scene: Dict, end_index: int, segment_index: int = None):
        """完成场景处理，可选择基于段落生成提示词"""
        scene["end_index"] = end_index
        
        # 如果有段落索引，使用段落特定的提示词生成
        if segment_index is not None:
            scene["prompt"] = self.generate_segment_specific_prompt(scene["sentences"], segment_index)
        else:
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
    
    def _ensure_correct_culture_background(self, prompt: str) -> str:
        """确保提示词中不会出现错误的文化背景"""
        # 获取正确的全局文化背景
        correct_culture = getattr(self, 'global_culture', self.core_elements.get("setting", {}).get("culture", "Universal"))
        correct_location = getattr(self, 'global_location', self.story_location or "Story World")
        correct_era = getattr(self, 'global_era', self.story_era or "Story Time")
        
        # 检查是否包含错误的文化背景
        for incorrect_culture in self.incorrect_cultures:
            if incorrect_culture in prompt and incorrect_culture not in correct_culture:
                print(f"检测到错误的文化背景: {incorrect_culture}，将替换为正确的文化背景: {correct_culture}")
                # 替换错误的文化背景
                prompt = prompt.replace(f"{incorrect_culture}", f"{correct_culture}")
                # 确保地点和时代也是正确的
                if "Japan" in prompt and "Japan" not in correct_location:
                    prompt = prompt.replace("Japan", correct_location)
                if "1784" in prompt and "1784" not in correct_era:
                    prompt = prompt.replace("1784", correct_era)
        
        return prompt

