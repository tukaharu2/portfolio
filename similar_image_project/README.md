# 🖼 similar_image_project

## 概要
本プロジェクトは、類似画像検索Webアプリケーションです。  
**主な処理の流れは以下の通りです。**

1. **事前処理**  
   - Open Images V7からランダムに取得した2000枚の画像に対し、**DINOv2** を用いて埋め込みベクトルを作成。
   - 同時に画像のサムネイル（小さい画像）を生成。
   - オリジナル画像とサムネイルはAWS S3にアップロード。

2. **データ保存**  
   - 生成した埋め込みベクトルとS3上の画像URLをAWS DynamoDBに保存。

3. **検索処理**  
   - フロントエンド（React）で画像をアップロードすると、バックエンドでプレイ用のサムネイルと埋め込みベクトルが作成される。
   - DynamoDBからランダムに200枚分のデータを選出し、アップロード画像とのコサイン類似度を計算。
   - 画像URLと類似度の情報をフロントに送信。

4. **表示とプレイ**  
   - フロントでは、送信されたURLをもとにS3からサムネイル画像をダウンロード。
   - Matter.jsを用いて、類似度に応じた物理特性（引力・斥力）を付与したサムネイルを描画し、簡単なアプリとしてプレイ可能にします。

5. **デプロイ**  
   - AWS Copilotを使用し、バックエンドサービスと連携するS3バケット、DynamoDBテーブルを自動で作成・管理しています。

---

## 処理の流れ（フローチャート）

```mermaid
flowchart TD
    A[Open Images V7から<br>2000枚の画像取得] --> B[DINOv2による<br>埋め込みベクトル作成]
    B --> C[サムネイル画像作成]
    C --> D[AWS S3にアップロード<br>(オリジナル＆サムネイル)]
    D --> E[AWS DynamoDBに<br>URLと埋め込みベクトル保存]
    E --> F[フロントエンド (React)<br>で画像アップロード]
    F --> G[バックエンドで<br>プレイ用データ作成]
    G --> H[DynamoDBから<br>ランダム200枚データ取得]
    H --> I[アップロード画像との<br>コサイン類似度計算]
    I --> J[画像URLと類似度を<br>フロントに送信]
    J --> K[フロントでS3から<br>サムネイル画像ダウンロード]
    K --> L[Matter.jsで<br>物理シミュレーション描画]
    L --> M[アプリプレイ開始]
app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
