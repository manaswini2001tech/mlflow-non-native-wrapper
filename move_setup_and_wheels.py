import os
import shutil

# Get current directory (should be mlflow_custom)
current_dir = os.path.abspath(os.getcwd())
parent_dir = os.path.dirname(current_dir)

# Move setup.py
setup_path = os.path.join(current_dir, "setup.py")
if os.path.exists(setup_path):
    shutil.move(setup_path, os.path.join(parent_dir, "setup.py"))
    print(f"Moved setup.py to {parent_dir}")
else:
    print("setup.py not found in current directory.")

# Move wheels directory
wheels_path = os.path.join(current_dir, "wheels")
if os.path.exists(wheels_path):
    dest_wheels = os.path.join(parent_dir, "wheels")
    # Remove destination if it already exists to avoid error
    if os.path.exists(dest_wheels):
        shutil.rmtree(dest_wheels)
    shutil.move(wheels_path, dest_wheels)
    print(f"Moved wheels/ to {parent_dir}")
else:
    print("wheels directory not found in current directory.")
