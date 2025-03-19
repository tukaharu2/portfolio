# transcribe_project

## 概要
本projectは、音声データをアップロードすると文字起こしを行い、結果を画面に表示し、PDFとしてダウンロード可能なWebアプリケーションです。  
[transcribe_project アプリ](https://your-app-url.example.com)
##
主な文字起こしエンジンとしてOpenAIの**Whisper**を使用しており、以下の3種類のモデルサイズから選択できます：
- **tiny**
- **small**
- **turbo**

また、2人の音声が重なっている場合、ユーザーが同時話者数を「二人」と指定すると、**Asteroid**を利用して音声分離を行い、各話者ごとに文字起こしを実施します。

##
`transcribe_project.ipynb`に使用技術の解説をまとめたのですが、ファイルサイズの問題でGit上で表示できませんでした。お手数ですがダウンロードしてgoogle colaboratoryにてご覧になって下さい。 
##
今回はcpuインスタンスでデプロイしているため、推論に時間が掛かります。今後gpuインスタンスの使用も検討します。



