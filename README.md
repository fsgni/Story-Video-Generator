# 故事视频生成器 | Story Video Generator | ストーリービデオジェネレーター

[中文](#中文说明) | [English](#english-description) | [日本語](#日本語説明)

<a id="中文说明"></a>
## 中文说明

这是一个自动将文本故事转换为视频的工具，包含语音合成、场景分析、图像生成和视频制作功能。

### 功能特点

- 文本处理：智能分割长句子，保持语义完整性
- 语音合成：使用 VOICEVOX 生成自然的日语语音
- 场景分析：使用 AI 分析故事内容，提取关键场景
- 图像生成：基于场景描述自动生成相关图像
- 视频制作：将图像、音频和字幕合成为完整视频

### 安装要求

1. Python 3.8+
2. VOICEVOX 引擎（用于语音合成）
3. ComfyUI（用于图像生成）
4. FFmpeg（用于视频处理）
5. 必要的 Python 库：
   ```
   pip install openai websocket-client python-dotenv mecab-python3
   ```

### 使用方法

1. 将故事文本放入 `input_texts` 目录（.txt 格式）
2. 在 `.env` 文件中设置 API 密钥
3. 启动 VOICEVOX 和 ComfyUI 服务
4. 运行主程序：
   ```
   python full_process.py
   ```
5. 最终视频将保存在 `output` 目录中

### 处理流程

1. 文本处理：分割长句子，保持语义完整性
2. 语音生成：使用 VOICEVOX 生成自然的语音
3. 故事分析：分析故事内容，提取时代背景和关键场景
4. 图像生成：为每个场景生成相应的图像
5. 字幕生成：创建与语音同步的字幕文件
6. 视频制作：将图像、音频和字幕合成为完整视频

### 文件结构

- `full_process.py` - 主程序，协调整个处理流程
- `text_processor.py` - 文本处理模块
- `voice_generator.py` - 语音生成模块
- `story_analyzer.py` - 故事分析模块
- `image_generator.py` - 图像生成模块
- `video_maker.py` - 视频制作模块
- `generate_srt.py` - 字幕生成模块
- `add_subtitles.py` - 字幕添加模块

### 自定义设置

- 在 `Base.json` 中可以调整图像生成参数
- 在 `voice_generator.py` 中可以更改语音角色
- 在 `story_analyzer.py` 中可以调整场景分析参数

### 注意事项

- 确保 VOICEVOX 和 ComfyUI 服务已启动
- 图像生成可能需要较长时间
- 视频处理需要足够的磁盘空间

[返回顶部](#故事视频生成器--story-video-generator--ストーリービデオジェネレーター)

---

<a id="english-description"></a>
## English Description

This is a tool that automatically converts text stories into videos, featuring voice synthesis, scene analysis, image generation, and video production.

### Features

- Text Processing: Intelligently splits long sentences while maintaining semantic integrity
- Voice Synthesis: Generates natural Japanese voice using VOICEVOX
- Scene Analysis: Analyzes story content using AI to extract key scenes
- Image Generation: Automatically generates relevant images based on scene descriptions
- Video Production: Combines images, audio, and subtitles into a complete video

### Requirements

1. Python 3.8+
2. VOICEVOX engine (for voice synthesis)
3. ComfyUI (for image generation)
4. FFmpeg (for video processing)
5. Required Python libraries:
   ```
   pip install openai websocket-client python-dotenv mecab-python3
   ```

### How to Use

1. Place story text in the `input_texts` directory (.txt format)
2. Set API keys in the `.env` file
3. Start VOICEVOX and ComfyUI services
4. Run the main program:
   ```
   python full_process.py
   ```
5. The final video will be saved in the `output` directory

### Process Flow

1. Text Processing: Split long sentences while maintaining semantic integrity
2. Voice Generation: Generate natural voice using VOICEVOX
3. Story Analysis: Analyze story content, extract era background and key scenes
4. Image Generation: Generate corresponding images for each scene
5. Subtitle Generation: Create subtitles synchronized with the voice
6. Video Production: Combine images, audio, and subtitles into a complete video

### File Structure

- `full_process.py` - Main program that coordinates the entire process
- `text_processor.py` - Text processing module
- `voice_generator.py` - Voice generation module
- `story_analyzer.py` - Story analysis module
- `image_generator.py` - Image generation module
- `video_maker.py` - Video production module
- `generate_srt.py` - Subtitle generation module
- `add_subtitles.py` - Subtitle addition module

### Custom Settings

- Adjust image generation parameters in `Base.json`
- Change voice characters in `voice_generator.py`
- Adjust scene analysis parameters in `story_analyzer.py`

### Notes

- Ensure VOICEVOX and ComfyUI services are running
- Image generation may take a long time
- Video processing requires sufficient disk space

[Back to Top](#故事视频生成器--story-video-generator--ストーリービデオジェネレーター)

---

<a id="日本語説明"></a>
## 日本語説明

これはテキストストーリーを自動的に動画に変換するツールで、音声合成、シーン分析、画像生成、動画制作の機能を備えています。

### 特徴

- テキスト処理：長い文を意味を保ちながらインテリジェントに分割
- 音声合成：VOICEVOXを使用して自然な日本語音声を生成
- シーン分析：AIを使用してストーリーの内容を分析し、重要なシーンを抽出
- 画像生成：シーンの説明に基づいて関連画像を自動生成
- 動画制作：画像、音声、字幕を組み合わせて完全な動画を作成

### 必要条件

1. Python 3.8+
2. VOICEVOX エンジン（音声合成用）
3. ComfyUI（画像生成用）
4. FFmpeg（動画処理用）
5. 必要なPythonライブラリ：
   ```
   pip install openai websocket-client python-dotenv mecab-python3
   ```

### 使用方法

1. ストーリーテキストを `input_texts` ディレクトリに配置（.txt形式）
2. `.env` ファイルにAPIキーを設定
3. VOICEVOXとComfyUIサービスを起動
4. メインプログラムを実行：
   ```
   python full_process.py
   ```
5. 最終的な動画は `output` ディレクトリに保存されます

### 処理フロー

1. テキスト処理：長い文を意味を保ちながら分割
2. 音声生成：VOICEVOXを使用して自然な音声を生成
3. ストーリー分析：ストーリーの内容を分析し、時代背景と重要なシーンを抽出
4. 画像生成：各シーンに対応する画像を生成
5. 字幕生成：音声と同期した字幕を作成
6. 動画制作：画像、音声、字幕を組み合わせて完全な動画を作成

### ファイル構造

- `full_process.py` - 全体のプロセスを調整するメインプログラム
- `text_processor.py` - テキスト処理モジュール
- `voice_generator.py` - 音声生成モジュール
- `story_analyzer.py` - ストーリー分析モジュール
- `image_generator.py` - 画像生成モジュール
- `video_maker.py` - 動画制作モジュール
- `generate_srt.py` - 字幕生成モジュール
- `add_subtitles.py` - 字幕追加モジュール

### カスタム設定

- `Base.json` で画像生成パラメータを調整
- `voice_generator.py` で音声キャラクターを変更
- `story_analyzer.py` でシーン分析パラメータを調整

### 注意事項

- VOICEVOXとComfyUIサービスが起動していることを確認
- 画像生成には時間がかかる場合があります
- 動画処理には十分なディスク容量が必要です

[トップに戻る](#故事视频生成器--story-video-generator--ストーリービデオジェネレーター)

## 更新说明

现在支持两种视频制作方式：
1. 基于 FFmpeg 的原始方法
2. 基于 MoviePy 的新方法（默认），提供更平滑的镜头效果

## 安装依赖

```
pip install openai numpy pillow pydub moviepy
```

## 使用方法

1. 将故事文本放入 `story.txt` 文件
2. 运行 `python full_process.py`
3. 如果想使用原始的 FFmpeg 方法，运行 `python full_process.py --use-ffmpeg`

## 视频效果

MoviePy 版本提供以下电影般的镜头效果：
- 从左到右平移
- 从右到左平移
- 从上到下平移
- 从下到上平移
- 缓慢放大
- 缓慢缩小

这些效果会随机应用到不同的场景，创造出更加生动的视觉体验。 