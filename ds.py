import cv2
import os

def mass_downscale_videos(root_dir, target_size=(640, 640)):
    valid_exts = ('.mp4', '.avi', '.mov', '.mkv', '.wmv')
    
    # Folder Check
    if not os.path.exists(root_dir):
        print(f"ERROR! '{root_dir}' Folder not found.")
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
                
                print(f"\n[Work began] {input_path}")
                
                cap = cv2.VideoCapture(input_path)
                
                # Video check
                if not cap.isOpened():
                    print("ERROR! OCV couldn't find video! Check directory name includes Korean or Japanese init.")
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
                
                # Corruption check
                if frame_count == 0:
                    print("ERROR! File corrupted!")
                    os.remove(output_path) 
                else:
                    print(f" [Completed]{frame_count} frames reduced.")

    if found_videos == 0:
        print("\nERROR! No video files found or _ds files already exist!")


# Target Folder
TARGET_FOLDER = r"C:\Users\Yakko\Desktop\Ai\이상행동 CCTV 영상\06.배회(wander)\inside_croki_01"


print("Downscaling bot started...")
mass_downscale_videos(TARGET_FOLDER, target_size=(640, 640))
