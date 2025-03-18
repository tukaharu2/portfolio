import io
import os
import base64
import json
from datetime import datetime
import random
import numpy as np
from PIL import Image

import boto3
import torch
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from transformers import AutoImageProcessor, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv


# 環境変数のロード
load_dotenv()

# Flask アプリ設定
app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200 

app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# Flask-Session設定（サーバーサイドセッション）
app.config['SESSION_TYPE'] = 'filesystem'  # 一旦ファイルで管理
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# AWS  設定
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
dynamodb = boto3.resource("dynamodb")
image_table = dynamodb.Table(os.getenv("DYNAMODB_TABLE"))
s3_client = boto3.client("s3")

# DINOv2 モデルの読み込み
processor = AutoImageProcessor.from_pretrained("facebook/dinov2-base")
model = AutoModel.from_pretrained("facebook/dinov2-base")

def compute_embedding(image):
    """画像の埋め込みベクトルを計算"""
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].squeeze(0)
    return embedding.detach().numpy()

def generate_thumbnail(image, size=(40, 40)):
    """画像のサムネイルを生成"""
    thumbnail = image.copy()
    thumbnail.thumbnail(size)
    return thumbnail

def upload_to_s3(file_bytes, s3_key, content_type="image/jpeg"):
    """S3に画像をアップロード"""
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=file_bytes,
        ContentType=content_type
    )
    return f"https://{S3_BUCKET}.s3.ap-northeast-1.amazonaws.com/{s3_key}"

def get_all_items(table):
    items = []
    response = table.scan()
    items.extend(response.get("Items", []))
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))
    return items

# 全件数取得用の関数
def get_total_count(table):
    total_count = 0
    response = table.scan(Select="COUNT")
    total_count += response["Count"]
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"], Select="COUNT")
        total_count += response["Count"]
    return total_count    

def get_img_data(embedding_vector,num_img=200):
    # DynamoDBテーブルから全件取得し、ランダムにnum_img件だけ選ぶ
    results = []

    total_count = get_total_count(image_table)
    print("Total count:", total_count)  # CloudWatch Logsで確認可能

    if total_count > num_img:
        # 全件取得
        all_items = get_all_items(image_table)
        print("All items retrieved:", len(all_items))  # CloudWatch Logsで確認可能

        # シャッフルしてnum_img件だけ選ぶ
        random.shuffle(all_items)
        results = all_items[:num_img]
    else:
        results = image_table.scan(Limit=num_img).get("Items", [])

    # 類似度計算（ただし、ソートせずそのまま返す）
    response_data = []
    for item in results:
        db_embedding = np.array(json.loads(item["embedding"]))
        similarity = cosine_similarity([embedding_vector], [db_embedding])[0][0]
        response_data.append({
            "s3_thumbnail_url": item["s3_thumbnail_url"],
            "s3_fullsize_url": item["s3_fullsize_url"],
            "similarity": similarity
        })

    return jsonify({
        "similar_images": response_data,  # 類似画像リスト
        # "num_total": total_count,
        # "num": len(results)
    })
   

@app.route("/backend", methods=["GET"])
def backend_root():
    return jsonify({"message": "Backend is running"}), 200

@app.route("/backend/upload", methods=["POST"])
def upload_image():
    """画像アップロード時に埋め込みベクトルを計算 & 類似画像リストを返す"""
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    img = Image.open(image).convert("RGB")

    num_img = request.form.get("num_img", "10")  # デフォルト値を設定（例: 10）
    try:
        num_img = int(num_img)  # 文字列を整数に変換
    except ValueError:
        return jsonify({"error": "Invalid num_img value"}), 400  # 無効な値ならエラーを返す    
    
    # 画像のバイナリデータをBase64にエンコードして保存
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # 埋め込みベクトルを計算
    embedding_vector = compute_embedding(img)
    embedding_json = json.dumps(embedding_vector.tolist())

    # 画像データと埋め込みベクトルをセッションに保存
    session["latest_image_info"] = {
        "image_base64": img_base64,
        "embedding_vector": embedding_json
    }

    img_data = get_img_data(embedding_vector, num_img)

    return img_data

    
@app.route("/backend/reload", methods=["POST"])
def reload_image():
    try:
        latest = session.get("latest_image_info")
        if not latest:
            return jsonify({"error": "No uploaded image data found in session"}), 400

        embedding_vector = np.array(json.loads(latest["embedding_vector"]))
        img_data = get_img_data(embedding_vector,num_img=200)

        return img_data

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/backend/save_image", methods=["POST"])
def save_image():
    try:
        latest = session.get("latest_image_info")
        if not latest:
            return jsonify({"error": "No uploaded image data found in session"}), 400

        # 画像データを復元
        image_bytes = base64.b64decode(latest["image_base64"])
        img = Image.open(io.BytesIO(image_bytes))

        # サムネイル生成
        thumbnail = generate_thumbnail(img)

        # オリジナル画像 & サムネイルをS3にアップロード
        image_key = f"fullsize/{session.sid}_original.jpg"
        thumbnail_key = f"thumbnail/{session.sid}_thumbnail.jpg"

        s3_image_url = upload_to_s3(image_bytes, image_key)
        thumbnail_buffer = io.BytesIO()
        thumbnail.save(thumbnail_buffer, format="JPEG")
        s3_thumb_url = upload_to_s3(thumbnail_buffer.getvalue(), thumbnail_key)
        uploaded_at = datetime.utcnow().isoformat()

        # DynamoDB に保存
        image_table.put_item(Item={
            "image_id": session.sid,
            "s3_fullsize_url": s3_image_url,
            "s3_thumbnail_url": s3_thumb_url,
            "embedding": latest["embedding_vector"],
            "uploaded_at": uploaded_at
        })

        # 保存完了後にセッションから削除
        #session.pop("latest_image_info", None)

        return jsonify({
            "message": "Image saved successfully",
            "s3_image_url": s3_image_url,
            "thumbnail_url": s3_thumb_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)