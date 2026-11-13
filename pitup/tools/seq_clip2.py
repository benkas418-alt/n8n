# Like seq_clip.py, but each segment can come from its own file and a landscape source is cropped to 9:16.
# segs: [[file, start, end, slow, cx]]  cx = horizontal centre of the 9:16 crop (0..1), null for a vertical source
import sys, json, subprocess
dst, segs = sys.argv[1], json.loads(sys.argv[2]); parts = []
for i, (src, a, b, f, cx) in enumerate(segs):
    p = f"/tmp/seg2_{i}.mp4"; vf = f"trim={a}:{b},setpts=PTS-STARTPTS"
    if cx is not None: vf += f",crop=ih*9/16:ih:(iw-ih*9/16)*{cx}:0"
    vf += (f",minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1,setpts={f}*PTS,fps=30" if f > 1.25 else f",setpts={f}*PTS,fps=30")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf + ",scale=1080:1920:flags=lanczos", "-an", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", p], check=True); parts.append(p)
open("/tmp/seglist2.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "/tmp/seglist2.txt", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", dst], check=True)
print(dst, subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst], capture_output=True, text=True).stdout.strip())
