#!/bin/sh
# 사용: sh reels/render.sh <출력폴더>   (make_reel.js 다음에 실행)
set -e
O="$1"; N=$(cat "$O/n.txt"); cd "$O"
E="-c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30"
: > list.txt
ffmpeg -y -loglevel error -framerate 30 -i png/hook.png -vf "format=yuv420p,loop=-1:1,trim=duration=2.4" $E t.mp4 && mv t.mp4 s_h.mp4 && echo "file s_h.mp4" >> list.txt
i=$((N-1)); k=0
while [ $k -lt $N ]; do
  D=2.2; [ $k -eq $((N-1)) ] && D=2.8
  ffmpeg -y -loglevel error -framerate 30 -i png/n$k.png -framerate 30 -i png/b$k.png -filter_complex \
  "[0]format=yuv420p,loop=-1:1,trim=duration=0.7,setpts=PTS-STARTPTS,zoompan=z='max(1.0,1.14-0.14*on/6)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,trim=duration=0.7[a];[1]format=yuv420p,loop=-1:1,trim=duration=$D,setpts=PTS-STARTPTS[b];[a][b]xfade=transition=slideleft:duration=0.15:offset=0.55" $E t.mp4 && mv t.mp4 s_$k.mp4 && echo "file s_$k.mp4" >> list.txt
  k=$((k+1))
done
ffmpeg -y -loglevel error -framerate 30 -i png/end.png -vf "format=yuv420p,loop=-1:1,trim=duration=3,setpts=PTS-STARTPTS,zoompan=z='max(1.0\,1.08-0.08*on/8)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30" $E t.mp4 && mv t.mp4 s_e.mp4 && echo "file s_e.mp4" >> list.txt
ffmpeg -y -loglevel error -f concat -i list.txt -c copy v.mp4
# 시그니처 사운드: 순위 공개마다 '쿵'(저음+금속성), 엔딩에 더블 '쿵'
T=2.4; EXPR=""; k=0
thump(){ echo "(0.9*sin(2*PI*55*(t-$1))*exp(-9*(t-$1))+0.25*sin(2*PI*1320*(t-$1))*exp(-22*(t-$1)))*gte(t,$1)"; }
EXPR=$(thump 0.05)
while [ $k -lt $N ]; do D=2.2; [ $k -eq $((N-1)) ] && D=2.8
  EXPR="$EXPR+$(thump $T)"; T=$(echo "$T+0.55+$D" | bc); k=$((k+1)); done
EXPR="$EXPR+$(thump $T)+$(thump $(echo "$T+0.18"|bc))"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 v.mp4)
ffmpeg -y -loglevel error -f lavfi -i "aevalsrc='0.6*($EXPR)':s=44100:d=$DUR" -ac 2 sfx.wav
ffmpeg -y -loglevel error -i v.mp4 -i sfx.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest final.mp4
echo "$O/final.mp4 $DUR"
