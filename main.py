import os, subprocess
os.makedirs("output",exist_ok=True)
subprocess.run(["python","story_engine.py"],check=True)
subprocess.run(["python","render.py"],check=True)
if os.getenv("AUTO_UPLOAD","false").lower()=="true":
    subprocess.run(["python","upload.py","short","long"],check=True)
