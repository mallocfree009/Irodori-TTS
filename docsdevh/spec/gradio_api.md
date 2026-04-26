# Irodori-TTS Gradio API 仕様

このドキュメントでは、Irodori-TTSのGradioアプリケーション (`gradio_app.py` および `gradio_app_voicedesign.py`) が提供するAPI (`api_name="generate"`) の仕様を定義します。
Gradio Client を使用して外部プログラム（ComfyUIカスタムノード等）からAPIを呼び出す際のインターフェースとして機能します。

## 1. Base Model (`gradio_app.py`)

参照音声 (Reference Audio) を用いた推論や、テキストのみからの推論を行うベースモデル向けのAPI仕様です。

### API エンドポイント
- `api_name="generate"`

### 入力パラメータ (`predict` に渡すキーワード引数推奨)
| パラメータ名 | 型 | 説明 |
| :--- | :--- | :--- |
| `checkpoint` | `str` | チェックポイントファイルのパスまたはHugging FaceリポジトリID。 |
| `model_device` | `str` | モデルの実行デバイス (例: `cuda:0`, `cpu`)。 |
| `model_precision` | `str` | モデルの精度 (例: `float32`, `float16`, `bfloat16`)。 |
| `codec_device` | `str` | コーデックの実行デバイス。 |
| `codec_precision` | `str` | コーデックの精度。 |
| `enable_watermark` | `bool` | 電子透かしの有効/無効化 (現状は内部実装に依存)。 |
| `text` | `str` | 読み上げる対象のテキスト（必須）。 |
| `uploaded_audio` | `str` \| `None` | 参照音声ファイルのパス。空またはNoneの場合はノーリファレンスモードになる。 |
| `num_steps` | `int` | 生成ステップ数 (デフォルト: 40)。 |
| `num_candidates` | `int` | 生成する音声候補の数 (1 〜 32)。 |
| `seed_raw` | `str` | シード値 (空文字列の場合はランダム)。 |
| `cfg_guidance_mode` | `str` | CFGガイダンスモード (`independent`, `joint`, `alternating`)。 |
| `cfg_scale_text` | `float` | テキストのCFGスケール。 |
| `cfg_scale_speaker` | `float` | 話者（参照音声）のCFGスケール。 |
| `cfg_scale_raw` | `str` | CFGスケールの上書き設定 (オプション)。 |
| `cfg_min_t` | `float` | CFG適用最小時間t。 |
| `cfg_max_t` | `float` | CFG適用最大時間t。 |
| `context_kv_cache` | `bool` | コンテキストのKVキャッシュを有効にするか。 |
| `truncation_factor_raw` | `str` | トランケーション係数 (オプション)。 |
| `rescale_k_raw` | `str` | 再スケール係数 k (オプション)。 |
| `rescale_sigma_raw` | `str` | 再スケール係数 sigma (オプション)。 |
| `speaker_kv_scale_raw` | `str` | 話者KVスケール (オプション)。 |
| `speaker_kv_min_t_raw` | `str` | 話者KV適用最小時間t (オプション、デフォルト `0.9`)。 |
| `speaker_kv_max_layers_raw` | `str` | 話者KV適用最大レイヤー数 (オプション)。 |

---

## 2. VoiceDesign Model (`gradio_app_voicedesign.py`)

キャプション (テキストによる声質や感情の指定) を用いた推論を行うVoiceDesignモデル向けのAPI仕様です。参照音声入力はサポートしていません。

### API エンドポイント
- `api_name="generate"`

### 入力パラメータ (`predict` に渡すキーワード引数推奨)
| パラメータ名 | 型 | 説明 |
| :--- | :--- | :--- |
| `checkpoint` | `str` | チェックポイントファイルのパスまたはHugging FaceリポジトリID。 |
| `model_device` | `str` | モデルの実行デバイス (例: `cuda:0`, `cpu`)。 |
| `model_precision` | `str` | モデルの精度 (例: `float32`, `float16`, `bfloat16`)。 |
| `codec_device` | `str` | コーデックの実行デバイス。 |
| `codec_precision` | `str` | コーデックの精度。 |
| `enable_watermark` | `bool` | 電子透かしの有効/無効化。 |
| `text` | `str` | 読み上げる対象のテキスト（必須）。 |
| `caption` | `str` | 声質や感情を指定するキャプションテキスト (空の場合はテキストのみの条件付け)。 |
| `num_steps` | `int` | 生成ステップ数 (デフォルト: 40)。 |
| `num_candidates` | `int` | 生成する音声候補の数 (1 〜 32)。 |
| `seed_raw` | `str` | シード値 (空文字列の場合はランダム)。 |
| `cfg_guidance_mode` | `str` | CFGガイダンスモード (`independent`, `joint`, `alternating`)。 |
| `cfg_scale_text` | `float` | テキストのCFGスケール。 |
| `cfg_scale_caption` | `float` | キャプションのCFGスケール。 |
| `cfg_scale_raw` | `str` | CFGスケールの上書き設定 (オプション)。 |
| `cfg_min_t` | `float` | CFG適用最小時間t。 |
| `cfg_max_t` | `float` | CFG適用最大時間t。 |
| `context_kv_cache` | `bool` | コンテキストのKVキャッシュを有効にするか。 |
| `max_text_len_raw` | `str` | テキストの最大長 (オプション)。 |
| `max_caption_len_raw` | `str` | キャプションの最大長 (オプション)。 |
| `truncation_factor_raw` | `str` | トランケーション係数 (オプション)。 |
| `rescale_k_raw` | `str` | 再スケール係数 k (オプション)。 |
| `rescale_sigma_raw` | `str` | 再スケール係数 sigma (オプション)。 |

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
