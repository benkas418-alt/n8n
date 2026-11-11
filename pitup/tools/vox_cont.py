# VoxCPM2 "continuation" cloning: the model hears the reference AND its exact transcript, then continues in the same
# natural rhythm. Whole script in one pass (prosody flows across sentences); more diffusion steps than before.
import sys, time, soundfile as sf
from voxcpm import VoxCPM
ref, ref_text, out, style, steps, n = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6])
text = sys.argv[7]
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
for i in range(n):
    t = time.time(); txt = f"({style}){text}" if style else text
    wav = m.generate(text=txt, prompt_wav_path=ref, prompt_text=ref_text, reference_wav_path=ref, cfg_value=2.0, inference_timesteps=steps)
    sf.write(f"{out}_{i}.wav", wav, m.tts_model.sample_rate); print(i, round(time.time() - t), "s", flush=True)
