import cv2
import os

def mass_downscale_videos(root_dir, target_size=(640, 640)):
    valid_exts = ('.mp4', '.avi', '.mov', '.mkv', '.wmv')
    
    # [방어막 1] 폴더 존재하는지 체크
    if not os.path.exists(root_dir):
        print(f"야!! '{root_dir}' 폴더가 없다. 바탕화면에 진짜 있는 거 맞냐?")
        return

    found_videos = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            ext = os.path.splitext(file)[1].lower()
            name_without_ext = os.path.splitext(file)[0]
            
            if ext in valid_exts:
                if name_without_ext.endswith('_ds'):
                    continue
                
                found_videos += 1
                input_path = os.path.join(dirpath, file)
                output_file = f"{name_without_ext}_ds.mp4" 
                output_path = os.path.join(dirpath, output_file)
                
                print(f"\n[작업 시작] {input_path}")
                
                cap = cv2.VideoCapture(input_path)
                
                # [방어막 2] 영상 제대로 열렸는지 확인 (한글 경로 체크)
                if not cap.isOpened():
                    print("  🚨 [에러] OpenCV가 영상을 못 열었음!! (경로에 한글 섞여있어서 뻗었을 확률 99%)")
                    continue

                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps == 0 or fps != fps:
                    fps = 30.0
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, target_size)
                
                frame_count = 0
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break 
                        
                    resized_frame = cv2.resize(frame, target_size)
                    out.write(resized_frame)
                    frame_count += 1
                    
                cap.release()
                out.release()
                
                # [방어막 3] 0프레임 컷 체크
                if frame_count == 0:
                    print("  🚨 [경고] 영상은 열렸는데 프레임이 0개임. 파일 뽀각난 듯.")
                    os.remove(output_path) 
                else:
                    print(f"  ✅ [완료] 총 {frame_count} 프레임 다이어트 성공.")

    if found_videos == 0:
        print("\n❌ 이 폴더 안에 변환할 영상이 없거나, 전부 이미 '_ds'가 붙어있음.")

# ==========================================
# 니가 불러준 바탕화면 배회 폴더 경로 (r 달아둠)
TARGET_FOLDER = r"C:\Users\Yakko\Desktop\Ai\이상행동 CCTV 영상\06.배회(wander)\inside_croki_01"
# ==========================================

print("다운스케일링 봇 기동 중...")
mass_downscale_videos(TARGET_FOLDER, target_size=(640, 640))