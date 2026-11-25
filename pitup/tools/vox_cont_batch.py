# Continuation cloning (keeps the speaker's timbre best): a short clean prompt with its exact transcript + a longer
# reference of the same speaker; many texts, n takes each, model loaded once.
# usage: vox_cont_batch.py prompt.wav "prompt text" ref.wav out_prefix n "text 1" "text 2" ...  -> out_prefix_<text>_<take>.wav
import sys, time, soundfile as sf
from voxcpm import VoxCPM
prompt, ptext, ref, out, n = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
for i, text in enumerate(sys.argv[6:]):
    for k in range(n):
        t = time.time()
        wav = m.generate(text=text, prompt_wav_path=prompt, prompt_text=ptext, reference_wav_path=ref, cfg_value=2.0, inference_timesteps=10)
        sf.write(f"{out}_{i}_{k}.wav", wav, m.tts_model.sample_rate); print(i, k, round(time.time() - t), "s", flush=True)
