import json
from pathlib import Path
from datetime import timedelta

def format_srt_time(seconds: float) -> str:
    """将秒数转换为 SRT 时间格式 (HH:MM:SS,mmm)"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    seconds = td.total_seconds() % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def split_long_sentence(text: str, max_length: int = 25) -> str:
    """将长句子分成多行，避免标点符号单独成行"""
    if len(text) <= max_length:
        return text
    
    # 定义标点符号
    punctuations = ['。', '、', '，', '！', '？', '」', '』', '）', '：', '…']
    
    # 如果文本以引号开始，特殊处理
    if text.startswith('「') or text.startswith('『'):
        quote = text[0]
        inner_text = text[1:]
        # 递归处理内部文本
        inner_lines = split_long_sentence(inner_text, max_length - 1)  # 减1为引号预留空间
        lines = [quote + line if i == 0 else line for i, line in enumerate(inner_lines.split('\n'))]
        return '\n'.join(lines)
    
    # 寻找最佳分割点
    best_split = max_length
    for i in range(max_length, 0, -1):
        if i >= len(text):
            continue
        # 避免在标点符号前分行
        if text[i] in punctuations:
            continue
        # 找到合适的分割点
        if text[i-1] not in punctuations:
            best_split = i
            break
    
    # 分割文本
    first_line = text[:best_split]
    remaining_text = text[best_split:]
    
    # 如果剩余文本不为空，递归处理
    if remaining_text:
        # 处理标点符号
        if remaining_text[0] in punctuations:
            first_line += remaining_text[0]
            remaining_text = remaining_text[1:]
        
        if remaining_text:
            return first_line + '\n' + split_long_sentence(remaining_text, max_length)
    
    return first_line

def generate_srt(audio_info_file: str, output_file: str):
    """根据音频信息生成 SRT 字幕文件"""
    # 读取音频信息
    with open(audio_info_file, 'r', encoding='utf-8') as f:
        info = json.load(f)
    
    # 生成 SRT 内容
    srt_content = []
    current_time = 0.0
    
    for i, audio in enumerate(info['audio_files'], 1):
        # 获取开始和结束时间
        start_time = current_time
        duration = audio.get('duration', 0)
        end_time = start_time + duration
        
        # 处理长句子
        text = split_long_sentence(audio['sentence'])
        
        # 格式化字幕条目
        srt_entry = (
            f"{i}\n"
            f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n"
            f"{text}\n"
        )
        srt_content.append(srt_entry)
        
        # 更新当前时间
        current_time = end_time
    
    # 写入 SRT 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(srt_content))
    
    print(f"已生成字幕文件: {output_file}")
    print(f"总字幕条数: {len(srt_content)}")
    print(f"总时长: {format_srt_time(current_time)}")

if __name__ == "__main__":
    # 音频信息文件路径
    audio_info_file = "output/audio/お菓子の森の秘密星に願いを込めてなど_audio_info.json"
    # 输出的 SRT 文件路径
    output_file = "output/お菓子の森の秘密星に願いを込めてなど.srt"
    
    # 确保输出目录存在
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    generate_srt(audio_info_file, output_file) 