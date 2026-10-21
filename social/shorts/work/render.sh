#!/bin/bash
set -e
cd /workspace/usethissi/social/shorts/work
ffmpeg -v error -y \
 -i clip1_overwhelmed.mp4 -i clip2_sorting.mp4 -i clip3_sunrise.mp4 -loop 1 -framerate 30 -t 6 -i last3.png \
 -f lavfi -i "aevalsrc='0.10*(sin(2*PI*110*t)+0.7*sin(2*PI*164.81*t)+0.6*sin(2*PI*220*t)+0.4*sin(2*PI*329.63*t))*(0.75+0.25*sin(2*PI*0.25*t))':s=48000:d=38" \
 -filter_complex "\
[0:v]trim=0:10,setpts=PTS-STARTPTS,fps=30,format=yuv420p,setsar=1[a];\
[1:v]setpts=PTS/1.2,trim=0:10,setpts=PTS-STARTPTS,fps=30,format=yuv420p,setsar=1[b];\
[2:v]trim=0:12,setpts=PTS-STARTPTS,fps=30,format=yuv420p,setsar=1[c];\
[3:v]scale=720:1280,boxblur=20:2,eq=brightness=-0.2:saturation=0.6,drawbox=0:0:720:1280:color=0x0a0b14@0.5:t=fill,fps=30,format=yuv420p,setsar=1,trim=0:6,setpts=PTS-STARTPTS[e];\
[a][b][c][e]concat=n=4:v=1:a=0,subtitles=subs.ass:fontsdir=/usr/share/fonts/truetype/sand-box/google/Poppins,format=yuv420p[v];\
[4:a]lowpass=f=900,volume=0.5,afade=t=in:d=1.5,afade=t=out:st=35:d=3,aformat=channel_layouts=stereo[au]" \
 -map "[v]" -map "[au]" -c:v libx264 -profile:v high -preset slow -crf 20 -pix_fmt yuv420p -r 30 -c:a aac -b:a 128k -ar 48000 -movflags +faststart -t 38 ../2026-10-17-pick-by-the-job.mp4
