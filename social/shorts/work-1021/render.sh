#!/bin/bash
set -e
cd /workspace/usethissi/social/shorts/work-1021
ffmpeg -v error -y -i clip.mp4 \
 -f lavfi -i "aevalsrc='0.10*(sin(2*PI*110*t)+0.7*sin(2*PI*164.81*t)+0.6*sin(2*PI*220*t)+0.4*sin(2*PI*329.63*t))*(0.75+0.25*sin(2*PI*0.25*t))':s=48000:d=14" \
 -filter_complex "\
[0:v]trim=0:14,setpts=PTS-STARTPTS,fps=30,scale=720:1280,setsar=1,\
drawbox=0:0:720:1280:color=0x0a0b14@0.72:t=fill:enable='gte(t,10.8)',\
subtitles=subs.ass:fontsdir=/usr/share/fonts/truetype/sand-box/google/Poppins,format=yuv420p[v];\
[1:a]lowpass=f=900,volume=0.5,afade=t=in:d=1,afade=t=out:st=12.5:d=1.5,aformat=channel_layouts=stereo[au]" \
 -map "[v]" -map "[au]" -c:v libx264 -profile:v high -preset slow -crf 20 -pix_fmt yuv420p -r 30 -c:a aac -b:a 128k -ar 48000 -movflags +faststart -t 14 ../2026-10-21-beacon-agent-memory.mp4
