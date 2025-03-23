# transcribe_project

## Overview
本projectは、音声データをアップロードすると文字起こしを行い、結果を画面に表示し、PDFとしてダウンロード可能なWebアプリケーションです。  
[transcribe_project アプリ](http://moji-a-publi-kpofio7xqi7h-1937773735.ap-northeast-1.elb.amazonaws.com/#a8464fbd)
（sample_audioフォルダの中にサンプル音声ファイルがありますので必要でしたらお使いください。）

※9~18時で実行可能となっています。
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



