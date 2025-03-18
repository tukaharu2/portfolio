import os
import tempfile
import requests
from io import BytesIO
import textwrap
from datetime import datetime

from pydub import AudioSegment
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont



st.markdown(
    """
    <style>
    /* アプリ全体の背景色とテキスト色を変更 */
    .appview-container {
        background-color: #1e1e2f;  /* ダークな背景 */
        color: #ffffff;  /* 白い文字 */
    }
    /* タイトルなどの見出しの色を変更 */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;  /* お好みの色に変更 */
        text-align: center;
    }
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
    display: none !important;
    }
    div[data-testid="stFileUploader"] label, 
    div[data-testid="stSelectbox"] label {
        color: white !important;
    }
    .stDownloadButton > button {
        background-color: #136FFF; 
        width: 250px;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 10px;
        font-size: 18px;
    }
    /* ストリームリットのボタンの色も変更 */
    .stButton > button {
        background-color: #136FFF;
        width: 250px;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 10px;
        font-size: 18px;
    }
    .stButton, .stDownloadButton {
        display: flex;
        justify-content: center;
    }
    .st-emotion-cache-jkfxgf.e1nzilvr5 {
    color: white;  /* 文字色を赤に */
    /*background-color: yellow;  /* 背景色を黄色に */
    }
    /* オーディオプレイヤーの背景色とテキスト色を反転 */
    audio {
    filter: invert(1);
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# 日本語フォントの登録（fonts フォルダに配置しておく）
pdfmetrics.registerFont(TTFont('NotoSansJP', 'fonts/NotoSansJP-VariableFont_wght.ttf'))

API_URL = "http://backend:5000/transcribe"

st.title("🎙音声テキスト変換📄")
st.markdown(
    "<p style='text-align: center; font-size: 16px;'>音声ファイルから文字起こしを行います<br \>二人同時に話している（重なっている）場合でも対応できます</p>",
    unsafe_allow_html=True
)

# ファイルアップローダー
uploaded_file = st.file_uploader("音声ファイルをアップロードしてください (MP3, WAV)", type=["mp3", "wav"])

st.write("")

# セッション状態に文字起こし結果を保持するための初期化
if "transcription_text" not in st.session_state:
    st.session_state.transcription_text = ""

col1, col2 = st.columns(2)
with col1:
    model_size = st.selectbox("モデルサイズ", ["tiny", "small", "turbo"], index=2)
with col2:
    mode_option = st.selectbox(
        "同時話者数（二人の場合音声分離に時間を要します）",
        options=["single", "two"], 
        format_func=lambda x: "一人" if x=="single" else "二人",
        key="mode_option",  # `st.session_state["mode_option"]` に保存
        )

if uploaded_file is not None:
    # MP3の場合、WAVに変換
    if uploaded_file.type == "audio/mp3":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
            temp_mp3.write(uploaded_file.read())
            temp_mp3_path = temp_mp3.name
        audio = AudioSegment.from_mp3(temp_mp3_path)
        # 例として16kHzに変換
        audio = audio.set_frame_rate(16000)
        temp_wav_path = temp_mp3_path.replace(".mp3", ".wav")
        audio.export(temp_wav_path, format="wav")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(uploaded_file.read())
            temp_wav_path = temp_audio.name

    st.audio(temp_wav_path, format="audio/wav")
    
    col1, col2 = st.columns([0.5, 0.5])  # ボタンとスピナーを横並びに配置
    with col1:  
        button_pressed = st.button("文字起こしを開始")  # ボタンはそのまま配置
    
    if button_pressed:    
        with col2, st.spinner("文字起こし中..."):
            files = {"file": (os.path.basename(temp_wav_path), open(temp_wav_path, "rb"), "audio/wav")}
            data = {"model_size": model_size, "mode": mode_option}
            response = requests.post(API_URL, files=files, data=data)

            if response.status_code == 200:
                result = response.json()

                # 🔹 セッションに結果を保存
                st.session_state.result = result
                st.session_state.filename = uploaded_file.name
                st.session_state.exec_mode_option = mode_option
                
                if mode_option == "single":

                    raw_text = result["text"]

                    st.session_state.transcription_text = raw_text

                    # テキストの折り返し処理
                    max_width = 42
                    wrapped_text = textwrap.fill(raw_text, width=max_width)

                    # アップロードされたファイルの情報
                    uploaded_filename = uploaded_file.name  
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  

                    # PDF の作成
                    pdf_buffer = BytesIO()
                    pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
                    pdf_canvas.setFont("NotoSansJP", 12)  # 日本語フォントを適用

                    text_object = pdf_canvas.beginText(50, 750)
                    text_object.setFont("NotoSansJP", 12)

                    # ファイル名と日時を記載
                    text_object.textLine(f"filename : {uploaded_filename}")
                    text_object.textLine(f"timestamp : {timestamp}")

                    # 空ける
                    text_object.textLine("")
                    text_object.textLine("")

                    for line in wrapped_text.split("\n"):
                        text_object.textLine(line)

                    pdf_canvas.drawText(text_object)
                    pdf_canvas.save()
                    pdf_buffer.seek(0)  

                    #  セッションに PDF データを保存
                    st.session_state.pdf_data = pdf_buffer.getvalue()  # `.getvalue()` を使う  

                elif mode_option == "two":

                    raw_text = f"**<span style='color: #CCFFFF;'>話者A :</span>**\n{result['text_A']}\
                                 \n\n**<span style='color: #FFD5EC;'>話者B :</span>**\n{result['text_B']}"
        
                    # セッション状態に結果を保存
                    st.session_state.transcription_text = raw_text

                    wrapped_text_A = textwrap.fill(result["text_A"], width=42)
                    wrapped_text_B = textwrap.fill(result["text_B"], width=42)

                    uploaded_filename = uploaded_file.name  # ファイル名
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 保存日時
                    
                    pdf_buffer = BytesIO()
                    pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
                    pdf_canvas.setFont("NotoSansJP", 12)  # 日本語フォントを適用

                    # テキストオブジェクトで改行処理
                    text_object = pdf_canvas.beginText(50, 750)
                    text_object.setFont("NotoSansJP", 12)

                    text_object.textLine(f"filename : {uploaded_filename}")
                    text_object.textLine(f"timestamp : {timestamp}")

                    text_object.textLine("")
                    text_object.textLine("")

                    text_object.textLine("話者 A:")
                    for line in wrapped_text_A.split("\n"):
                        text_object.textLine(line)
                    text_object.textLine("") 

                    text_object.textLine("話者 B:")
                    for line in wrapped_text_B.split("\n"):
                        text_object.textLine(line)
               
                    pdf_canvas.drawText(text_object)
                    pdf_canvas.save()
                    pdf_buffer.seek(0)

                    st.session_state.pdf_data = pdf_buffer.getvalue() 

if "pdf_data" in st.session_state:
    with col2:
        filename = " "
        if uploaded_file:
            filename = os.path.splitext(uploaded_file.name)[0]
        st.download_button(
            label="📄結果を PDF でダウンロード",
            data=st.session_state.pdf_data,
            file_name="transcription_" + filename + ".pdf",
            mime="application/pdf"
        )

result = st.session_state.get("result", {})

if st.session_state.transcription_text:
    if st.session_state.exec_mode_option == "single":
        
        filename = st.session_state.get("filename")
        st.subheader("変換結果")
        st.markdown(
            f"<p style='text-align: center; font-size: 16px;'>{filename}</p>",
            unsafe_allow_html=True
        )

        # スタイル付きの結果表示
        styled_text = (
        "<div style='"
        "background-color: #3a3a50; padding: 15px; border-radius: 10px; "
        "border: 2px solid #ffffff; margin-top: 10px;'>"
        "<div>{}</div>"
        "</div>"
        ).format(result['text'].replace("\n", "<br>"))

        # HTML を適用
        st.markdown(styled_text, unsafe_allow_html=True)    

    elif st.session_state.exec_mode_option == "two": 

        filename = st.session_state.get("filename")   
        st.subheader("変換結果")
        st.markdown(
            f"<p style='text-align: center; font-size: 16px;'>{filename}</p>",
            unsafe_allow_html=True
        )
        
        styled_text = (
        "<div style='"
        "background-color: #3a3a50; padding: 15px; border-radius: 10px; "
        "border: 2px solid #ffffff; margin-top: 10px;'>"
        "<div style='color: #CCFFFF; font-weight: bold;'>話者 A:</div>"
        "<div style='margin-bottom: 10px;'>{}</div>"
        "<div style='color: #CCFFFF; font-weight: bold;'>話者 B:</div>"
        "<div>{}</div>"
        "</div>"
        ).format(result['text_A'].replace("\n", "<br>"), result['text_B'].replace("\n", "<br>"))

        st.markdown(styled_text, unsafe_allow_html=True)        
