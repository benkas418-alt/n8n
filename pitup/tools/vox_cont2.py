# Continuation from a short clean prompt (exact transcript) + timbre from a separate, longer reference recording.
import sys, time, soundfile as sf
from voxcpm import VoxCPM
prompt, prompt_text, ref, out, steps, n, text = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
for i in range(n):
    t = time.time()
    wav = m.generate(text=text, prompt_wav_path=prompt, prompt_text=prompt_text, reference_wav_path=ref, cfg_value=2.0, inference_timesteps=steps)
    sf.write(f"{out}_{i}.wav", wav, m.tts_model.sample_rate); print(i, round(time.time() - t), "s", flush=True)
