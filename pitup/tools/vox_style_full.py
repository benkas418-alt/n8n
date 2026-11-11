# Clone mode (timbre from the reference) + a tone instruction, whole script in ONE pass so intonation flows across sentences.
import sys, time, soundfile as sf
from voxcpm import VoxCPM
ref, out, steps, text = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
styles = sys.argv[5:]
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
for i, st in enumerate(styles):
    t = time.time()
    wav = m.generate(text=f"({st}){text}", reference_wav_path=ref, cfg_value=2.0, inference_timesteps=steps)
    sf.write(f"{out}_{i}.wav", wav, m.tts_model.sample_rate); print(i, round(time.time() - t), "s", flush=True)
