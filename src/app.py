from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_sslify import SSLify
from pydub import AudioSegment
import io
import datetime
import speech_recognition as sr
import os
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 's_k!'
sslify = SSLify(app)
socketio = SocketIO(app)

ROOT_DIR = os.getcwd()
AUDIO_DIR = 'static/audio'
SETTING_AUDIO_DIR = os.path.join(ROOT_DIR, AUDIO_DIR)

@app.route('/')
def index():
    data = []

    # 디렉터리 내의 파일 목록을 가져옵니다.
    for filename in os.listdir(SETTING_AUDIO_DIR):
        if filename.endswith(".txt"):  # .txt 확장자를 가진 파일만 처리
            file_path = os.path.join(SETTING_AUDIO_DIR, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_contents = file.read()
                wav_file_path = os.path.join('audio', filename.replace('_text.txt', '_recording.wav'))
                data.append({
                    'file_id': get_format_id(filename),
                    'file_name': filename,
                    'file_date': get_format_datetime(filename),
                    'file_content': file_contents,
                    'file_path': wav_file_path
                })
    # 정렬 (최신순)
    sorted_list = sorted(data, key=lambda x: x['file_date'], reverse=True)
    return render_template('index.html', ad=sorted_list)  # 클라이언트 사이드 HTML 파일

@socketio.on('audio')
def handle_audio(data):

    if not os.path.exists(SETTING_AUDIO_DIR):
        os.makedirs(SETTING_AUDIO_DIR)  # 디렉토리를 생성

    all_bytes = b''.join(data)
    # 바이트 배열을 오디오 세그먼트로 변환
    audio_segment = AudioSegment.from_file(io.BytesIO(all_bytes), format="webm")

    # 이름 만들기
    year, month, day, hour, minute, second = get_current_datetime()

    ymd_name = f"{year}{month}{day}_{hour}{minute}{second}"
    file_name = f"{ymd_name}_recording.wav"

    print("여기도 체크")
    print(os.path.join(SETTING_AUDIO_DIR, file_name))
    # .wav 형식으로 파일로 저장
    audio_segment.export(os.path.join(SETTING_AUDIO_DIR, file_name), format="wav")

    # 음성 인식
    recognizer = sr.Recognizer()    

    with sr.AudioFile(os.path.join(SETTING_AUDIO_DIR, file_name)) as source:
        audio_data = recognizer.record(source)

    try:
        # Google Web Speech API를 사용하여 텍스트로 변환
        text = recognizer.recognize_google(audio_data, language='ko-KR')
        print("변환된 텍스트: " + text)

        text_name = f"{ymd_name}_text.txt"
        # 변환된 텍스트를 텍스트 파일로 저장
        with open(os.path.join(SETTING_AUDIO_DIR, text_name), "w") as text_file:
            text_file.write(text)

        # 파일 정리
        for filename in os.listdir(SETTING_AUDIO_DIR):

            text_file = os.path.join(SETTING_AUDIO_DIR, filename.replace('_recording.wav', '_text.txt'))
            wav_file = os.path.join(SETTING_AUDIO_DIR, filename.replace('_text.txt', '_recording.wav'))

            if not (os.path.exists(text_file)):
                if os.path.exists(wav_file):
                    os.remove(wav_file)
                continue

    except sr.UnknownValueError:
        print("Google Speech Recognition이 오디오를 이해할 수 없습니다.")
    except sr.RequestError as e:
        print("Google 서비스에 문제가 생겼습니다; {0}".format(e))

    return "처리 완료"

@socketio.on('del')
def delete_audio(data):

    if os.path.exists(os.path.join(SETTING_AUDIO_DIR, f"{data}_text.txt")):
        os.remove(os.path.join(SETTING_AUDIO_DIR, f"{data}_text.txt"))

    if os.path.exists(os.path.join(SETTING_AUDIO_DIR, f"{data}_recording.wav")):
        os.remove(os.path.join(SETTING_AUDIO_DIR, f"{data}_recording.wav"))

def get_current_datetime():
    current_datetime = datetime.datetime.now()
    year = current_datetime.year
    month = current_datetime.strftime("%m")
    day = current_datetime.strftime("%d")
    hour = current_datetime.strftime("%H")
    minute = current_datetime.strftime("%M")
    second = current_datetime.strftime("%S")
    return year, month, day, hour, minute, second

def get_format_datetime(string_date):
    input_string = string_date
    date_part = input_string[:8]
    time_part = input_string[9:15]
    formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
    return formatted_date

def get_format_id(string_date):
    input_string = string_date
    date_part = input_string[:8]
    time_part = input_string[9:15]
    formatted_date = f"{date_part[:4]}{date_part[4:6]}{date_part[6:]}_{time_part[:2]}{time_part[2:4]}{time_part[4:]}"
    return formatted_date

if __name__ == '__main__':
    cert_path = '../ssl/certificate.crt'
    key_path = '../ssl/private.key'
    socketio.run(app, host='0.0.0.0', port=443, allow_unsafe_werkzeug=True, ssl_context=(cert_path, key_path))