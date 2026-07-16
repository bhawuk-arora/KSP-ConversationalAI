# frontend/rename_assets.py
import os
import shutil

out_dir = os.path.join(os.path.dirname(__file__), "out")
next_dir = os.path.join(out_dir, "_next")
target_dir = os.path.join(out_dir, "next")

if os.path.exists(next_dir):
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.move(next_dir, target_dir)
    print("Renamed _next to next in out folder!")
else:
    print("_next folder not found or already renamed.")

# Search and replace all occurrences of _next with next in output files
for root, dirs, files in os.walk(out_dir):
    for file in files:
        if file.endswith((".html", ".js", ".css", ".json", ".txt")):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Replace paths
                new_content = content.replace("/_next/", "/next/").replace("_next/", "next/")
                
                if new_content != content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Updated paths in: {file}")
            except Exception as e:
                print(f"Error processing {file}: {e}")
