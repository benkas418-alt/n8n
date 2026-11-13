# IPA phone recognition (wav2vec2 xlsr espeak) to check pronunciation word by word, e.g. "vil" vs "vilə".
# usage: phones.py file.wav start end [start end ...]
import sys, json, numpy as np, soundfile as sf, torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2FeatureExtractor
from huggingface_hub import hf_hub_download
M = "facebook/wav2vec2-xlsr-53-espeak-cv-ft"
fe = Wav2Vec2FeatureExtractor.from_pretrained(M); voc = {v: k for k, v in json.load(open(hf_hub_download(M, 'vocab.json'))).items()}
model = Wav2Vec2ForCTC.from_pretrained(M).eval()
a, sr = sf.read(sys.argv[1], dtype="float32"); a = a if a.ndim == 1 else a.mean(1)
t = list(map(float, sys.argv[2:]))
for s, e in zip(t[::2], t[1::2]):
    x = a[int(s * sr):int(e * sr)]; n = int(len(x) * 16000 / sr); x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)
    iv = fe(x, sampling_rate=16000, return_tensors="pt").input_values
    with torch.no_grad(): ids = model(iv).logits.argmax(-1)
    seq = ids[0].tolist(); out = [voc[c] for i, c in enumerate(seq) if (i == 0 or c != seq[i - 1]) and voc[c] not in ('<pad>', '<s>', '</s>', '<unk>')]
    print(f"{s:.2f}-{e:.2f}: {' '.join(out)}")
