import os
import subprocess

def mass_downscale_videos_gpu(root_dir):
    valid_exts = ('.mp4', '.avi', '.mov', '.mkv', '.wmv')
    target_size = "640:640"
    
    # Folder Check
    if not os.path.exists(root_dir):
        print(f"ERROR! '{root_dir}' Folder not found.")
        return

    print("\n[Ready] Initializing NVIDIA RTX GPU (NVENC) Hardware Accelerator...")

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
                
                print(f"\n[Work began] GPU Encoding: {input_path}")
                
                # FFmpeg GPU 가속 명령어 (NVENC)
                cmd = [
                    'ffmpeg', 
                    '-y',                      # 덮어쓰기 허용
                    '-hwaccel', 'cuda',        # CUDA 가속 활성화
                    '-i', input_path, 
                    '-vf', f'scale={target_size}', # 리사이즈
                    '-c:v', 'h264_nvenc',      # 3080 Ti 하드웨어 인코더 사용
                    '-preset', 'p6',           # 속도/품질 밸런스 
                    '-c:a', 'copy',            # 오디오는 연산 안 하고 그대로 복사
                    output_path
                ]
                
                try:
                    # 프로세스 실행 (에러 나기 전까지 FFmpeg 로그 화면에 안 띄움)
                    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    
                    # Corruption check & File replacement
                    if result.returncode == 0:
                        os.remove(input_path)
                        final_path = os.path.join(dirpath, f"{name_without_ext}.mp4")
                        os.rename(output_path, final_path)
                        print(f" [Completed] GPU encoded. Original deleted & renamed: {file}")
                    else:
                        # FFmpeg 에러 발생 시 원인 출력
                        err_msg = result.stderr.decode('utf-8', errors='ignore').split('\n')[-2]
                        print(f"ERROR! FFmpeg failed for {file}. Reason: {err_msg}")
                        if os.path.exists(output_path):
                            os.remove(output_path)
                            
                except FileNotFoundError:
                    print("ERROR! FFmpeg is not installed or not in System PATH! (Run 'winget install ffmpeg' in cmd)")
                    return
                except Exception as e:
                    print(f"ERROR! Process failed for {file}: {e}")

    if found_videos == 0:
        print("\nERROR! No video files found or _ds files already exist!")
    else:
        print("\n[All Tasks Finished] GPU NVENC processing completed.")

# =====================================================================
# Execution Block
# =====================================================================
if __name__ == '__main__':
    # Target Folder
    TARGET_FOLDER = os.path.dirname(os.path.abspath(__file__))
    
    print("GPU Downscaling bot started...")
    mass_downscale_videos_gpu(TARGET_FOLDER)