# ComfyUI IrodoriTTS Custom Node マニュアル

本カスタムノードを利用することで、[Irodori-TTS](https://github.com/Aratako/Irodori-TTS) の音声合成モデルをComfyUI上で動作させることができます。

## インストール方法

本リポジトリはPythonのパッケージ管理ツール `uv` を使用して依存関係を管理しています。ComfyUIのカスタムノードとして導入する手順は以下の通りです。

### 1. リポジトリのクローン

ComfyUIの `custom_nodes` ディレクトリ内に移動し、本リポジトリをクローンします。

```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/Aratako/Irodori-TTS.git
```

### 2. モデルのダウンロード

Irodori-TTSの推論にはモデルファイル（チェックポイント）が必要です。以下のいずれかの方法で準備してください。

*   **Hugging Face Hubからの自動ダウンロード**: デフォルトの設定では、自動的に `Aratako/Irodori-TTS-500M-v2` または `Aratako/Irodori-TTS-500M-v2-VoiceDesign` がダウンロード・利用されます。
*   **ローカルへの配置**: 独自のファインチューニングモデルなどを利用する場合は、`.pt` または `.safetensors` ファイルを任意のディレクトリに配置し、ノードの `checkpoint` 入力にそのファイルパスを指定してください。

### 3. 依存パッケージのインストール

ComfyUIのPython環境に依存関係をインストールします。本リポジトリは `uv` を前提としていますが、ComfyUI標準の環境（venvなど）を利用している場合は、その環境のアクティベート後、`requirements.txt` を利用してインストールすることも可能です。（ただし、`uv sync` によるインストールが推奨されます）。

**uv を使用する場合 (推奨)**
```bash
cd Irodori-TTS
uv sync
```
*(注意: ComfyUIが別環境で動いている場合は、ComfyUIのPythonインタプリタから利用できるように適切に環境を統合・設定する必要があります)*

## 提供されるノードと使い方

本リポジトリは2種類のノードを提供します。

### MFIrodoriTTS (ベースモデル用)

標準的な音声合成および、リファレンス音声を利用したVoice Cloning（話者スタイルの転写）を行うためのノードです。

*   **text**: 合成させたいテキストを入力します（必須）。
*   **checkpoint**: モデルのパス、またはHugging FaceのリポジトリID（例: `Aratako/Irodori-TTS-500M-v2`）を指定します。
*   **uploaded_audio** (オプション): リファレンスとなる音声データ（ComfyUI標準のAUDIO形式）を入力に繋ぐことで、その音声の話者スタイルを模倣します。
*   その他の詳細なパラメータ（`num_steps`, `cfg_scale_text`, `cfg_scale_speaker`など）は、生成の品質や推論速度を調整するために使用します。基本的にはデフォルト値で動作します。

### MFIrodoriTTSDesign (VoiceDesignモデル用)

キャプション（スタイルプロンプト）を指定して、テキストから音声合成を行うためのノードです。

*   **text**: 合成させたいテキストを入力します（必須）。
*   **caption**: 話者のスタイルを指示するキャプションテキスト（例：「明るく元気な若い女性の声で、少し早口で話す。」など）を入力します。
*   **checkpoint**: モデルのパス、またはHugging FaceのリポジトリID（例: `Aratako/Irodori-TTS-500M-v2-VoiceDesign`）を指定します。
*   このノードでは音声（AUDIO）の入力は使用しません。スタイルの制御はすべて `caption` を通じて行われます。

## ワークフローの構築例

1.  キャンバス上で右クリックし、`Add Node` -> `MFIrodoriTTS` -> `MFIrodoriTTS` (または `MFIrodoriTTSDesign`) を選択してノードを配置します。
2.  `text` フィールドに読み上げさせたい文章を入力します。
3.  （VoiceDesignの場合）`caption` フィールドにスタイルの指示を入力します。
4.  出力の `AUDIO` ピンから、`SaveAudio` などの音声保存/再生ノードに接続します。
5.  「Queue Prompt」を実行して音声を生成します。
