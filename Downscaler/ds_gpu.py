import os
import subprocess
import cv2  # [Added] For resolution inspection

def mass_downscale_videos_gpu(root_dir):
    valid_exts = ('.mp4', '.avi', '.mov', '.mkv', '.wmv')
    target_w, target_h = 640, 640
    target_size_str = f"{target_w}:{target_h}"
    
    # Folder Check
    if not os.path.exists(root_dir):
        print(f"ERROR! '{root_dir}' Folder not found.")
        return

    print("\n[Ready] Initializing NVIDIA RTX GPU (NVENC) Hardware Accelerator...")

    found_videos = 0
    skipped_videos = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            ext = os.path.splitext(file)[1].lower()
            name_without_ext = os.path.splitext(file)[0]
            
            if ext in valid_exts:
                if name_without_ext.endswith('_ds'):
                    continue
                
                input_path = os.path.join(dirpath, file)
                
                # Inspect video resolution to avoid re-encoding already processed files.
                try:
                    cap = cv2.VideoCapture(input_path)
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    cap.release()
                    
                    if width == target_w and height == target_h:
                        print(f" [Skipped] Already at target resolution ({width}x{height}): {file}")
                        skipped_videos += 1
                        continue
                except Exception as e:
                    print(f"ERROR! Failed to read video metadata for {file}: {e}")
                    continue
                
                found_videos += 1
                output_file = f"{name_without_ext}_ds.mp4" 
                output_path = os.path.join(dirpath, output_file)
                
                print(f"\n[Work began] GPU Encoding ({width}x{height} -> {target_size_str}): {input_path}")
                
                # FFmpeg GPU accel command (NVENC)
                cmd = [
                    'ffmpeg', 
                    '-y',                      
                    '-hwaccel', 'cuda',        
                    '-i', input_path, 
                    '-vf', f'scale={target_size_str}', 
                    '-c:v', 'h264_nvenc',      
                    '-preset', 'p6',           
                    '-c:a', 'copy',            
                    output_path
                ]
                
                try:
                    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    
                    # Corruption check & File replacement
                    if result.returncode == 0:
                        os.remove(input_path)
                        final_path = os.path.join(dirpath, f"{name_without_ext}.mp4")
                        os.rename(output_path, final_path)
                        print(f" [Completed] GPU encoded. Original deleted & renamed: {file}")
                    else:
                        err_msg = result.stderr.decode('utf-8', errors='ignore').split('\n')[-2]
                        print(f"ERROR! FFmpeg failed for {file}. Reason: {err_msg}")
                        if os.path.exists(output_path):
                            os.remove(output_path)
                            
                except FileNotFoundError:
                    print("ERROR! FFmpeg is not installed or not in System PATH! (Run 'winget install ffmpeg' in cmd)")
                    return
                except Exception as e:
                    print(f"ERROR! Process failed for {file}: {e}")

    if found_videos == 0 and skipped_videos == 0:
        print("\nERROR! No video files found in this directory.")
    else:
        print(f"\n[All Tasks Finished] Processed: {found_videos} | Skipped: {skipped_videos}")

# Execution Block
if __name__ == '__main__':
    TARGET_FOLDER = os.path.dirname(os.path.abspath(__file__))
    print(f"GPU Downscaling bot started in: {TARGET_FOLDER}")
    mass_downscale_videos_gpu(TARGET_FOLDER)
