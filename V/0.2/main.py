import json
from pathlib import Path
from text_processor import TextProcessor
from voice_generator import VoiceVoxGenerator
from image_generator import PromptGenerator

def process_story(input_file: str, output_dir: str):
    """处理整个故事流程"""
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. 文本处理
    text_processor = TextProcessor()
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
    sentences = text_processor.process_japanese_text(text)
    
    # 2. 语音生成
    voice_generator = VoiceVoxGenerator()
    audio_info = []
    
    for i, sentence in enumerate(sentences):
        try:
            # 获取音频时长
            duration = voice_generator.get_audio_duration(sentence)
            # 生成音频文件
            audio_file = f"audio_{i:03d}.wav"
            audio_path = output_path / audio_file
            voice_generator.synthesize(sentence, audio_path)
            
            audio_info.append({
                "sentence": sentence,
                "audio_file": audio_file,
                "duration": duration
            })
        except Exception as e:
            print(f"生成音频失败 {i}: {e}")
    
    # 3. 生成提示词和场景信息
    prompt_generator = PromptGenerator()
    merged_scenes = prompt_generator.merge_related_sentences(sentences)
    prompts = prompt_generator.generate_prompts_for_story(Path(input_file).name, sentences)
    
    # 4. 保存项目信息
    project_data = {
        "project_name": Path(input_file).stem,
        "scenes": []
    }
    
    current_time = 0
    for i, (scene_sentences, prompt) in enumerate(zip(merged_scenes, prompts)):
        # 找到这个场景对应的所有音频信息
        scene_audio = []
        scene_duration = 0
        for sentence in scene_sentences:
            for audio in audio_info:
                if audio["sentence"] == sentence:
                    scene_audio.append(audio)
                    scene_duration += audio["duration"]
        
        scene_data = {
            "scene_id": i,
            "sentences": {
                "text": scene_sentences,
                "start_index": len(project_data["scenes"])
            },
            "audio": {
                "files": [a["audio_file"] for a in scene_audio],
                "duration": scene_duration
            },
            "image": {
                "prompt": prompt,
                "file": f"image_{i:03d}.png"
            },
            "timing": {
                "start_time": current_time,
                "end_time": current_time + scene_duration
            }
        }
        
        current_time += scene_duration
        project_data["scenes"].append(scene_data)
    
    # 保存项目信息
    project_file = output_path / f"{Path(input_file).stem}_project.json"
    with open(project_file, "w", encoding="utf-8") as f:
        json.dump(project_data, f, ensure_ascii=False, indent=2)
    
    return project_data

if __name__ == "__main__":
    input_file = "input_texts/お菓子の森の秘密星に願いを込めてなど.txt"
    output_dir = "output"
    project_data = process_story(input_file, output_dir)
    print(f"处理完成，项目信息已保存到 {output_dir}") 