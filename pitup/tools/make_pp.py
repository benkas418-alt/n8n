# New phone clips from real pi-tup.com mobile captures (product pages, store page); prices masked.
import subprocess
from PIL import Image, ImageDraw
W,H=780,1688; R='real/pp'
def ease(u): return u*u*(3-2*u)
def out(name,frames,fps=30):
    p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-c:v","libx264","-crf","16","-pix_fmt","yuv420p",f"story/v/{name}.mp4"],stdin=subprocess.PIPE)
    for f in frames: p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait(); print(name)
def prod(n):
    im=Image.open(f'{R}/{n}_view.png').convert('RGB'); ImageDraw.Draw(im).rectangle((40,1336,742,1377),fill='white'); return im
# swipe through products
P=[prod(n) for n in ['tech','sherpa','adidas','pullrl','sneak']]
head=P[0].crop((0,0,W,200)); foot_y=1378
fr=[]
for i,a in enumerate(P):
    fr+= [a]*17
    if i<len(P)-1:
        b=P[i+1]
        for k in range(9):
            u=ease((k+1)/9); x=int(W*u); f=a.copy()
            mid=Image.new('RGB',(W,foot_y-200),'white'); mid.paste(a.crop((0,200,W,foot_y)),(-x,0)); mid.paste(b.crop((0,200,W,foot_y)),(W-x,0))
            f.paste(mid,(0,200)); f.paste(b.crop((0,foot_y,W,H)),(0,foot_y)); fr.append(f)
out('ph_swipe',fr)
# tap on "Acheter maintenant"
s=prod('sneak'); fr=[]
for k in range(90):
    f=s.copy()
    if 40<=k<70:
        u=(k-40)/30; d=ImageDraw.Draw(f,'RGBA'); r=int(20+90*u)
        if k<52: d.rounded_rectangle((404,1410,748,1496),radius=22,fill=(0,0,0,40))
        d.ellipse((576-r,1453-r,576+r,1453+r),fill=(255,255,255,int(150*(1-u))))
    fr.append(f)
out('ph_buy',fr)
# store page: gentle push-in on the real viewport
st=Image.open(f'{R}/store_view.png').convert('RGB'); fr=[]
for k in range(120):
    z=1+0.07*ease(k/119); w,h=int(W/z),int(H/z); x=(W-w)//2; y=int((H-h)*0.35)
    fr.append(st.crop((x,y,x+w,y+h)).resize((W,H),Image.LANCZOS))
out('ph_store',fr)
# desktop store page for the laptop: erase blue price lines, then a smooth vertical pan
import numpy as np
d=Image.open(f'{R}/dstore.png').convert('RGB'); a=np.asarray(d).astype(int)
blue=(a[...,2]>180)&(a[...,0]<110)&(a[...,1]>60)&(a[...,1]<150); blue[:900]=False
dr=ImageDraw.Draw(d); rows=np.where(blue.any(1))[0]
grp=[]; 
for r in rows:
    if grp and r-grp[-1][1]<=3: grp[-1][1]=r
    else: grp.append([r,r])
for y0,y1 in grp:
    cols=np.where(blue[y0:y1+1].any(0))[0]
    # fill per contiguous column run (one per card)
    run=[]; 
    for c in cols:
        if run and c-run[-1][1]<=40: run[-1][1]=c
        else: run.append([c,c])
    for x0,x1 in run:
        reg=a[y0:y1+1,x0:x1+1]; white=((reg>235).all(-1)).mean()
        if y1-y0<=40 and x1-x0<=360 and white>0.45: dr.rectangle((x0-6,y0-6,x1+6,y1+6),fill='white')
print('bands',len(grp))
d.save(f'{R}/dstore_clean.png')
LW,LH=1832,1136; k=LW/d.width; vh=LH/k
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{LW}x{LH}","-r","30","-i","-","-c:v","libx264","-crf","16","-pix_fmt","yuv420p","story/v/lap_store.mp4"],stdin=subprocess.PIPE)
y1=min(d.height-vh,2000)
for i in range(150):
    y=y1*ease(i/149); p.stdin.write(d.resize((LW,LH),Image.LANCZOS,box=(0,y,d.width,y+vh)).tobytes())
p.stdin.close(); p.wait(); print('lap_store')
