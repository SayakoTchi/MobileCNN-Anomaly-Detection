import cv2
import os
from concurrent.futures import ProcessPoolExecutor

# [Worker Function] Process a single video
def process_single_video(input_path):
    target_size = (640, 640)
    dirpath = os.path.dirname(input_path)
    file = os.path.basename(input_path)
    name_without_ext = os.path.splitext(file)[0]
    
    output_file = f"{name_without_ext}_ds.mp4" 
    output_path = os.path.join(dirpath, output_file)
    
    cap = cv2.VideoCapture(input_path)
    
    # Video check
    if not cap.isOpened():
        return f"ERROR! OCV couldn't find video: {file}"

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
    
    # Corruption check & File replacement
    if frame_count == 0:
        if os.path.exists(output_path):
            os.remove(output_path)
        return f"ERROR! File corrupted (0 frames): {file}"
    else:
        try:
            os.remove(input_path)
            final_path = os.path.join(dirpath, f"{name_without_ext}.mp4")
            os.rename(output_path, final_path)
            return f" [Completed] {frame_count} frames reduced. Original deleted & renamed: {file}"
        except Exception as e:
            return f"ERROR! Delete/Rename failed for {file}: {e}"

# =====================================================================
# [Main Function] Collect videos and distribute to workers
# =====================================================================
def mass_downscale_videos_multicore(root_dir, max_workers=12):
    valid_exts = ('.mp4', '.avi', '.mov', '.mkv', '.wmv')
    
    # Folder Check
    if not os.path.exists(root_dir):
        print(f"ERROR! '{root_dir}' Folder not found.")
        return

    # 1. Collect all video files to process
    video_list = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            ext = os.path.splitext(file)[1].lower()
            name_without_ext = os.path.splitext(file)[0]
            
            if ext in valid_exts and not name_without_ext.endswith('_ds'):
                video_list.append(os.path.join(dirpath, file))

    if not video_list:
        print("\nERROR! No video files found or _ds files already exist!")
        return

    print(f"\n[Ready] Found {len(video_list)} videos. Starting multicore processing with {max_workers} threads...")

    # 2. Run multiprocessing (ProcessPoolExecutor)
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(process_single_video, video_list)
        
        for res in results:
            print(res)
            
    print("\n[All Tasks Finished] Multicore processing completed.")

# Execution Block (Required for Windows multiprocessing)
if __name__ == '__main__':
    # Target Folder
    TARGET_FOLDER = r"C:\Users\Yakko\Desktop\Ai\이상행동 CCTV 영상\06.배회(wander)"
    
    print("Multi-core Downscaling bot started...")
    
    # Set max_workers to your CPU thread count (Default: 12)
    mass_downscale_videos_multicore(TARGET_FOLDER, max_workers=12)


print("Downscaling bot started...")
mass_downscale_videos(TARGET_FOLDER, target_size=(640, 640))
