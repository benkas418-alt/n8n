# Puts the directed take's timing into a v13 config: scene starts = sentence starts, end card on "Télécharge".
import json, sys, shutil
SP = "/tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad"
v = sys.argv[1]; r = json.load(open(f"{SP}/audio/v13r/{v}.wav.json")); c = json.load(open(f"{SP}/cfg/v13_{v}.json"))
assert len(r["starts"]) == len(c["scenes"])
ew = c.get("end_word", "telecharg"); tel = [w for w in r["words"] if w[0].startswith(ew)][0][1]
c["starts"] = [round(s - 0.12, 3) for s in r["starts"]]   # cut lands just before the first syllable
c["end_card_at"] = round(tel - 0.1, 3); c["vo_end"] = r["end"]
shutil.copy(f"{SP}/audio/v13r/{v}.wav", f"{SP}/audio/v8/v13_{v}.wav")
json.dump(c, open(f"{SP}/cfg/v13_{v}.json", "w"), indent=1, ensure_ascii=False); print(v, c["starts"], c["end_card_at"], c["vo_end"])
