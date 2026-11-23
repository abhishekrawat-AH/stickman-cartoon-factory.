import os, json, math, subprocess, textwrap, random
from PIL import Image, ImageDraw, ImageFont

W,H=720,1280
FPS=20
BG=(250,250,247); INK=(25,25,30); BLUE=(55,115,220); PINK=(220,85,135)

def font(size,bold=False):
    paths=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def say(text, voice, path):
    v="en-us+m3" if voice=="male" else "en-us+f3"
    subprocess.run(["espeak-ng","-v",v,"-s","158","-a","165","-w",path,text],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def draw_person(d,x,y,scale,color,pose,t):
    head=int(38*scale)
    bob=math.sin(t*5)*5*scale
    cy=int(y-160*scale+bob)
    d.ellipse((x-head,cy-head,x+head,cy+head),outline=color,width=max(4,int(8*scale)))
    # body
    d.line((x,cy+head,x,y),fill=color,width=max(4,int(8*scale)))
    # legs
    swing=math.sin(t*6)*25*scale
    d.line((x,y,x-35*scale-swing,y+75*scale),fill=color,width=max(4,int(8*scale)))
    d.line((x,y,x+35*scale+swing,y+75*scale),fill=color,width=max(4,int(8*scale)))
    # arms
    if pose%3==0:
        d.line((x,cy+head+25*scale,x-55*scale,y+5*scale),fill=color,width=max(4,int(8*scale)))
        d.line((x,cy+head+25*scale,x+55*scale,y+5*scale),fill=color,width=max(4,int(8*scale)))
    elif pose%3==1:
        d.line((x,cy+head+25*scale,x-60*scale,y-30*scale),fill=color,width=max(4,int(8*scale)))
        d.line((x,cy+head+25*scale,x+55*scale,y+20*scale),fill=color,width=max(4,int(8*scale)))
    else:
        d.line((x,cy+head+25*scale,x-45*scale,y+30*scale),fill=color,width=max(4,int(8*scale)))
        d.line((x,cy+head+25*scale,x+45*scale,y+30*scale),fill=color,width=max(4,int(8*scale)))

def wrap(text, f, maxw, draw):
    words=text.split(); lines=[]; cur=""
    for word in words:
        test=(cur+" "+word).strip()
        if draw.textbbox((0,0),test,font=f)[2] <= maxw: cur=test
        else:
            if cur: lines.append(cur)
            cur=word
    if cur: lines.append(cur)
    return lines

def make_frame(path, speaker, text, idx, t, total, topic):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    # simple stage
    d.rounded_rectangle((35,45,W-35,190),radius=28,fill=(235,240,250),outline=(220,225,235),width=3)
    d.text((60,85),"STICKMAN STORY",font=font(32,True),fill=INK)
    d.text((60,140),topic[:38],font=font(22),fill=(90,95,110))
    d.line((40,930,W-40,930),fill=(210,210,210),width=5)
    draw_person(d,250,820,1.25,BLUE,idx,t)
    draw_person(d,500,820,1.25,PINK,idx+1,t+0.8)
    # speech bubble
    f=font(31,True); lines=wrap(text,f,580,d)
    bh=max(110, len(lines)*43+55)
    d.rounded_rectangle((45,260,W-45,260+bh),radius=30,fill="white",outline=(40,40,50),width=4)
    for j,line in enumerate(lines[:4]):
        d.text((75,285+j*43),line,font=f,fill=INK)
    d.text((50,1175),f"{speaker}  •  Episode",font=font(24,True),fill=(95,95,105))
    d.rectangle((40,1230,W-40,1242),fill=(220,220,220))
    d.rectangle((40,1230,40+int((W-80)*min(1,t/max(total,1))),1242),fill=BLUE)
    im.save(path)

def render(kind):
    story=json.load(open(f"output/{kind}_story.json",encoding="utf-8"))
    beats=story["beats"]; os.makedirs("output/frames_"+kind,exist_ok=True)
    audio=[]
    for i,(spk,line) in enumerate(beats):
        voice="male" if spk=="A" else "female"
        ap=f"output/{kind}_{i}.wav"; say(line,voice,ap); audio.append(ap)
    # concatenate audio with ffmpeg concat demuxer
    with open(f"output/{kind}_audio.txt","w") as f:
        for a in audio: f.write("file '"+os.path.abspath(a)+"'\n")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",f"output/{kind}_audio.txt","-ac","2","-ar","44100",f"output/{kind}_audio.wav"],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    # allocate each beat an equal display window; ensure total duration matches audio + pauses
    durations=[]
    for a in audio:
        p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",a],capture_output=True,text=True,check=True)
        durations.append(float(p.stdout.strip()))
    total=sum(durations)
    frame_no=0
    for i,((spk,line),dur) in enumerate(zip(beats,durations)):
        count=max(1,int(dur*FPS))
        for n in range(count):
            t=n/FPS
            make_frame(f"output/frames_{kind}/{frame_no:06d}.jpg",spk,line,i,t,total,story["topic"])
            frame_no+=1
    out=f"output/{kind}.mp4"
    subprocess.run(["ffmpeg","-y","-framerate",str(FPS),"-i",f"output/frames_{kind}/%06d.jpg","-i",f"output/{kind}_audio.wav","-vf","scale=720:1280,format=yuv420p","-c:v","libx264","-preset","ultrafast","-crf","25","-c:a","aac","-b:a","128k","-shortest",out],check=True)
    # thumbnail: use first frame, add readable title
    im=Image.open(f"output/frames_{kind}/000000.jpg").convert("RGB")
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((35,980,685,1150),radius=25,fill=(255,245,180),outline=INK,width=5)
    title=story["topic"][:30]
    d.text((65,1025),title,font=font(34,True),fill=INK)
    im.save(f"output/{kind}_thumbnail.jpg",quality=90)
    meta={"title":f"{story['topic']} | Stickman Cartoon #shorts" if kind=="short" else f"{story['topic']} | Stickman Cartoon Comedy","description":"Original stickman cartoon comedy. New episodes regularly. #stickman #animation #cartoon #comedy","tags":["stickman","animation","cartoon","comedy","funny"]}
    json.dump(meta,open(f"output/{kind}_metadata.json","w"),indent=2)
    print(out,round(total,1),"seconds")

if __name__=="__main__":
    for k in ("short","long"): render(k)
