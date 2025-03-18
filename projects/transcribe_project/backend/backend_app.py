import os
from flask import Flask, request, jsonify
from pydub import AudioSegment
import whisper
from asteroid.models import BaseModel as AsteroidBaseModel


sep_model = AsteroidBaseModel.from_pretrained("mpariente/DPRNNTasNet-ks2_WHAM_sepclean")

#model準備
MODEL_SIZES = ["tiny", "small", "turbo"]
models = {size: whisper.load_model(size) for size in MODEL_SIZES}

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """音声ファイルを受け取り、モードに応じて文字起こしする"""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    model_size = request.form.get('model_size', 'base')
    mode = request.form.get('mode', 'single')  # 'single' または 'two'

    # 一時ファイル保存
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    # モノラル変換後のファイルパス
    mono_file_path = os.path.join("uploads", "mono_" + file.filename)

    try:
        # 音声をロードしてモノラル変換
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_channels(1)  # モノラルに変換
        audio.export(mono_file_path, format="wav")  # WAV 形式で保存
    except Exception as e:
        return jsonify({"error": f"Audio processing failed: {str(e)}"}), 500
    
    if mode == "single":

        model = models[model_size]
        result = model.transcribe(mono_file_path)
        os.remove(file_path)
        os.remove(mono_file_path)

        return jsonify({"text": result['text']})
    elif mode == "two":
        # ファイルを分離（この例では、実行するとカレントディレクトリに <basename>_est1.wav, <basename>_est2.wav が保存される）
        sep_model.separate(mono_file_path, resample=True)
        base_filepath, _ = os.path.splitext(mono_file_path)
        file_A = os.path.join(base_filepath + "_est1.wav")
        file_B = os.path.join(base_filepath + "_est2.wav")
        
        model = models[model_size]
        result_A = model.transcribe(file_A)
        result_B = model.transcribe(file_B)

        # 使用済みの一時ファイルを削除
        os.remove(file_path)
        os.remove(mono_file_path)
        if os.path.exists(file_A):
            os.remove(file_A)
        if os.path.exists(file_B):
            os.remove(file_B)
        
        return jsonify({"text_A": result_A['text'], "text_B": result_B['text']})
    else:
        os.remove(file_path)
        return jsonify({"error": "Invalid mode specified"}), 400

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
