# Sharpens a soft 1080x1920 clip: back to its true detail size (540x960), Real-ESRGAN general x4v3, down to 1080x1920.
# usage: esrgan_clip.py in.mp4 out.mp4 [denoise 0..1]
import sys, subprocess, numpy as np, onnxruntime as ort, time
src, dst = sys.argv[1], sys.argv[2]
so = ort.SessionOptions(); so.intra_op_num_threads = 0
sess = ort.InferenceSession("/root/.cache/esrgan/g4.onnx", so, providers=["CPUExecutionProvider"])
W, H = 540, 960
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"scale={W}:{H}:flags=area", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W*4}x{H*4}", "-r", "30", "-i", "-",
                        "-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", dst], stdin=subprocess.PIPE)
n, t0 = 0, time.time()
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    x = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32).transpose(2, 0, 1)[None] / 255
    y = sess.run(None, {"input": x})[0][0].transpose(1, 2, 0)
    enc.stdin.write((np.clip(y, 0, 1) * 255).astype(np.uint8).tobytes()); n += 1
    if n == 1: print("first frame", round(time.time() - t0, 1), "s", flush=True)
enc.stdin.close(); enc.wait(); print("frames", n, "in", round(time.time() - t0), "s")
