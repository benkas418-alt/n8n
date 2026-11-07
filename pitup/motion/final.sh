cd /tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad
A=audio/v8
python3 tools/motion_mix.py hf/videos/pitup-m-point/assets/bgm.wav motion/point_v.wav "[[\"$A/mo_0.wav\",0.3],[\"$A/mo_1.wav\",13.7]]"
python3 tools/motion_mix.py hf/videos/pitup-m-survol/assets/bgm.wav motion/survol_v.wav "[[\"$A/moc_0.wav\",10.2]]"
python3 tools/motion_mix.py hf/videos/pitup-m-glass/assets/bgm.wav motion/glass_v.wav "[[\"$A/mo_2.wav\",12.5],[\"$A/mo_3.wav\",14.55],[\"$A/moc_2.wav\",16.45]]"
for p in point survol glass; do ffmpeg -v error -y -i livrables/PitUp-Motion-$p.mp4 -i motion/${p}_v.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart livrables/PitUp-Motion-$p-voix.mp4; done
ls -la livrables/PitUp-Motion-*; echo FINALDONE
