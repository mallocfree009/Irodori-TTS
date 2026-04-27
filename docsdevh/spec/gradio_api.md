# Irodori-TTS Gradio API 仕様

このドキュメントでは、Irodori-TTSのGradioアプリケーション (`gradio_app.py` および `gradio_app_voicedesign.py`) が提供するAPI (`api_name="generate"`) の仕様を定義します。
Gradio Client を使用して外部プログラム（ComfyUIカスタムノード等）からAPIを呼び出す際のインターフェースとして機能します。

## 1. Base Model (`gradio_app.py`)

参照音声 (Reference Audio) を用いた推論や、テキストのみからの推論を行うベースモデル向けのAPI仕様です。

### API エンドポイント
- `api_name="generate"`

### 入力パラメータ (`predict` に渡すキーワード引数推奨)
| パラメータ名 | 型 | デフォルト値 | 説明 |
| :--- | :--- | :--- | :--- |
| `checkpoint` | `str` | `Aratako/Irodori-TTS-500M-v2`<br>またはローカルに見つかった最新ファイル | チェックポイントファイルのパスまたはHugging FaceリポジトリID。 |
| `model_device` | `str` | 実行環境のデフォルトデバイス<br>(例: `cuda:0`) | モデルの実行デバイス。 |
| `model_precision` | `str` | そのデバイスのデフォルト精度<br>(例: `bfloat16`) | モデルの精度。 |
| `codec_device` | `str` | 実行環境のデフォルトデバイス<br>(例: `cuda:0`) | コーデックの実行デバイス。 |
| `codec_precision` | `str` | そのデバイスのデフォルト精度<br>(例: `bfloat16`) | コーデックの精度。 |
| `enable_watermark` | `bool` | `False` | 電子透かしの有効/無効化 (現状は内部実装に依存)。 |
| `text` | `str` | なし (必須) | 読み上げる対象のテキスト。 |
| `uploaded_audio` | `str` \| `None` | `None` (ノーリファレンス) | 参照音声ファイルのパス。空またはNoneの場合はノーリファレンスモードになる。 |
| `num_steps` | `int` | `40` | 生成ステップ数 (1 〜 120)。 |
| `num_candidates` | `int` | `1` | 生成する音声候補の数 (1 〜 32)。 |
| `audio_format` | `str` | `"ogg"` | 出力音声ファイルのフォーマット (`wav`, `ogg`, `aac`, `mp3`)。 |
| `seed_raw` | `str` | `""` (ランダム) | シード値 (空文字列の場合はランダム)。 |
| `cfg_guidance_mode` | `str` | `"independent"` | CFGガイダンスモード (`independent`, `joint`, `alternating`)。 |
| `cfg_scale_text` | `float` | `3.0` | テキストのCFGスケール (0.0 〜 10.0)。 |
| `cfg_scale_speaker` | `float` | `5.0` | 話者（参照音声）のCFGスケール (0.0 〜 10.0)。 |
| `cfg_scale_raw` | `str` | `""` (未使用) | CFGスケールの上書き設定 (オプション)。 |
| `cfg_min_t` | `float` | `0.5` | CFG適用最小時間t。 |
| `cfg_max_t` | `float` | `1.0` | CFG適用最大時間t。 |
| `context_kv_cache` | `bool` | `True` | コンテキストのKVキャッシュを有効にするか。 |
| `truncation_factor_raw` | `str` | `""` (未使用) | トランケーション係数 (オプション)。 |
| `rescale_k_raw` | `str` | `""` (未使用) | 再スケール係数 k (オプション)。 |
| `rescale_sigma_raw` | `str` | `""` (未使用) | 再スケール係数 sigma (オプション)。 |
| `speaker_kv_scale_raw` | `str` | `""` (未使用) | 話者KVスケール (オプション)。 |
| `speaker_kv_min_t_raw` | `str` | `"0.9"` | 話者KV適用最小時間t (オプション)。 |
| `speaker_kv_max_layers_raw` | `str` | `""` (未使用) | 話者KV適用最大レイヤー数 (オプション)。 |
| `output_file` | `str` \| `None` | `""` (未使用) | 出力音声ファイルの保存先パス。指定した場合、このパスに出力されます。複数候補生成時は `_{index:03d}` が付与されます。 |

---

## 2. VoiceDesign Model (`gradio_app_voicedesign.py`)

キャプション (テキストによる声質や感情の指定) を用いた推論を行うVoiceDesignモデル向けのAPI仕様です。参照音声入力はサポートしていません。

### API エンドポイント
- `api_name="generate"`

### 入力パラメータ (`predict` に渡すキーワード引数推奨)
| パラメータ名 | 型 | デフォルト値 | 説明 |
| :--- | :--- | :--- | :--- |
| `checkpoint` | `str` | `Aratako/Irodori-TTS-500M-v2-VoiceDesign`<br>またはローカルに見つかった最新ファイル | チェックポイントファイルのパスまたはHugging FaceリポジトリID。 |
| `model_device` | `str` | 実行環境のデフォルトデバイス<br>(例: `cuda:0`) | モデルの実行デバイス。 |
| `model_precision` | `str` | そのデバイスのデフォルト精度<br>(例: `bfloat16`) | モデルの精度。 |
| `codec_device` | `str` | 実行環境のデフォルトデバイス<br>(例: `cuda:0`) | コーデックの実行デバイス。 |
| `codec_precision` | `str` | そのデバイスのデフォルト精度<br>(例: `bfloat16`) | コーデックの精度。 |
| `enable_watermark` | `bool` | `False` | 電子透かしの有効/無効化。 |
| `text` | `str` | なし (必須) | 読み上げる対象のテキスト。 |
| `caption` | `str` | `""` (テキストのみ) | 声質や感情を指定するキャプションテキスト (空の場合はテキストのみの条件付け)。 |
| `num_steps` | `int` | `40` | 生成ステップ数 (1 〜 120)。 |
| `num_candidates` | `int` | `1` | 生成する音声候補の数 (1 〜 32)。 |
| `audio_format` | `str` | `"ogg"` | 出力音声ファイルのフォーマット (`wav`, `ogg`, `aac`, `mp3`)。 |
| `seed_raw` | `str` | `""` (ランダム) | シード値 (空文字列の場合はランダム)。 |
| `cfg_guidance_mode` | `str` | `"independent"` | CFGガイダンスモード (`independent`, `joint`, `alternating`)。 |
| `cfg_scale_text` | `float` | `2.0` | テキストのCFGスケール (0.0 〜 10.0)。 |
| `cfg_scale_caption` | `float` | `4.0` | キャプションのCFGスケール (0.0 〜 10.0)。 |
| `cfg_scale_raw` | `str` | `""` (未使用) | CFGスケールの上書き設定 (オプション)。 |
| `cfg_min_t` | `float` | `0.5` | CFG適用最小時間t。 |
| `cfg_max_t` | `float` | `1.0` | CFG適用最大時間t。 |
| `context_kv_cache` | `bool` | `True` | コンテキストのKVキャッシュを有効にするか。 |
| `max_text_len_raw` | `str` | `""` (未使用) | テキストの最大長 (オプション)。 |
| `max_caption_len_raw` | `str` | `""` (未使用) | キャプションの最大長 (オプション)。 |
| `truncation_factor_raw` | `str` | `""` (未使用) | トランケーション係数 (オプション)。 |
| `rescale_k_raw` | `str` | `""` (未使用) | 再スケール係数 k (オプション)。 |
| `rescale_sigma_raw` | `str` | `""` (未使用) | 再スケール係数 sigma (オプション)。 |
| `output_file` | `str` \| `None` | `""` (未使用) | 出力音声ファイルの保存先パス。指定した場合、このパスに出力されます。複数候補生成時は `_{index:03d}` が付与されます。 |

---

## 3. 出力仕様 (Base / VoiceDesign 共通)

`predict` メソッドの戻り値は、最大32個の音声ファイル（Audioコンポーネント）と2つのテキスト出力からなる **34要素のタプル** です。

1. **`result[0:32]` (音声ファイル候補)**
   - 生成された音声ファイルのパスが格納されます（Gradio v4では辞書形式 `{'value': '...', '__type__': 'update'}` または直接文字列などで返る場合があります。値を抽出して利用してください）。
   - 指定した `num_candidates` より後の要素は `None` 扱い（UI上では `visible=False`）となります。
2. **`result[32]` (Run Log)**
   - APIの実行ログ、使用されたシード値、出力ファイルパスなどの詳細情報が文字列で格納されます (`detail_text`)。
3. **`result[33]` (Timing)**
   - 各処理ステップの実行時間（ミリ秒単位）と総デコード時間が文字列で格納されます (`timing_text`)。

**注意:**
外部のカスタムノード等から呼び出す際は、返された音声ファイルがシステム上のテンポラリディレクトリ (`%LOCALAPPDATA%\Temp\gradio` 等) にキャッシュされることがあります。不要になった場合は明示的に削除するか、クリーンアップスクリプト (`run_clean_temp.bat`等) を活用してディスク容量を管理してください。
