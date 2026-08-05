# `mallocfree009_03` 変更仕様書（`main` 基準）

## 目的

この文書は、`main...mallocfree009_03` の変更を後続のAI／開発者へ引き継ぐための実装仕様である。対象ブランチでは、Irodori-TTS の Gradio 推論画面を外部から呼べる Web API として整備し、出力音声の形式・保存先・一時ファイル管理を拡張した。さらに、その API を利用する ComfyUI カスタムノードと、各種起動・クリーンアップスクリプトを追加した。

## 変更の全体像

| 領域 | `main` からの変更 |
| --- | --- |
| Gradio Base / VoiceDesign | `generate` API を公開し、音声形式、保存先、一時ファイル削除を追加 |
| 推論出力 | WAV 専用保存関数を汎用音声保存関数へ変更。既定拡張子は OGG |
| ComfyUI | Gradio API を呼び出す Base / VoiceDesign 用カスタムノードを新設 |
| 運用 | Windows/macOS の起動スクリプト、GPU 固定起動、出力・Gradio 一時ファイル削除を追加 |
| 品質 | Gradio の一時ファイル削除と ComfyUI ノードのユニットテストを追加 |

## 1. Gradio Web API

### 対象アプリケーション

- Base: `gradio_app.py`、既定ポート `7860`
- VoiceDesign: `gradio_app_voicedesign.py`、既定ポート `7861`

両方の「Generate」ボタンに `api_name="generate"` を設定する。外部クライアントは `gradio_client.Client(...).predict(..., api_name="/generate")` で呼び出せる。

戻り値は、最大 32 個の音声コンポーネントと文字列 2 個から成る **34 要素**である。

- `result[0:32]`: 音声候補。Gradio の update 辞書（通常は `{"value": <path-or-none>, "visible": <bool>, ...}`）として返る場合がある。
- `result[32]`: 実行ログ。再ロード有無、使用シード、候補数、保存先、推論メッセージを含む。
- `result[33]`: タイミング情報。

候補数は 1～32 に制限する。テキストが空の場合はエラーにする。

### 追加パラメータ

Base と VoiceDesign の API に、既存の推論パラメータに加えて次を追加する。

| パラメータ | 型 / 既定値 | 仕様 |
| --- | --- | --- |
| `audio_format` | `str` / `"ogg"` | `wav`、`ogg`、`aac`、`mp3` のいずれか。生成一時ファイルの拡張子を決める。 |
| `output_file` | `str` / `""` | 任意の最終保存先。指定時は一時出力をこのパスへコピーする。既存ファイルは上書きする。 |
| `not_save_temp` | `bool` / `False` | `True` かつ `output_file` が非空のときだけ、生成後に一時出力ディレクトリを削除する。 |

`audio_format` は UI では Sampling セクション、`output_file` と `not_save_temp` は Advanced セクションで指定する。

### 出力ファイルの規則

通常の一時出力先は以下とする。

- Base: `gradio_outputs/sample_<timestamp>_<index:03d>.<audio_format>`
- VoiceDesign: `gradio_outputs_voicedesign/sample_<timestamp>_<index:03d>.<audio_format>`

`output_file` が指定された場合も、まず上記の一時ファイルへエンコードし、その後 `shutil.copy2` で最終保存先へ複製する。コピーであり再エンコードではないため、実際の音声エンコード形式は `audio_format` により決まる。ファイル名と内容の不整合を避けるため、`output_file` の拡張子も `audio_format` と一致させること。

候補が複数ある場合、最終保存先は次のように枝番を付ける。

```text
output_file = outputs/result.ogg
→ outputs/result_001.ogg, outputs/result_002.ogg, ...
```

実行ログには、`output_file` 指定時は最終保存先、未指定時は一時出力先を `saved[n]: ...` として記録する。

### 一時ファイル削除の重要な制約

`not_save_temp=True` だけでは削除しない。**`output_file` も指定された場合に限り**、専用の一時ディレクトリを作り、全候補を最終保存先へコピー後に削除する。

```text
gradio_outputs/temp_<timestamp>/             # Base
gradio_outputs_voicedesign/temp_<timestamp>/ # VoiceDesign
```

削除後に無効なパスを Gradio へ返さないため、この条件では `result[0:32]` の音声値を `None`、表示を非表示にする。したがって API 利用者は、音声パスを戻り値から取得できない。このモードでは `result[32]` の保存ログ、または呼び出し時に指定した `output_file` を最終成果物として扱うこと。

`not_save_temp=False`、または `output_file` が空の場合は、従来どおり一時出力のパスを音声戻り値として返し、削除しない。

## 2. 音声保存機能と CLI

`irodori_tts.inference_runtime.save_wav` は `save_audio(path, audio, sample_rate)` に改名する。呼び出し元はすべて新名称へ移行する。

- まず `torchaudio.save` で指定拡張子の保存を試行する。
- `RuntimeError` 時は、AAC 以外では `soundfile.write` へフォールバックする。
- AAC は SoundFile でフォールバックできないため、`torchaudio.save` 失敗時に説明付きの `RuntimeError` を送出する。

`infer.py` の `--output-wav` は名称を維持するが、既定値を `output.wav` から **`output.ogg`** に変える。引数は `.wav`、`.mp3`、`.ogg`、`.aac` を保存先拡張子として受け付ける。複数候補時は、指定ファイル名の stem と拡張子を使って `_001` 形式の枝番を付ける。

## 3. ComfyUI カスタムノード

新規ディレクトリ `ComfyUI-IrodoriTTSAPI/` は、ComfyUI の `custom_nodes` 配下へ配置する独立パッケージである。

### 提供ノード

| ノード ID | 表示名 | 接続先 | 用途 |
| --- | --- | --- | --- |
| `IrodoriTTSWebAPI` | Irodori TTS Web API | Base の `/generate` | 参照音声あり／なしの音声合成 |
| `IrodoriTTSDesignWebAPI` | Irodori TTS VoiceDesign Web API | VoiceDesign の `/generate` | caption による声質指定の音声合成 |

両ノードは `AUDIO` と `DICT`（返却名は `audio`、`parameters`）を返す。`AUDIO` は ComfyUI 形式の `{"waveform": <batch, channels, samples>, "sample_rate": <int>}` とする。

### API 呼び出しとファイル管理

- `gradio_client.Client(src=api_url)` を生成し、キーワード引数で `/generate` を呼ぶ。位置引数呼び出しは使用しない。
- ComfyUI の Base ノードで `uploaded_audio` が指定された場合、受け取った波形を一時 WAV として保存し、`handle_file()` を通じて Gradio にアップロードする。リクエスト完了後はそのアップロード用一時 WAV を削除する。
- Gradio 結果から最初の音声候補だけを読み込む。戻り値が update 辞書なら `value` をパスとして抽出する。
- 読み込み後、および先頭候補が無効な場合は、戻り値中の全音声候補（最後のログ・タイミング 2 要素を除く）を、存在するものだけ削除する。これは Gradio Client がローカルにダウンロードしたキャッシュの蓄積を防ぐためである。
- 先頭候補が `None` の場合は `ValueError` とする。

現実装のノードは、Gradio 側で追加した `audio_format`、`output_file`、`not_save_temp` を送信しない。そのためノード経由の呼び出しは Gradio の既定値（OGG、一時出力を保持）を使用する。またノードは `enable_watermark` を入力・送信しない。

### 依存関係と登録

- パッケージ要件: Python 3.10 以上、`gradio_client>=1.0.0`
- `__init__.py` の `NODE_CLASS_MAPPINGS` と `NODE_DISPLAY_NAME_MAPPINGS` で 2 ノードを登録する。
- 実行環境には ComfyUI 側の `torch`、`torchaudio` も必要である。

## 4. 起動・保守スクリプト

### Gradio 起動

以下のスクリプトを追加する。すべてスクリプト自身のディレクトリへ移動し、`.venv` の存在を確認して有効化後、ローカルホストにサーバーを起動する。

| ファイル | 環境 | 起動内容 |
| --- | --- | --- |
| `run_gui.bat` | Windows | Base、`127.0.0.1:7860` |
| `run_gui_voicedesign.bat` | Windows | VoiceDesign、`127.0.0.1:7861` |
| `run_gui.sh` | macOS / Linux | Base、`127.0.0.1:7860` |
| `run_gui_voicedesign.sh` | macOS / Linux | VoiceDesign、`127.0.0.1:7861` |
| `run_gui_gpu0.bat` | Windows | `CUDA_VISIBLE_DEVICES=0` を設定して Base を `127.0.0.1:7860` で起動 |
| `run_gui_gpu1.bat` | Windows | `CUDA_VISIBLE_DEVICES=1` を設定して Base を `127.0.0.1:7860` で起動 |

Windows の各 `.bat` は終了後に `pause`、macOS / Linux の `.sh` は終了後に Enter 待ちを行う。GPU 0/1 起動スクリプトは別プロセスで使うことを想定するが、どちらも同じポート `7860` を使うため、同一ホストで同時起動する場合は片方のポートを変更する必要がある。

### 一時ファイル削除

`run_clean_temp.bat` は次のディレクトリ内の内容を、ディレクトリ本体を残して削除する Windows 用保守スクリプトである。

1. `%LOCALAPPDATA%\Temp\gradio`
2. `V:\ai\Irodori-TTS\gradio_outputs`
3. `V:\ai\Irodori-TTS\gradio_outputs_voicedesign`

各パスが存在する場合のみ、配下のファイルとサブディレクトリを確認なしで削除する。スクリプト内のリポジトリ絶対パスは `V:\ai\Irodori-TTS` に固定されているため、別の配置先では更新が必要である。

## 5. テスト要件

追加テストは以下の振る舞いを保証する。

- `tests/test_gradio_app.py`: Base で `output_file` 指定かつ `not_save_temp=True` の場合に一時ディレクトリ削除が実行され、最初の音声 update の値が `None` になること。削除無効時は音声値を保持すること。
- `tests/test_gradio_app_voicedesign.py`: VoiceDesign で同じ一時ファイル削除規則を確認すること。
- `tests/test_comfyui_api_nodes.py`: 両ノードの入出力定義、先頭音声のロード、ダウンロード済み全候補の削除、返却する ComfyUI AUDIO 形式を確認すること。

## 6. AI 実装時の不変条件

今後この変更領域を修正する AI は、少なくとも次を維持すること。

1. Gradio の API 入力順は UI の click 入力と一致させ、外部呼び出しはキーワード引数を使う。
2. `not_save_temp` の削除は、最終保存先へのコピー成功後にだけ行う。削除後の一時パスを Gradio の音声値として返さない。
3. 複数候補では、最終保存先・CLI 保存先とも `_001` から始まる三桁の枝番を付与する。
4. AAC 保存エラーを SoundFile へ無条件フォールバックしない。
5. ComfyUI は受信・ダウンロードした一時音声を、読み込み完了後に必ず削除する。
6. ComfyUI ノードで Gradio の出力形式や `not_save_temp` を拡張する場合は、先頭音声が `None` になり得る仕様を明示的に扱う。
