#!/bin/bash
# Rebuild the Lubumbashi sister voice (v36 cuts and pauses) with a "studio" chain: stronger denoise, no exciter or
# treble boost (they made the sizzle), soft downward expander in the pauses. usage: rebuild_voice_studio.sh out.wav "chain" wet_db
set -e; S=/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad; cd $S; OUT=$1; CH="$2"; WET=${3:--22}
T=$S/tmp/studio; mkdir -p $T
ffmpeg -v error -y -i ${SRC:-audio/v32/soeur_6.wav} -af "$CH" -ar 48000 -ac 1 -c:a pcm_f32le $T/N.wav
python3 - <<'EOF'
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve
S="/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"; T=S+"/tmp/studio"
r,sr=sf.read(f"{S}/audio/v32/soeur_6.wav",dtype="float32"); r=r if r.ndim==1 else r.mean(1); v,_=sf.read(f"{T}/N.wav",dtype="float32")
x=r[int(5*sr):int(6*sr)]; c=fftconvolve(v[int(4.8*sr):int(6.2*sr)],x[::-1],"valid"); lag=int(np.argmax(np.abs(c)))-int(.2*sr); print("offset",lag)
if lag: v=np.roll(v,-lag)
seg=v[int(0.55*sr):int(18.81*sr)].copy(); m=int(.01*sr); seg[:m]*=np.linspace(0,1,m); m=int(.04*sr); seg[-m:]*=np.linspace(1,0,m)
sf.write(f"{S}/audio/v32/soeurV_6.wav",seg,sr)
EOF
python3 tools/assemble_v34.py > $T/a34.log
cp $S/tmp/plan34.bak.json audio/v32/plan34.json   # keep the validated v36 pause plan: same timing as the picture
python3 - <<'EOF'
import numpy as np, soundfile as sf
S="/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad/audio/v32"
a,sr=sf.read(f"{S}/v34_ciel.wav",dtype="float32"); F=int(.01*sr)
E=20*np.log10(np.array([np.sqrt((a[k:k+F]**2).mean()) for k in range(0,len(a)-F,F)])+1e-9)
sp=np.median(E[E>-40]); g=-14.0-sp; a2=a*10**(g/20); pk=np.abs(a2).max()
if pk>0.95: a2*=0.95/pk; g-=20*np.log10(pk/0.95)
E2=E+g; floor=float(np.percentile(E2[E2<sp+g-25],30)); sf.write(f"{S}/v34_cielG.wav",a2,sr); open(f"{S}/floor34.txt","w").write(f"{max(floor,-62):.1f}")
EOF
/home/user/fw/bin/python tools/level_words.py audio/v32/v34_cielG.wav $T/L.wav 2>/dev/null | tail -1
python3 - <<'EOF'
import numpy as np, soundfile as sf
T="/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad/tmp/studio"; T0=0.08
a,sr=sf.read(f"{T}/L.wav",dtype="float32"); a=a.copy()
i0=int((1.045-T0)*sr); i1=int((1.17-T0)*sr); f=int(.02*sr)
a[i0:i1]=0; a[i1:i1+f]*=np.sin(np.linspace(0,np.pi/2,f))**2
sf.write(f"{T}/L2.wav",a,sr)
EOF
FL=$(cat audio/v32/floor34.txt); P=$(python3 -c "import json;print(json.dumps(json.load(open('audio/v32/plan34.json'))['plan']))")
python3 tools/punct_pause3.py $T/L2.wav $T/p.wav "$P" $FL && python3 tools/add_breath.py $T/p.wav $T/b.wav 0.30 0.15 -13 && python3 tools/room_tail.py $T/b.wav $T/r.wav $WET 0.35 && /home/user/fw/bin/python tools/level_words.py $T/r.wav $T/lv.wav 2>/dev/null | tail -1
ffmpeg -v error -y -i $T/lv.wav -af "agate=threshold=0.006:ratio=2.5:range=0.2:attack=8:release=300:knee=4" -c:a pcm_f32le $OUT
cp audio/v32/plan34.json $OUT.map.json
