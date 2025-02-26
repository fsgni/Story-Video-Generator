from pathlib import Path
from voice_generator import VoiceVoxGenerator
import json

def process_voice_generation(input_file: str, output_dir: str, speaker_id: int = 8):
    """处理文本到语音的转换"""
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 初始化语音生成器
    voice_generator = VoiceVoxGenerator()
    
    # 列出可用角色
    print("可用角色列表：")
    for id, name in voice_generator.list_speakers().items():
        print(f"ID: {id} - {name}")
    
    # 设置说话人
    voice_generator.set_speaker(speaker_id)
    print(f"\n使用角色: {voice_generator.speakers[speaker_id]}")
    
    # 读取文本文件
    with open(input_file, "r", encoding="utf-8") as f:
        sentences = [line.strip() for line in f if line.strip()]
    
    # 存储音频信息
    audio_info = []
    
    # 处理每个句子
    for i, sentence in enumerate(sentences):
        try:
            # 生成音频文件并获取时长
            audio_file = f"audio_{i:03d}.wav"
            audio_path = output_path / audio_file
            duration = voice_generator.synthesize(sentence, audio_path)
            
            if duration is None:
                raise Exception("无法获取音频时长")
            
            # 记录信息
            audio_info.append({
                "id": i,
                "sentence": sentence,
                "audio_file": str(audio_file),
                "duration": duration
            })
            
            print(f"已生成音频 {i+1}/{len(sentences)}: {audio_file} (时长: {duration:.2f}秒)")
            
        except Exception as e:
            print(f"生成音频失败 {i}: {e}")
            audio_info.append({
                "id": i,
                "sentence": sentence,
                "error": str(e)
            })
    
    # 保存音频信息到JSON文件
    info_file = output_path / f"{Path(input_file).stem}_audio_info.json"
    with open(info_file, "w", encoding="utf-8") as f:
        json.dump({
            "source_file": input_file,
            "total_sentences": len(sentences),
            "total_duration": sum(info.get("duration", 0) for info in audio_info),
            "audio_files": audio_info
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n处理完成！")
    print(f"总句子数: {len(sentences)}")
    print(f"音频信息已保存到: {info_file}")
    
    return audio_info

if __name__ == "__main__":
    # 处理指定的文本文件
    input_file = "output_texts/お菓子の森の秘密星に願いを込めてなど.txt"
    output_dir = "output/audio"
    speaker_id = 8  # 可以根据需要更改角色
    
    audio_info = process_voice_generation(input_file, output_dir, speaker_id) 