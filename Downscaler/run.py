import importlib
import subprocess
import sys
import os

# Required Packages Dictionary
REQUIRED_PACKAGES = {
    "cv2": "opencv-python",
    "requests": "requests",
    "ultralytics": "ultralytics",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "multipart": "python-multipart"
}

def verify_and_install_packages():
    print("[System Check] Initializing Python environment inspection...\n")
    missing_packages = []

    for module_name, package_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print(f"[Action Required] Installing {len(missing_packages)} missing packages. Please wait...")
        try:
            # Hide verbose pip logs but show progress
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
            print("\n[Success] All missing packages have been installed automatically!\n")
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Automated installation failed. Exiting.")
            sys.exit(1)
    else:
        print("[All Systems Go] Every required package is already installed.\n")

def execute_main_script(script_name="ds_gpu.py"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_script = os.path.join(current_dir, script_name)
    
    if not os.path.exists(target_script):
        print(f"[ERROR] Target script '{script_name}' not found in: {current_dir}")
        print("Make sure both files are in the same directory.")
        return

    print(f"[Boot Sequence] Handing over execution to '{script_name}'...\n")
    print("=" * 65)
    
    try:
        # Run the target script and let it use the current console window
        subprocess.run([sys.executable, target_script])
    except KeyboardInterrupt:
        print(f"\n[Terminated] '{script_name}' execution stopped by user.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Failed to run '{script_name}': {e}")
        
    print("=" * 65)

# Execution Block
if __name__ == '__main__':
    # 1. Verify packages
    verify_and_install_packages()
    
    # 2. Run script
    execute_main_script("ds_gpu.py")
    
    input("\nPress Enter to exit the launcher...")