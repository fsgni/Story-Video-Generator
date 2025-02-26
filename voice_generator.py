import requests
import json
import wave
import time
from pathlib import Path
from typing import Dict

class VoiceVoxGenerator:
    def __init__(self, host="127.0.0.1", port="50021", speaker=8):  # 默认使用 8 号角色
        self.base_url = f"http://{host}:{port}"
        self.speaker = speaker
        
        # VOICEVOX 角色列表
        self.speakers = {
            1: "四国めたん",
            2: "ずんだもん",
            3: "春日部つむぎ",
            4: "雨晴はう",
            7: "小夜/SAYO",
            8: "ナースロボ＿タイプＴ",
            9: "春歌ナナ",
            10: "波音リツ",
            11: "玄野武宏",
            12: "白上虎太郎",
            13: "青山龍星",
            14: "冥鳴ひまり",
            15: "九州そら",
            16: "もち子さん",
            17: "剣崎雌雄"
        }
    
    def list_speakers(self):
        """列出所有可用的说话人"""
        return self.speakers
    
    def set_speaker(self, speaker_id: int):
        """设置说话人"""
        if speaker_id in self.speakers:
            self.speaker = speaker_id
            return True
        return False
    
    def get_audio_query(self, text, speaker=None):
        """获取音频查询参数"""
        speaker = speaker or self.speaker
        params = {"text": text, "speaker": speaker}
        response = requests.post(f"{self.base_url}/audio_query", params=params)
        return response.json()
    
    def get_audio_duration(self, text, speaker=1):
        """获取音频时长（秒）"""
        try:
            # 生成一个临时音频文件来获取时长
            temp_path = Path("temp_duration.wav")
            
            # 获取音频查询参数
            query = self.get_audio_query(text, speaker)
            
            # 合成音频
            params = {"speaker": speaker}
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.base_url}/synthesis",
                params=params,
                data=json.dumps(query),
                headers=headers
            )
            
            # 保存临时文件
            temp_path.write_bytes(response.content)
            
            # 从音频文件读取实际时长
            with wave.open(str(temp_path), 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
            
            # 删除临时文件
            temp_path.unlink()
            
            return duration
            
        except Exception as e:
            print(f"获取音频时长时出错: {e}")
            return None
    
    def synthesize(self, text, output_path, speaker=None):
        """生成音频文件并返回实际时长"""
        try:
            speaker = speaker or self.speaker
            # 1. 获取音频查询参数
            query = self.get_audio_query(text, speaker)
            
            # 2. 合成音频
            params = {"speaker": speaker}
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.base_url}/synthesis",
                params=params,
                data=json.dumps(query),
                headers=headers
            )
            
            # 3. 保存音频文件
            output_path = Path(output_path)
            output_path.write_bytes(response.content)
            
            # 4. 获取实际音频时长
            with wave.open(str(output_path), 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
                return duration
                
        except Exception as e:
            print(f"生成音频时出错: {e}")
            return None
    
    def process_text_with_voices(self, text: str, voice_mapping: Dict[str, int]) -> float:
        """处理带有说话者标记的文本，使用不同的声音"""
        current_speaker = "narrator"
        
        # 识别说话者和对话
        if text.startswith("「") or text.startswith("『"):
            # 尝试从上下文识别说话者
            # 这里需要更复杂的逻辑来准确识别说话者
            pass
        
        # 使用对应的声音ID
        speaker_id = voice_mapping.get(current_speaker, 8)
        return self.synthesize(text, speaker_id) 