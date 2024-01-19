# audio_recording_python
웹 브라우저를 이용하여 음성을 녹음하고 서버에 저장 후 텍스트를 변환하여 호출한다.
모바일, 태블릿에서는 사용불가
PC에서 크롬 브라우저에서만 마이크 권한을 허용하여 사용 할 수 있다.

# python 필요 라이브러리
pip3 install flask flask_socketio flask_sslify pydub SpeechRecognition

# dockerfile 빌드
docker build -t audio_recording_python .

# docker 실행 (-v 볼륨으로 본인의 환경에 맞게 수정 및 제외한다)
docker run -d -p 0.0.0.0:5000:443/tcp --name audio_recording_python -v /home/python/src:/app/src audio_recording_python



# 도커 자주 쓰는 명령어 

- 도커 이미지와 컨테이너 동시 삭제
docker rm -f audio_recording_python && docker rmi audio_recording_python
- docker 로그 실시간으로 확인
docker logs -f audio_recording_python
