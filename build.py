import PyInstaller.__main__
import os
import sys
import shutil

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_root, "src")
    
    sys.path.insert(0, project_root)
    
    print(f"Building from project root: {project_root}")
    print(f"Source directory: {src_dir}")
    
    PyInstaller.__main__.run([
        os.path.join(src_dir, 'main.py'),
        '--onefile',
        '--name=automation',
        f'--add-data={os.path.join(src_dir, "assets")}:assets',
        f'--add-data={os.path.join(src_dir, "services")}:services',
        f'--add-data={os.path.join(project_root, "t2_data.json")}:.',
        '--paths=' + src_dir,
        '--log-level=INFO'
    ])
    
    dist_dir = os.path.join(project_root, "dist")
    if os.path.exists(dist_dir):
        print(f"Build output directory: {dist_dir}")
        print(f"Contents: {os.listdir(dist_dir)}")
    
    print("Build completed successfully!")

if __name__ == "__main__":
    main()