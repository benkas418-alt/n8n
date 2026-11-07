cd /tmp/claude-0/-home-user-n8n/3a1d2361-6d15-5131-aa88-7efcec5ec51a/scratchpad
A=audio/v8; N=audio/v9
python3 tools/motion_mix.py hf/videos/pitup-m-point/assets/bgm.wav motion/point_v.wav "[[\"$N/a0_1.wav\",0.3],[\"$N/a1_1.wav\",2.4],[\"$N/a2_1.wav\",4.5],[\"$N/a3_1.wav\",7.7],[\"$A/mo_1.wav\",13.2],[\"$N/f1_1.wav\",15.9],[\"$N/e1_0.wav\",19.1]]"
python3 tools/motion_mix.py hf/videos/pitup-m-survol/assets/bgm.wav motion/survol_v.wav "[[\"$N/b0_0.wav\",0.4],[\"$N/b1_0.wav\",4.0],[\"$N/b2_1.wav\",8.4],[\"$A/moc_0.wav\",10.2],[\"$N/f1_1.wav\",14.0],[\"$N/e1_0.wav\",17.2]]"
python3 tools/motion_mix.py hf/videos/pitup-m-glass/assets/bgm.wav motion/glass_v.wav "[[\"$N/c0_0.wav\",0.4],[\"$N/c1_0.wav\",3.4],[\"$N/c2_0.wav\",6.3],[\"$N/c3_0.wav\",10.1],[\"$N/b2_1.wav\",12.75],[\"$A/mo_3.wav\",14.55],[\"$N/f1_1.wav\",16.7],[\"$N/e1_0.wav\",19.9]]"
for p in point survol glass; do ffmpeg -v error -y -i livrables/PitUp-Motion-$p.mp4 -i motion/${p}_v.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart livrables/PitUp-Motion-$p-voix.mp4; done
ls -la livrables/PitUp-Motion-*; echo FINALDONE
