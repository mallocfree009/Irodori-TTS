# Irodori-TTS ComfyUI API Custom Nodes Specification

このドキュメントでは、Irodori-TTSのGradioサーバーをAPIとしてコールし、ComfyUI上で音声を合成するためのカスタムノードの実装仕様を定義します。

## ノード一覧

### 1. IrodoriTTSWebAPI
`gradio_app.py` で起動したGradioサーバーに対してリクエストを送信し、音声を合成します。

#### INPUT_TYPES
*   **required**:
    *   `api_url` (STRING): Gradio APIのURL。デフォルトは `"http://127.0.0.1:7860/"`。
    *   `checkpoint` (STRING): モデルチェックポイント（HFリポジトリまたはローカルパス）。デフォルトは `"Aratako/Irodori-TTS-500M-v2"`。
    *   `model_device` (STRING): モデルの実行デバイス (`"auto"`, `"cuda"`, `"cpu"`, `"mps"`)。デフォルトは `"auto"`。
    *   `model_precision` (STRING): モデルの精度 (`"fp32"`, `"bf16"`, `"fp16"`)。デフォルトは `"fp32"`。
    *   `codec_device` (STRING): コーデックの実行デバイス。デフォルトは `"auto"`。
    *   `codec_precision` (STRING): コーデックの精度。デフォルトは `"fp32"`。
    *   `enable_watermark` (BOOLEAN): 電子透かしを有効にするか。デフォルトは `False`。
    *   `text` (STRING, multiline): 合成するテキスト。
    *   `num_steps` (INT): サンプリングステップ数。デフォルトは `40`、最小 `1`、最大 `120`。
    *   `num_candidates` (INT): 候補数。デフォルトは `1`、最小 `1`、最大 `32`。
    *   `cfg_guidance_mode` (STRING): CFGガイダンスモード (`"independent"`, `"joint"`, `"alternating"`)。デフォルトは `"independent"`。
    *   `cfg_scale_text` (FLOAT): テキストのCFGスケール。デフォルトは `3.0`。
    *   `cfg_scale_speaker` (FLOAT): 話者のCFGスケール。デフォルトは `5.0`。
    *   `cfg_min_t` (FLOAT): CFGの最小t。デフォルトは `0.5`。
    *   `cfg_max_t` (FLOAT): CFGの最大t。デフォルトは `1.0`。
    *   `context_kv_cache` (BOOLEAN): KVキャッシュを有効にするか。デフォルトは `True`。
*   **optional**:
    *   `uploaded_audio` (AUDIO): 参照音声データ。未指定時はリファレンスなしモードとして動作。
    *   `seed_raw` (STRING): シード値の文字列。空文字列の場合はランダム。
    *   `cfg_scale_raw` (STRING): CFGスケールのオーバーライド。
    *   `truncation_factor_raw` (STRING): 切り捨て係数。
    *   `rescale_k_raw` (STRING): リスケールk。
    *   `rescale_sigma_raw` (STRING): リスケールsigma。
    *   `speaker_kv_scale_raw` (STRING): 話者KVスケール。
    *   `speaker_kv_min_t_raw` (STRING): 話者KVの最小t。デフォルトは `"0.9"`。
    *   `speaker_kv_max_layers_raw` (STRING): 話者KVの最大レイヤー数。

#### RETURN_TYPES
*   `AUDIO`: `{"waveform": tensor, "sample_rate": sample_rate}` の形式で音声データを返します。


### 2. IrodoriTTSDesignWebAPI
`gradio_app_voicedesign.py` で起動したVoiceDesign版Gradioサーバーに対してリクエストを送信し、音声を合成します。

#### INPUT_TYPES
*   **required**:
    *   `api_url` (STRING): Gradio APIのURL。デフォルトは `"http://127.0.0.1:7861/"`。
    *   `checkpoint` (STRING): モデルチェックポイント。デフォルトは `"Aratako/Irodori-TTS-500M-v2-VoiceDesign"`。
    *   `model_device` (STRING): モデルの実行デバイス。デフォルトは `"auto"`。
    *   `model_precision` (STRING): モデルの精度。デフォルトは `"fp32"`。
    *   `codec_device` (STRING): コーデックの実行デバイス。デフォルトは `"auto"`。
    *   `codec_precision` (STRING): コーデックの精度。デフォルトは `"fp32"`。
    *   `enable_watermark` (BOOLEAN): 電子透かしを有効にするか。デフォルトは `False`。
    *   `text` (STRING, multiline): 合成するテキスト。
    *   `num_steps` (INT): サンプリングステップ数。デフォルトは `40`。
    *   `num_candidates` (INT): 候補数。デフォルトは `1`。
    *   `cfg_guidance_mode` (STRING): CFGガイダンスモード。デフォルトは `"independent"`。
    *   `cfg_scale_text` (FLOAT): テキストのCFGスケール。デフォルトは `2.0`。
    *   `cfg_scale_caption` (FLOAT): キャプションのCFGスケール。デフォルトは `4.0`。
    *   `cfg_min_t` (FLOAT): CFGの最小t。デフォルトは `0.5`。
    *   `cfg_max_t` (FLOAT): CFGの最大t。デフォルトは `1.0`。
    *   `context_kv_cache` (BOOLEAN): KVキャッシュを有効にするか。デフォルトは `True`。
*   **optional**:
    *   `caption` (STRING, multiline): 音声のスタイルを指定するキャプションテキスト。
    *   `seed_raw` (STRING): シード値の文字列。
    *   `cfg_scale_raw` (STRING): CFGスケールのオーバーライド。
    *   `max_text_len_raw` (STRING): 最大テキスト長。
    *   `max_caption_len_raw` (STRING): 最大キャプション長。
    *   `truncation_factor_raw` (STRING): 切り捨て係数。
    *   `rescale_k_raw` (STRING): リスケールk。
    *   `rescale_sigma_raw` (STRING): リスケールsigma。

#### RETURN_TYPES
*   `AUDIO`: `{"waveform": tensor, "sample_rate": sample_rate}` の形式で音声データを返します。

## API呼び出しの要件
*   `gradio_client.Client(src=api_url)` を利用して通信を行う。
*   `client.predict(..., api_name="/generate")` を利用する。
*   ComfyUI側でAudio入力を受け取った場合、一時ファイル（WAV）に保存して `gradio_client.handle_file` を通じてAPIに送信する。
*   戻り値としてGradio APIから取得したWAVファイルを読み込み、ComfyUIの `AUDIO` 形式に変換する。
