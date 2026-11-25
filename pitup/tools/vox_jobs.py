# Several VoxCPM2 continuation jobs with one model load.
# usage (voxcpm python): vox_jobs.py jobs.json
# jobs.json: [{"out": "dir/a", "prompt": "p.wav", "prompt_text": "...", "ref": "r.wav",
#              "cfg": 2.0, "steps": 25, "takes": 2, "texts": ["...", "..."]}, ...]
# Writes <out>_<text index>_<take>.wav. A take longer than 0.25 s per character is a runaway: it is logged and skipped.
import sys, json, soundfile as sf
from voxcpm import VoxCPM

m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
sr = m.tts_model.sample_rate
for job in json.load(open(sys.argv[1])):
    for i, text in enumerate(job["texts"]):
        for k in range(job.get("takes", 2)):
            wav = m.generate(text=text, prompt_wav_path=job["prompt"], prompt_text=job["prompt_text"],
                             reference_wav_path=job.get("ref"), cfg_value=job.get("cfg", 2.0),
                             inference_timesteps=job.get("steps", 25))
            dur = len(wav) / sr
            if dur > 0.25 * len(text):
                print(f"RUNAWAY {job['out']}_{i}_{k} {dur:.1f}s", flush=True)
                continue
            sf.write(f"{job['out']}_{i}_{k}.wav", wav, sr)
            print(f"OK {job['out']}_{i}_{k} {dur:.1f}s", flush=True)
