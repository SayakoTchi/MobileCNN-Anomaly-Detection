# "pip install opencv-python requests" required before start.
import cv2
import requests
import time

# ================= 설정충 등판 =================
# 1. 웹캠 장치 번호 (첫 번째 USB 웹캠이나 노트북 내장 캠은 국룰 0번임)
WEBCAM_ID = 0 

# 2. USB 테더링으로 묶인 스마트폰의 로컬 IP 주소 및 포트 (일단 테스트용 폰 IP)
PHONE_API_URL = "http://192.168.42.129:5000/predict" 

# 3. 1초에 몇 장 보낼 건지 (기술 검증용이니까 3fps 유지)
TARGET_FPS = 3 
# ===============================================

def stream_and_send():
    print("Starting up Camera.. Please wait..")
    
    # RTSP 주소 대신 숫자 0(웹캠) 던져주면 끝남
    cap = cv2.VideoCapture(WEBCAM_ID)
    
    if not cap.isOpened():
        print("Camera not detected. Check connectivity or access.")
        return

    # 웹캠 기본 프레임 레이트 확인 (보통 30fps 나옴)
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    if original_fps == 0 or original_fps != original_fps: 
        original_fps = 30 
        
    frame_interval = max(1, int(original_fps // TARGET_FPS))
    print(f"Camera detected. OG FPS: {original_fps} -> Target FPS: {TARGET_FPS} (Sending frames every {frame_interval}frames.)")

    count = 0
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Camera feed disconnected. Terminating..")
            break

        # 타겟 FPS에 맞춰서 프레임 솎아내기
        if count % frame_interval == 0:
            
            # 램(메모리)에서 바로 JPG 파일(바이트)로 압축
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
            success, img_encoded = cv2.imencode('.jpg', frame, encode_param)
            
            if success:
                files = {'file': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
                
                try:
                    # 폰으로 전송 (timeout=1 방어막)
                    response = requests.post(PHONE_API_URL, files=files, timeout=1)
                    print(f"[{count} fps] response from phone: {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"Connection to phone ERROR (Check if server is on or check IP address.): {e}")
                    
        count += 1
        
        # [테스트용 꿀팁] 웹캠 화면 PC에서 띄워보고 싶으면 아래 주석 풀어라
        # cv2.imshow('Webcam Test', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    stream_and_send()