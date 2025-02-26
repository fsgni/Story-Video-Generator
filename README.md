# 故事视频生成器

这是一个自动将文本故事转换为视频的工具，包含语音合成、场景分析、图像生成和视频制作功能。

## 功能特点

- 文本处理：智能分割长句子，保持语义完整性
- 语音合成：使用 VOICEVOX 生成自然的日语语音
- 场景分析：使用 AI 分析故事内容，提取关键场景
- 图像生成：基于场景描述自动生成相关图像
- 视频制作：将图像、音频和字幕合成为完整视频

## 安装要求

1. Python 3.8+
2. VOICEVOX 引擎（用于语音合成）
3. ComfyUI（用于图像生成）
4. FFmpeg（用于视频处理）
5. 必要的 Python 库：
   ```
   pip install openai websocket-client python-dotenv mecab-python3
   ```

## 使用方法

1. 将故事文本放入 `input_texts` 目录（.txt 格式）
2. 在 `.env` 文件中设置 API 密钥
3. 启动 VOICEVOX 和 ComfyUI 服务
4. 运行主程序：
   ```
   python full_process.py
   ```
5. 最终视频将保存在 `output` 目录中

## 处理流程

1. 文本处理：分割长句子，保持语义完整性
2. 语音生成：使用 VOICEVOX 生成自然的语音
3. 故事分析：分析故事内容，提取时代背景和关键场景
4. 图像生成：为每个场景生成相应的图像
5. 字幕生成：创建与语音同步的字幕文件
6. 视频制作：将图像、音频和字幕合成为完整视频

## 文件结构

- `full_process.py` - 主程序，协调整个处理流程
- `text_processor.py` - 文本处理模块
- `voice_generator.py` - 语音生成模块
- `story_analyzer.py` - 故事分析模块
- `image_generator.py` - 图像生成模块
- `video_maker.py` - 视频制作模块
- `generate_srt.py` - 字幕生成模块
- `add_subtitles.py` - 字幕添加模块

## 自定义设置

- 在 `Base.json` 中可以调整图像生成参数
- 在 `voice_generator.py` 中可以更改语音角色
- 在 `story_analyzer.py` 中可以调整场景分析参数

## 注意事项

- 确保 VOICEVOX 和 ComfyUI 服务已启动
- 图像生成可能需要较长时间
- 视频处理需要足够的磁盘空间 