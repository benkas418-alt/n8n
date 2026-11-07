# Cuts the cleaned Lubumbashi footage into 1080x1920 shots of at least 2.4 s (short shots in motion-interpolated slow motion).
SRC=real/lushi_clean.mp4; V=story/v
shot(){ n=$1; a=$2; b=$3; d=$(python3 -c "print($b-$a)"); sp=$(python3 -c "print(min(1.0, $d/2.4))")
  if python3 -c "import sys; sys.exit(0 if $sp < 1 else 1)"; then
    ffmpeg -v error -y -ss $a -to $b -i $SRC -an -vf "minterpolate=fps=$(python3 -c "print(int(30/$sp)+1)"):mi_mode=mci:mc_mode=aobmc:vsbmc=1,setpts=PTS/$sp,fps=30,scale=1080:1920:flags=lanczos,format=yuv420p" -c:v libx264 -crf 18 -preset fast $V/$n.mp4
  else
    ffmpeg -v error -y -ss $a -i $SRC -an -t 3.5 -vf "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p" -c:v libx264 -crf 18 -preset fast $V/$n.mp4
  fi; echo -n "$n "; }
shot L1 1.75 2.02; shot L2 2.05 3.80; shot L5 4.15 5.60; shot L8 6.12 6.65; shot L9 6.70 7.80; shot L10 7.85 8.50
shot L11 8.55 9.30; shot L12 9.35 9.80; shot L13 9.85 10.28; shot L14 10.32 10.80; shot L15 10.85 12.68; shot L16 12.72 13.25
shot L17 13.30 13.88; shot L19 14.15 14.95; shot L20 15.00 15.98; shot L23 17.15 17.85; shot L24 17.90 18.15; shot L25 18.20 18.55
shot L26 18.60 19.70; shot L27 19.75 20.65; shot L28 20.70 21.14; shot L29 21.20 22.20; shot L32 22.72 23.20; shot L33 23.25 24.25
shot L35 24.50 24.75; shot L39 26.45 27.40; shot L0 0.00 1.45
