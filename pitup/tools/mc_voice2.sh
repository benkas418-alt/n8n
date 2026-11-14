#!/bin/bash
# "Human" variant of mc_voice.sh (14 Nov): closer to her real recording. Lighter denoise, air restored (+4 dB shelf at 8 kHz),
# short pauses only at sentence ends (0.4 s; none added at commas: her real speech has almost no pause), softer pause dip.
# usage: mc_voice.sh take.wav cut_start cut_end "REF text" out.wav
set -e; S=/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad; cd $S
IN=$1; C0=$2; C1=$3; REF="$4"; OUT=$5; T=$S/tmp/mcv2; mkdir -p $T
python3 tools/wiener_denoise.py $IN $T/dn.wav ${DN:-18} 2.0 >/dev/null
ffmpeg -v error -y -i $T/dn.wav -af "highpass=f=80,afftdn=nr=${NR:-8}:nf=-60:tn=1,equalizer=f=250:t=q:w=1.0:g=-2,equalizer=f=3200:t=q:w=1.2:g=1.5,highshelf=f=8000:g=${AIR:-4},deesser=i=0.4" -ar 48000 -ac 1 -c:a pcm_f32le $T/ch.wav
python3 - $IN $T/ch.wav $C0 $C1 $T/cut.wav <<'EOF'
import sys, numpy as np, soundfile as sf
from scipy.signal import fftconvolve
r,sr=sf.read(sys.argv[1],dtype="float32"); v,_=sf.read(sys.argv[2],dtype="float32"); c0,c1=float(sys.argv[3]),float(sys.argv[4])
x=r[int(5*sr):int(6*sr)]; c=fftconvolve(v[int(4.8*sr):int(6.2*sr)],x[::-1],"valid"); lag=int(np.argmax(np.abs(c)))-int(.2*sr)
if lag: v=np.roll(v,-lag)
seg=v[int(c0*sr):int(c1*sr)].copy(); m=int(.01*sr); seg[:m]*=np.linspace(0,1,m); m=int(.05*sr); seg[-m:]*=np.linspace(1,0,m)
sf.write(sys.argv[5],seg,sr); print("align lag",lag)
EOF
/home/user/fw/bin/python - $T/cut.wav $T/words.json <<'EOF'
import sys, json, numpy as np, soundfile as sf
from faster_whisper import WhisperModel
a,sr=sf.read(sys.argv[1],dtype="float32"); y=np.interp(np.linspace(0,len(a)-1,int(len(a)*16000/sr)),np.arange(len(a)),a).astype(np.float32)
r,_=WhisperModel("medium",compute_type="int8").transcribe(y,language="fr",beam_size=5,word_timestamps=True)
json.dump([(w.word.strip(),w.start,w.end,w.probability) for s in r for w in s.words],open(sys.argv[2],"w"))
EOF
python3 - $T/cut.wav $T/words.json "$REF" $T/plan.json <<'EOF'
# narrative pauses: target silence per punctuation, placed in the first real silence after the word
import sys, json, re, difflib, numpy as np, soundfile as sf
a,sr=sf.read(sys.argv[1],dtype="float32"); W=json.load(open(sys.argv[2])); REF=sys.argv[3]
TGT={"…":.4,"!":.4,".":.42,"?":.42}
F=int(.01*sr); E=20*np.log10(np.array([np.sqrt((a[k:k+F]**2).mean()) for k in range(0,len(a)-F,F)])+1e-9)
norm=lambda t: re.sub(r"[^a-zà-ÿ0-9]","",t.lower())
ref=[(norm(w),w) for w in REF.replace(" ?","?").replace(" :",":").replace("-"," ").replace("'","' ").split()]; ref=[t for t in ref if t[0]]
W=[w2 for w in W for w2 in ([[x,w[1],w[2],w[3]] for x in w[0].split("-") if x] if "-" in w[0] else [w])]
hyp=[norm(w[0]) for w in W]; sm=difflib.SequenceMatcher(None,[t[0] for t in ref],hyp,autojunk=False); pos={}
for b in sm.get_matching_blocks():
    for k in range(b.size): pos[b.a+k]=b.b+k
plan=[]
for i,(tok,raw) in enumerate(ref[:-1]):
    tgt=TGT.get(raw[-1])
    if not tgt or i not in pos or i+1 not in pos: continue
    w0,w1=W[pos[i]],W[pos[i+1]]; i0,i1=int((w0[2]-0.08)*100),int((w1[1]+0.05)*100)+1; k=None; j=i0
    while j<i1 and j<len(E):
        if E[j]<-40:
            r=j
            while r<len(E) and E[r]<-40: r+=1
            if r-j>=4: k=j; break
            j=r
        else: j+=1
    if k is None: print("  no silence after",raw); continue
    q0=q1=k
    while q0>0 and E[q0-1]<-45: q0-=1
    while q1<len(E)-1 and E[q1+1]<-45: q1+=1
    have=(q1-q0+1)/100 if E[k]<-45 else 0.0; add=round(max(0.0,tgt-have),2)
    if add>0.02: plan.append([round(k/100,3),add]); print(f"  pause after {raw:14s} at {k/100:.2f}s +{add}")
json.dump(plan,open(sys.argv[4],"w"))
EOF
python3 tools/punct_pause3.py $T/cut.wav $T/p.wav "$(cat $T/plan.json)" -62 && python3 tools/room_tail.py $T/p.wav $T/r.wav -24 0.35 >/dev/null && /home/user/fw/bin/python tools/level_words.py $T/r.wav $T/lv.wav 2>/dev/null | tail -1 && python3 tools/pause_dip.py $T/lv.wav $OUT 5
