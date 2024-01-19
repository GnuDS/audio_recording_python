FROM python:3.8-slim

COPY . /app

WORKDIR /app/src

RUN apt-get update -y \
    && apt-get install -y ffmpeg
    
RUN pip3 install flask flask_socketio flask_sslify pydub SpeechRecognition

EXPOSE 443

CMD ["python3", "app.py"]