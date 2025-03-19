# 🎙 transcribe_project

## 概要
transcribe_projectは、音声データをアップロードすると文字起こしを行い、結果を画面に表示し、PDFとしてダウンロード可能なWebアプリケーションです。  
主な文字起こしエンジンとしてOpenAIの**Whisper**を使用しており、以下の3種類のモデルサイズから選択できます：
- **tiny**
- **small**
- **turbo**

また、2人以上の音声が重なっている場合、ユーザーが同時話者数を「2」と指定すると、**Asteroid**を利用して音声分離を行い、各話者ごとに文字起こしを実施します。

## 特徴
- **音声アップロード & 文字起こし**  
  音声ファイルをアップロードすると、文字起こし結果が画面上に表示されます。

- **PDFダウンロード**  
  文字起こし結果をPDFファイルとして保存・ダウンロード可能です。

- **モデル選択**  
  Whisperの3つのモデルサイズ（tiny, small, turbo）から選択し、処理内容を調整できます。

- **音声分離機能**  
  複数話者が混在する音声の場合、ユーザーが指定した話者数に基づいてAsteroidを用いた音声分離が実行されます。

- **AWS Copilotでデプロイ**  
  現在、AWS Copilotを利用してバックエンドサービスをデプロイしているため、推論に時間がかかる場合があります。将来的にはGPUインスタンスへの移行を検討中です。

- **シンプルなフロントエンド**  
  フロントエンドはStreamlitを使用しており、シンプルかつ直感的なUIを提供します。

## 利用方法
1. **リポジトリのクローンまたはZIPダウンロード**  
   リポジトリをクローン、もしくはZIPファイルとしてダウンロードしてください。

2. **依存関係のインストール**  
   プロジェクトフォルダ内の `requirements.txt` を参考に、必要なライブラリをインストールしてください。  
   例:
   ```bash
   pip install -r requirements.txt


This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
