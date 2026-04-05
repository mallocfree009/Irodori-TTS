# ComfyUI IrodoriTTS Custom Nodes

This package provides custom nodes for using [IrodoriTTS](https://github.com/IrodoriTTS/IrodoriTTS) within ComfyUI.

## 概要 (Overview)

提供されているノードは以下の2つです。

1. **MFIrodoriTTS**: ベースモデル用の音声合成ノード。`gradio_app.py`で利用できるパラメータと同様の操作を提供します。テキスト入力または音声参照(リファレンスオーディオ)入力による合成が可能です。
2. **MFIrodoriTTSDesign**: VoiceDesignモデル用の音声合成ノード。`gradio_app_voicedesign.py`で利用できるパラメータと同様の操作を提供します。テキストとキャプション(スタイルプロンプト)入力による合成が可能です。

## インストール方法 (Installation)

ComfyUIの `custom_nodes` フォルダ内に、このプロジェクトのディレクトリを配置します。

```bash
cd ComfyUI/custom_nodes/
git clone <this_repository_url> IrodoriTTS-ComfyUI
```

IrodoriTTSに必要な依存関係をインストールしてください。

```bash
cd IrodoriTTS-ComfyUI
pip install -r requirements.txt
```

## 各ノードの使い方 (Usage)

### 1. MFIrodoriTTS
- **text (Required)**: 読み上げたいテキストを入力します。
- **checkpoint**: IrodoriTTSのチェックポイントのパス(ローカルの .pt や .safetensors)を指定します。
- **uploaded_audio (Optional)**: 参照したい音声がある場合、ComfyUIの `Load Audio` などのノードを接続します。指定がない場合はノーリファレンスモード(テキストのみ)で動作します。
- **cfg_scale_text / cfg_scale_speaker**: それぞれのCFGスケールを調整して、テキストや声質の反映度合いをコントロールします。

### 2. MFIrodoriTTSDesign
- **text (Required)**: 読み上げたいテキストを入力します。
- **caption (Optional)**: どのような声で読み上げるか、スタイルのプロンプト(キャプション)を入力します。空欄の場合はテキストのみで合成されます。
- **checkpoint**: VoiceDesign版のチェックポイントパスを指定します。(例: `Aratako/Irodori-TTS-500M-v2-VoiceDesign` など)

## 出力 (Output)
- **AUDIO**: ComfyUI標準の音声フォーマット(`{"waveform": Tensor, "sample_rate": int}`)として出力されます。これを `Save Audio` などのノードに接続して保存やプレビューを行うことができます。
