from flask import Flask, render_template, Response, request, jsonify
import cv2

app = Flask(__name__)

# --- [카메라 세팅] ---
# 0은 노트북에 달린 기본 웹캠을 의미합니다.
# 나중에 안 쓰는 스마트폰을 연결할 때는 스마트폰의 'IP Webcam' 주소를 여기에 넣습니다.
# 예: camera = cv2.VideoCapture("http://192.168.0.12:8080/video")
camera = cv2.VideoCapture(0)

# --- [영상 스트리밍 로직] ---
def generate_video_stream():
    """카메라에서 프레임을 읽어와서 웹 브라우저로 연속 전송하는 제너레이터"""
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # TODO: 나중에 여기에 YOLOv8 모델을 넣어서 frame 위에 박스를 그릴 겁니다!
            
            # 읽어온 프레임을 화면에 띄울 수 있게 JPEG 포맷으로 인코딩
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            # MJPEG 방식: 이미지를 계속 덮어씌우면서 동영상처럼 보이게 만듦
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# --- [라우터 (API 엔드포인트)] ---
@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """프론트엔드의 <img> 태그가 영상 데이터를 받아가는 주소"""
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    model_type = data.get('model')
    print(f"시스템 로그: {model_type} 모델로 변경을 요청받았습니다.")
    return jsonify({"status": "success", "message": f"{model_type} 모델 적용 완료"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)