# ComfyUI IrodoriTTS Custom Node 仕様書

## 概要

ComfyUI上でIrodoriTTSを利用するためのカスタムノードを実装する。
提供するカスタムノードは以下の2種類。

1. **MFIrodoriTTS**: `gradio_app.py`で提供されるパラメータと同等の機能を持ち、音声合成を行う。
2. **MFIrodoriTTSDesign**: `gradio_app_voicedesign.py`で提供されるパラメータと同等の機能を持ち、キャプション指定での音声合成を行う。

## カスタムノード仕様

### 1. MFIrodoriTTS (ベースモデル用)
`gradio_app.py`に準拠したパラメータ入力を持ち、リファレンス音声を利用した合成（またはテキストのみ）を実行する。

#### 入力パラメータ
- **checkpoint**: チェックポイントのパス (文字列、デフォルト: `./checkpoint_...`)
- **model_device**: モデルのデバイス (`cpu`, `cuda`, `mps`)
- **model_precision**: モデルの精度 (`fp32`, `bf16`)
- **codec_device**: コーデックのデバイス
- **codec_precision**: コーデックの精度
- **enable_watermark**: ウォーターマークを有効にするか (bool)
- **text**: 合成するテキスト (文字列)
- **uploaded_audio**: リファレンス音声 (ComfyUIのオーディオ入力)
- **num_steps**: 推論ステップ数 (int、デフォルト: 40)
- **num_candidates**: 候補数 (int、デフォルト: 1)
- **seed_raw**: シード値 (int、空欄でランダム)
- **cfg_guidance_mode**: CFGのモード (`independent`, `joint`, `alternating`)
- **cfg_scale_text**: テキストCFGスケール (float、デフォルト: 3.0)
- **cfg_scale_speaker**: スピーカーCFGスケール (float、デフォルト: 5.0)
- **cfg_scale_raw**: 上書き用CFGスケール
- **cfg_min_t**: CFG最小T (float、デフォルト: 0.5)
- **cfg_max_t**: CFG最大T (float、デフォルト: 1.0)
- **context_kv_cache**: KVキャッシュ利用 (bool、デフォルト: True)
- **truncation_factor_raw**: トランケーション係数
- **rescale_k_raw**: rescale k
- **rescale_sigma_raw**: rescale sigma
- **speaker_kv_scale_raw**: スピーカーKVスケール
- **speaker_kv_min_t_raw**: スピーカーKV最小T (デフォルト: 0.9)
- **speaker_kv_max_layers_raw**: スピーカーKV最大レイヤー

#### 出力
- **AUDIO**: 合成された音声データ (ComfyUIオーディオフォーマット)

### 2. MFIrodoriTTSDesign (VoiceDesignモデル用)
`gradio_app_voicedesign.py`に準拠したパラメータ入力を持ち、キャプション(スタイル)による音声合成を実行する。

#### 入力パラメータ
- **checkpoint**: チェックポイントのパス (文字列、デフォルト: `Aratako/Irodori-TTS-500M-v2-VoiceDesign`)
- **model_device**: モデルのデバイス
- **model_precision**: モデルの精度
- **codec_device**: コーデックのデバイス
- **codec_precision**: コーデックの精度
- **enable_watermark**: ウォーターマークを有効にするか (bool)
- **text**: 合成するテキスト (文字列)
- **caption**: キャプション/スタイルプロンプト (文字列)
- **num_steps**: 推論ステップ数 (int、デフォルト: 40)
- **num_candidates**: 候補数 (int、デフォルト: 1)
- **seed_raw**: シード値 (int、空欄でランダム)
- **cfg_guidance_mode**: CFGのモード (`independent`, `joint`, `alternating`)
- **cfg_scale_text**: テキストCFGスケール (float、デフォルト: 2.0)
- **cfg_scale_caption**: キャプションCFGスケール (float、デフォルト: 4.0)
- **cfg_scale_raw**: 上書き用CFGスケール
- **cfg_min_t**: CFG最小T (float、デフォルト: 0.5)
- **cfg_max_t**: CFG最大T (float、デフォルト: 1.0)
- **context_kv_cache**: KVキャッシュ利用 (bool、デフォルト: True)
- **max_text_len_raw**: 最大テキスト長
- **max_caption_len_raw**: 最大キャプション長
- **truncation_factor_raw**: トランケーション係数
- **rescale_k_raw**: rescale k
- **rescale_sigma_raw**: rescale sigma

#### 出力
- **AUDIO**: 合成された音声データ (ComfyUIオーディオフォーマット)

## 実装ファイルの配置
ComfyUI Manager等で扱いやすいパッケージ構成として以下の配置とする。
- `__init__.py`: リポジトリ直下のファイル。ComfyUIからのエントリポイントとして機能し、内部パッケージからノードをロードする。
- `comfyui_irodori_tts/`: カスタムノードの実体となるパッケージディレクトリ。
  - `__init__.py`: Pythonパッケージ用の初期化ファイル。
  - `nodes.py`: カスタムノードのクラス定義 (`MFIrodoriTTS`, `MFIrodoriTTSDesign`)

## タスクリスト
- [x] カスタムノードの仕様書を作成する (`docsdevh/spec/customnode/spec.md`)
- [x] カスタムノードの実装を行う (`__init__.py`, `comfyui_irodori_tts/nodes.py`)
- [x] `gradio_app.py`, `gradio_app_voicedesign.py` で利用している推論処理 (`irodori_tts.inference_runtime`) をComfyUI向けにラップする。
- [x] 音声入出力のComfyUIフォーマットとの変換処理を実装する。
- [x] (必要に応じて) テスト用のワークフロー(JSON)を作成する。
