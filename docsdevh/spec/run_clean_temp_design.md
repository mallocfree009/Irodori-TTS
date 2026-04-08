# Irodori-TTS 一時ファイル削除バッチ仕様

このドキュメントでは、Irodori-TTSのGradioサーバーなどによって生成される一時ファイルを削除するバッチファイル (`run_clean_temp.bat`) の仕様について定義します。

## 概要

`run_clean_temp.bat` は、Gradioの動作時やIrodori-TTSの生成結果として蓄積される一時ファイルやディレクトリをすべて削除するためのWindows向けバッチスクリプトです。これにより、ディスク容量の圧迫を防ぎ、クリーンな環境を保つことができます。

## 対象ディレクトリ

スクリプト実行時、以下の3つのディレクトリ内に存在するすべてのファイルおよびサブディレクトリが削除されます。ディレクトリ自体は削除されず、中身が空になります。

1. **Gradioの一時ファイル**
   - パス: `%LOCALAPPDATA%\Temp\gradio` (通常は `C:\Users\<カレントユーザ>\AppData\Local\Temp\gradio`)
2. **Irodori-TTSの出力ファイル (Base Model)**
   - パス: `V:\ai\Irodori-TTS\gradio_outputs`
3. **Irodori-TTSの出力ファイル (VoiceDesign Model)**
   - パス: `V:\ai\Irodori-TTS\gradio_outputs_voicedesign`

## 動作要件

- バッチファイルはダブルクリックまたはコマンドプロンプトからの実行に対応します。
- 各ディレクトリが存在するか確認し、存在する場合のみ削除処理を行います。
- `del /q /s` および `rmdir /q /s` コマンドを使用し、確認プロンプトを出さずに静かに削除処理を行います。
- 実行完了時に完了メッセージを表示し、`pause` コマンドでウィンドウを維持することで、ユーザーが実行結果を確認できるようにします。