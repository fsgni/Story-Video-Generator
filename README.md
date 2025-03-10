# NarraSync

**当前版本：v1.2.0**
[中文](#中文说明) | [English](#english-description) | [日本語](#日本語説明)

<a id="中文说明"></a>
## 中文说明

NarraSync 是一个智能叙事同步工具，能够自动将文本故事转换为视频，包含语音合成、场景分析、图像生成和视频制作功能。通过先进的AI技术，NarraSync将文字与视觉完美同步，创造出引人入胜的视听体验。

### 功能特点

- 文本处理：智能分割长句子，保持语义完整性
- 语音合成：使用 VOICEVOX 生成自然的日语语音，支持发音词典
- 场景分析：使用 AI 分析故事内容，提取关键场景
- 图像生成：基于场景描述自动生成相关图像，支持多种风格和比例选择
- 视频制作：将图像、音频和字幕合成为完整视频
- Web界面：提供直观的用户界面，支持实时预览和参数调整

### 最新更新

- **ComfyUI风格选择**：添加了多种ComfyUI风格选项，包括水墨、手绘、古风、插画、写实和电影风格
- **图像比例选择**：为Midjourney图像生成器添加了16:9和9:16宽高比选项，支持生成横屏和竖屏图像
- **图像风格选择**：添加了预设风格选择功能，包括电影级品质、水墨画风格、油画风格等多种风格，以及自定义风格输入
- **输出目录清理优化**：改进了输出目录清理功能，确保在开始新的视频生成时彻底清理所有临时文件
- **WebUI界面优化**：改进了WebUI界面，添加了风格选择和图像比例选择控件，提供更直观的用户体验
- **优化视频特效**：解决抖动和黑边问题，添加平滑的淡入淡出效果
- **发音词典系统**：新增 VOICEVOX 发音词典管理功能，可纠正常见发音错误
- **简化图像提示词**：优化图像生成提示词，减少过度细节描述
- **电影效果增强**：改进视频制作流程，提供更自然的镜头转场效果
- **故事分析优化**：改进故事分析模块，支持更准确的 JSON 解析和场景描述生成，确保时代背景和场景描述的一致性
- **WebUI 界面**：新增基于 Gradio 的 Web 用户界面，提供更直观的操作体验和实时预览功能
- **场景提示词优化**：改进场景提示词生成逻辑，更好地整合故事分析结果（文化、地点、时代和风格）到最终的图像生成提示词中
- **提示词英语化**：添加自动翻译功能，确保所有图像生成提示词都使用英语，提高图像生成质量和一致性
- **分段分析功能**：增加对长文本的分段分析支持，可以更精确地处理长故事并生成段落级别的提示词
- **提示词精简优化**：大幅精简图像生成提示词，移除不必要的词汇，控制提示词长度，提高图像生成准确性

### 安装要求

1. Python 3.8+
2. VOICEVOX 引擎（用于语音合成）
3. ComfyUI（用于图像生成）或 Midjourney API 密钥
4. FFmpeg（用于视频处理）
5. 必要的 Python 库：
   ```
   pip install openai websocket-client python-dotenv mecab-python3 numpy pillow pydub moviepy gradio
   ```

### 使用方法

#### 使用WebUI界面（推荐）

1. 启动 VOICEVOX 和 ComfyUI 服务（如果使用本地图像生成）
2. 在 `.env` 文件中设置 API 密钥
3. 运行WebUI：
   ```
   python webui.py
   ```
4. 在浏览器中打开显示的URL（通常是 http://127.0.0.1:7860）
5. 输入故事文本或选择已有文件
6. 选择图像生成方式（ComfyUI或Midjourney）
7. 如果选择Midjourney，可以设置图像比例（默认方形、16:9或9:16）
8. 选择图像风格（电影级品质、水墨画风格、油画风格等）或输入自定义风格
9. 点击"开始处理"按钮
10. 等待处理完成，查看输出日志和生成的视频

#### 使用命令行

1. 将故事文本放入 `input_texts` 目录（.txt 格式）
2. 在 `.env` 文件中设置 API 密钥
3. 启动 VOICEVOX 和 ComfyUI 服务（如果使用本地图像生成）
4. 运行主程序：
   ```
   python full_process.py 你的故事文件.txt --image_generator [comfyui|midjourney] --aspect_ratio [16:9|9:16] --image_style "你的风格描述"
   ```
5. 最终视频将保存在 `output` 目录中

### WebUI 使用方法

为了提供更友好的用户体验，我们新增了基于 Gradio 的 Web 界面：

1. 安装额外依赖：
   ```
   pip install gradio
   ```

2. 启动 WebUI：
   ```
   python webui.py
   ```

3. 在浏览器中访问 `http://127.0.0.1:7860` 即可使用

WebUI 提供以下功能：
- 文本输入区：直接输入或上传故事文本
- 参数设置：调整视频生成参数
- 实时预览：查看生成的图像和场景描述
- 进度显示：实时显示处理进度
- 结果下载：直接下载生成的视频和音频文件

### 发音词典管理

新增的发音词典系统可以帮助 VOICEVOX 更准确地发音日语单词：

```bash
# 同步本地词典和VOICEVOX词典
python manage_dictionary.py --sync

# 添加自定义词条
python manage_dictionary.py --add "専有名詞" "センユウメイシ"

# 查看所有词条
python manage_dictionary.py --list

# 导出词典
python manage_dictionary.py --export "my_dict.json"

# 导入词典
python manage_dictionary.py --import "my_dict.json"
```

### 处理流程

1. 文本处理：分割长句子，保持语义完整性
2. 语音生成：使用 VOICEVOX 生成自然的语音（应用发音词典）
3. 故事分析：分析故事内容，提取时代背景和关键场景
4. 图像生成：为每个场景生成相应的图像
5. 字幕生成：创建与语音同步的字幕文件
6. 视频制作：将图像、音频和字幕合成为完整视频

### 视频效果

MoviePy 版本提供以下电影般的镜头效果：
- 从左到右平移
- 从右到左平移
- 从上到下平移
- 从下到上平移
- 缓慢放大
- 缓慢缩小

这些效果会随机应用到不同的场景，创造出更加生动的视觉体验。

### 文件说明

- `full_process.py` - 主程序，整合所有功能
- `text_processor.py` - 文本处理模块
- `voice_generator.py` - 语音生成模块
- `story_analyzer.py` - 故事分析模块
- `image_generator.py` - 图像生成模块
- `video_maker.py` - 视频制作模块（FFmpeg版）
- `video_maker_moviepy.py` - 视频制作模块（MoviePy版，提供更平滑的效果）
- `generate_srt.py` - 字幕生成模块
- `add_subtitles.py` - 字幕添加模块
- `pronunciation_dictionary.py` - 发音词典管理模块
- `manage_dictionary.py` - 词典管理工具
- `webui.py` - Web 用户界面模块，基于 Gradio 框架

### 注意事项

- 确保 VOICEVOX 和 ComfyUI 服务已启动
- 图像生成可能需要较长时间
- 推荐文本长度：500-2000字（约5-15分钟视频）
- 最大可处理文本：约5000-10000字（约15-30分钟视频）

[返回顶部](#NarraSync)

---

<a id="english-description"></a>
## English Description

NarraSync is an intelligent narrative synchronization tool that automatically converts text stories into videos, including voice synthesis, scene analysis, image generation, and video production. Through advanced AI technology, NarraSync perfectly synchronizes text with visuals, creating an engaging audiovisual experience.

### Features

- Text Processing: Intelligently splits long sentences while maintaining semantic integrity
- Voice Synthesis: Uses VOICEVOX to generate natural Japanese voice with pronunciation dictionary support
- Scene Analysis: Uses AI to analyze story content and extract key scenes
- Image Generation: Automatically generates relevant images based on scene descriptions, supports multiple style and aspect ratio options
- Video Production: Combines images, audio, and subtitles into a complete video
- WebUI Interface: Provides a user-friendly interface for real-time preview and parameter adjustment

### Latest Updates

- **ComfyUI Style Selection**: Added multiple ComfyUI style options, including ink painting, hand-drawn, classical Chinese, illustration, realistic, and cinematic styles
- **Image Aspect Ratio Selection**: Added 16:9 and 9:16 aspect ratio options for Midjourney image generator, supporting horizontal and vertical image generation
- **Image Style Selection**: Added preset style selection feature, including multiple styles such as cinematic quality, ink painting style, oil painting style, and custom style input
- **Output Directory Cleanup Optimization**: Improved output directory cleanup functionality to ensure thorough cleanup of all temporary files before starting a new video generation
- **WebUI Interface Optimization**: Improved WebUI interface by adding style selection and image aspect ratio selection controls for a more intuitive user experience
- **Pronunciation Dictionary System**: Added VOICEVOX pronunciation dictionary management to correct common pronunciation errors
- **Simplified Image Prompts**: Optimized image generation prompts, reducing excessive detail descriptions
- **Enhanced Cinematic Effects**: Improved video production process with more natural camera transitions
- **Story Analysis Optimization**: Improved story analysis module to support more accurate JSON parsing and scene description generation, ensuring consistency between era background and scene descriptions
- **WebUI Interface**: Added a new Web UI based on Gradio for a more intuitive operation experience and real-time preview functionality
- **Scene Prompt Optimization**: Improved scene prompt generation logic to better integrate story analysis results (culture, location, era, and style) into the final image generation prompts
- **English Prompt Conversion**: Added automatic translation to ensure all image generation prompts use English, improving image generation quality and consistency
- **Segmented Analysis Function**: Added support for segmented analysis of long texts, allowing for more precise handling of long stories and generation of paragraph-level prompts
- **Prompt Refinement Optimization**: Significantly simplified image generation prompts, removed unnecessary vocabulary, controlled prompt length to improve image generation accuracy

### Installation Requirements

1. Python 3.8+
2. VOICEVOX engine (for voice synthesis)
3. ComfyUI (for image generation) or Midjourney API key
4. FFmpeg (for video processing)
5. Required Python libraries:
   ```
   pip install openai websocket-client python-dotenv mecab-python3 numpy pillow pydub moviepy gradio
   ```

### Usage

#### Using WebUI Interface (Recommended)

1. Start VOICEVOX and ComfyUI services (if using local image generation)
2. Set API keys in the `.env` file
3. Run WebUI:
   ```
   python webui.py
   ```
4. Open the displayed URL in your browser (usually http://127.0.0.1:7860)
5. Input story text or select an existing file
6. Select image generation method (ComfyUI or Midjourney)
7. If selecting Midjourney, set image aspect ratio (default square, 16:9, or 9:16)
8. Select image style (cinematic quality, ink painting style, oil painting style, etc.) or input custom style
9. Click "Start Processing" button
10. Wait for processing to complete, check output logs and generated video

#### Using Command Line

1. Place story text in the `input_texts` directory (.txt format)
2. Set API keys in the `.env` file
3. Start VOICEVOX and ComfyUI services (if using local image generation)
4. Run the main program:
   ```
   python full_process.py your_story_file.txt --image_generator [comfyui|midjourney] --aspect_ratio [16:9|9:16] --image_style "your_style_description"
   ```
5. The final video will be saved in the `output` directory

### WebUI Usage

To provide a better user experience, we've added a new Web UI based on Gradio:

1. Install additional dependencies:
   ```
   pip install gradio
   ```

2. Start WebUI:
   ```
   python webui.py
   ```

3. Access the Web UI in your browser by visiting `http://127.0.0.1:7860`

WebUI provides the following features:
- Text Input Area: Directly input or upload story text
- Parameter Settings: Adjust video generation parameters
- Real-time Preview: View generated images and scene descriptions
- Progress Display: Display real-time processing progress
- Result Download: Directly download generated video and audio files

### Pronunciation Dictionary Management

The new pronunciation dictionary system helps VOICEVOX pronounce Japanese words more accurately:

```bash
# Sync local dictionary with VOICEVOX
python manage_dictionary.py --sync

# Add custom entries
python manage_dictionary.py --add "term" "pronunciation"

# View all entries
python manage_dictionary.py --list

# Export dictionary
python manage_dictionary.py --export "my_dict.json"

# Import dictionary
python manage_dictionary.py --import "my_dict.json"
```

### Processing Flow

1. Text Processing: Split long sentences while maintaining semantic integrity
2. Voice Generation: Generate natural voice using VOICEVOX (applying pronunciation dictionary)
3. Story Analysis: Analyze story content, extract era background and key scenes
4. Image Generation: Generate corresponding images for each scene
5. Subtitle Generation: Create subtitles synchronized with audio
6. Video Production: Combine images, audio, and subtitles into a complete video

### Video Effects

The MoviePy version provides the following cinematic camera effects:
- Pan from left to right
- Pan from right to left
- Pan from top to bottom
- Pan from bottom to top
- Slow zoom in
- Slow zoom out

These effects are randomly applied to different scenes, creating a more vivid visual experience.

### File Description

- `full_process.py` - Main program integrating all functions
- `text_processor.py` - Text processing module
- `voice_generator.py` - Voice generation module
- `story_analyzer.py` - Story analysis module
- `image_generator.py` - Image generation module
- `video_maker.py` - Video production module (FFmpeg version)
- `video_maker_moviepy.py` - Video production module (MoviePy version with smoother effects)
- `generate_srt.py` - Subtitle generation module
- `add_subtitles.py` - Subtitle addition module
- `pronunciation_dictionary.py` - Pronunciation dictionary management module
- `manage_dictionary.py` - Dictionary management tool
- `webui.py` - Web UI module, based on Gradio framework

### Notes

- Ensure VOICEVOX and ComfyUI services are running
- Image generation may take a long time
- Recommended text length: 500-2000 characters (about 5-15 minute video)
- Maximum processable text: about 5000-10000 characters (about 15-30 minute video)

[Back to Top](#NarraSync)

---

<a id="日本語説明"></a>
## 日本語説明

NarraSyncは、テキストストーリーを自動的に動画に変換するインテリジェントなナラティブ同期ツールで、音声合成、シーン分析、画像生成、動画制作機能を含みます。先進的なAI技術により、NarraSyncはテキストとビジュアルを完璧に同期させ、魅力的な視聴覚体験を創り出します。

### 機能特徴

- テキスト処理：長い文を意味的整合性を保ちながらインテリジェントに分割
- 音声合成：VOICEVOXを使用して自然な日本語音声を生成、発音辞書をサポート
- シーン分析：AIを使用してストーリーの内容を分析し、重要なシーンを抽出
- 画像生成：シーンの説明に基づいて関連画像を自動生成
- 動画制作：画像、音声、字幕を完全な動画に合成

### 最新アップデート

- **発音辞書システム**：VOICEVOX発音辞書管理機能を追加し、一般的な発音エラーを修正
- **画像プロンプトの簡素化**：画像生成プロンプトを最適化し、過度な詳細説明を削減
- **映画効果の強化**：より自然なカメラトランジション効果を提供する動画制作プロセスを改善
- **ストーリー分析の最適化**：ストーリー分析モジュールを改善し、より正確なJSON解析とシーンの説明生成をサポートし、時代背景とシーンの説明の一貫性を確保
- **WebUI インタフェース**：新しいWeb UIを追加し、より直感的な操作体験とリアルタイムプレビュー機能を提供
- **シーンプロンプトの最適化**：シーンプロンプト生成ロジックを改善し、より正確なJSON解析とシーンの説明生成をサポートし、文化、場所、時代、スタイルを統合した最終的な画像生成プロンプトを作成
- **プロンプト英語化**：自動翻訳機能を追加し、すべての画像生成プロンプトが英語を使用するようにして、画像生成の品質と一貫性を向上
- **分段分析機能**：長いテキストの分節分析をサポートし、長いストーリーをより正確に処理し、段落レベルのプロンプトを生成
- **プロンプト精緻化の最適化**：画像生成プロンプトを大幅に簡素化し、不要な語彙を削除、プロンプトの長さを制御して画像生成の精度を向上

### インストール要件

1. Python 3.8+
2. VOICEVOXエンジン（音声合成用）
3. ComfyUI（画像生成用）
4. FFmpeg（動画処理用）
5. 必要なPythonライブラリ：
   ```
   pip install openai websocket-client python-dotenv mecab-python3 numpy pillow pydub moviepy gradio
   ```

### 使用方法

#### WebUIを使用する方法（推奨）

1. VOICEVOXとComfyUIサービスを起動（ローカル画像生成を使用する場合）
2. `.env`ファイルにAPIキーを設定
3. WebUIを実行：
   ```
   python webui.py
   ```
4. 表示されたURLをブラウザで開く（通常はhttp://127.0.0.1:7860）
5. ストーリーテキストを入力するか既存のファイルを選択
6. 画像生成方法を選択（ComfyUIまたはMidjourney）
7. Midjourneyを選択する場合は、画像のアスペクト比を設定（デフォルトは正方形、16:9または9:16）
8. 画像のスタイルを選択（映画級の品質、水墨画スタイル、油絵スタイルなど）またはカスタムスタイルを入力
9. "Start Processing"ボタンをクリック
10. 処理が完了するのを待ち、出力ログと生成された動画を確認

#### コマンドラインを使用する方法

1. ストーリーテキストを`input_texts`ディレクトリに配置（.txt形式）
2. `.env`ファイルにAPIキーを設定
3. VOICEVOXとComfyUIサービスを起動（ローカル画像生成を使用する場合）
4. メインプログラムを実行：
   ```
   python full_process.py your_story_file.txt --image_generator [comfyui|midjourney] --aspect_ratio [16:9|9:16] --image_style "your_style_description"
   ```
5. 最終動画は`output`ディレクトリに保存されます

### WebUI 使用方法

よりユーザフレンドリーな体験を提供するために、新しいWeb UIを追加しました：

1. 追加の依存関係をインストール：
   ```
   pip install gradio
   ```

2. Web UIを起動：
   ```
   python webui.py
   ```

3. ブラウザで`http://127.0.0.1:7860`にアクセスして使用

Web UIは以下の機能を提供します：
- テキスト入力領域：テキストを直接入力するかアップロード
- パラメータ設定：動画生成パラメータを調整
- リアルタイムプレビュー：生成された画像とシーンの説明を表示
- 進行表示：処理の進行をリアルタイムで表示
- 結果ダウンロード：生成された動画と音声ファイルを直接ダウンロード

### 発音辞書管理

新しい発音辞書システムは、VOICEVOXがより正確に日本語の単語を発音するのに役立ちます：

```bash
# ローカル辞書とVOICEVOX辞書を同期
python manage_dictionary.py --sync

# カスタムエントリを追加
python manage_dictionary.py --add "専有名詞" "センユウメイシ"

# すべてのエントリを表示
python manage_dictionary.py --list

# 辞書をエクスポート
python manage_dictionary.py --export "my_dict.json"

# 辞書をインポート
python manage_dictionary.py --import "my_dict.json"
```

### 処理フロー

1. テキスト処理：長い文を意味的整合性を保ちながら分割
2. 音声生成：VOICEVOXを使用して自然な音声を生成（発音辞書を適用）
3. ストーリー分析：ストーリーの内容を分析し、時代背景と重要なシーンを抽出
4. 画像生成：各シーンに対応する画像を生成
5. 字幕生成：音声と同期した字幕を作成
6. 動画制作：画像、音声、字幕を完全な動画に合成

### 動画効果

MoviePyバージョンは以下の映画のようなカメラ効果を提供します：
- 左から右へのパン
- 右から左へのパン
- 上から下へのパン
- 下から上へのパン
- ゆっくりズームイン
- ゆっくりズームアウト

これらの効果は異なるシーンにランダムに適用され、より生き生きとした視覚体験を作り出します。

### ファイル説明

- `full_process.py` - すべての機能を統合するメインプログラム
- `text_processor.py` - テキスト処理モジュール
- `voice_generator.py` - 音声生成モジュール
- `story_analyzer.py` - ストーリー分析モジュール
- `image_generator.py` - 画像生成モジュール
- `video_maker.py` - 動画制作モジュール（FFmpegバージョン）
- `video_maker_moviepy.py` - 動画制作モジュール（MoviePyバージョン、よりスムーズな効果）
- `generate_srt.py` - 字幕生成モジュール
- `add_subtitles.py` - 字幕追加モジュール
- `pronunciation_dictionary.py` - 発音辞書管理モジュール
- `manage_dictionary.py` - 辞書管理ツール
- `webui.py` - Web UI module, based on Gradio framework

### 注意事項

- VOICEVOXとComfyUIサービスが起動していることを確認
- 画像生成には時間がかかる場合があります
- 推奨テキスト長：500〜2000文字（約5〜15分の動画）
- 最大処理可能テキスト：約5000〜10000文字（約15〜30分の動画）

[トップに戻る](#NarraSync)

## 更新説明

現在は2つの動画制作方法をサポートしています：
1. 基礎となるFFmpegの方法
2. 新しい方法（デフォルト）に基づくMoviePy、よりスムーズなカメラ効果を提供

## インストール依存

```
pip install openai numpy pillow pydub moviepy
```

## 使用方法

1. ストーリーテキストを`story.txt`ファイルに配置
2. `python full_process.py`を実行
3. 基礎となるFFmpegの方法を使用する場合は、`python full_process.py --use-ffmpeg`を実行

## 動画効果

MoviePyバージョンは以下の映画のようなカメラ効果を提供します：
- 左から右へのパン
- 右から左へのパン
- 上から下へのパン
- 下から上へのパン
- ゆっくりズームイン
- ゆっくりズームアウト

これらの効果は異なるシーンにランダムに適用され、より生き生きとした視覚体験を作り出します。

## 更新日誌

[CHANGELOG.md](CHANGELOG.md)を確認して詳細な更新履歴を確認してください。 