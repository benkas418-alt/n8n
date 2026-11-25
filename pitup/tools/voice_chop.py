# Choppiness: short energy dips (50-250 ms, >15 dB under the local speech level) per second of speech.
import sys, numpy as np, librosa
for f in sys.argv[1:]:
    y, sr = librosa.load(f, sr=16000)
    hop = 160; e = librosa.feature.rms(y=y, frame_length=400, hop_length=hop)[0]
    db = 20*np.log10(e+1e-9); ref = np.percentile(db, 90)
    low = db < ref-15; speech = (~low).sum()*hop/sr
    runs=[]; n=0
    for v in low:
        if v: n+=1
        else:
            if n: runs.append(n)
            n=0
    dips=[r for r in runs if 5<=r<=25]
    print(f.split('/')[-1], 'dips/s', round(len(dips)/max(speech,0.1),2), 'speech', round(speech,1))
