import json, subprocess, sys, os
SUF = os.environ.get("SUF", "")   # "_slow": reference stretched to 0.82 tempo, the model copies the calmer pace
S = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
cfg = json.load(open(f"{S}/cfg/scripts_v13.json")); steps, n = sys.argv[1], sys.argv[2]; only = sys.argv[3:] or list(cfg)
for v in only:
    c = cfg[v]
    # throwaway words at both ends: the first word glues onto the prompt, the last one tends to be cut
    txt = "Bon, alors. " + " ".join(c["scenes"]).replace("Lubumbashi", "Louboumbachi") + " Voilà, merci."
    ref_txt = open(f"{S}/{c['reftxt']}").read().strip()
    r = subprocess.run(["/home/user/voxcpm/.venv/bin/python", "-I", f"{S}/tools/vox_cont.py", f"{S}/{c['ref'][:-4]}{SUF}.wav", ref_txt, f"{S}/audio/v13/{v}{SUF}", "", steps, n, txt], capture_output=True, text=True, cwd="/tmp")
    print(v, [l for l in r.stdout.splitlines() if l[:1].isdigit()], r.stderr[-300:] if r.returncode else "", flush=True)
print("VOX13DONE")
