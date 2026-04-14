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
                
                # FFmpeg GPU Hardware accel (NVENC)
                cmd = [
                    'ffmpeg', 
                    '-y',                      # Over-write
                    '-hwaccel', 'cuda',        # CUDA accel enable
                    '-i', input_path, 
                    '-vf', f'scale={target_size}', # Resize
                    '-c:v', 'h264_nvenc',      # use Nvidia encoder
                    '-preset', 'p6',           # Speed/Quality balance
                    '-c:a', 'copy',            # No audio
                    output_path
                ]
                
                try:
                    # Run (Nothing shows up before it errors out itself)
                    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    
                    # Corruption check & File replacement
                    if result.returncode == 0:
                        os.remove(input_path)
                        final_path = os.path.join(dirpath, f"{name_without_ext}.mp4")
                        os.rename(output_path, final_path)
                        print(f" [Completed] GPU encoded. Original deleted & renamed: {file}")
                    else:
                        # If FFmpeg fails, logs showing on console
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

# Execution Block
if __name__ == '__main__':
    # Target Folder
    TARGET_FOLDER = os.path.dirname(os.path.abspath(__file__))
    
    print("GPU Downscaling bot started...")
    mass_downscale_videos_gpu(TARGET_FOLDER)
