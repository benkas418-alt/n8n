# Builds one 1080x1920 sequence from source segments: [(start, end, slow)], slow > 1.25 uses motion interpolation.
import sys, json, subprocess, os
src, dst, segs = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]); parts = []
for i, (a, b, f) in enumerate(segs):
    p = f"/tmp/seg_{i}.mp4"; vf = f"trim={a}:{b},setpts=PTS-STARTPTS"
    vf += (f",minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1,setpts={f}*PTS,fps=30" if f > 1.25 else f",setpts={f}*PTS,fps=30")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf + ",scale=1080:1920:flags=lanczos", "-an", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", p], check=True); parts.append(p)
open("/tmp/seglist.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "/tmp/seglist.txt", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", dst], check=True)
print(dst, subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst], capture_output=True, text=True).stdout.strip())
