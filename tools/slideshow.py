import subprocess,sys,json
def make(imgs,durs,music,start,out,fade=0.6):
    W,H,F=1080,1920,30; args=[]; fil=[]
    for k,(im,d) in enumerate(zip(imgs,durs)):
        n=int((d+fade)*F)
        args+=['-loop','1','-t',str(d+fade),'-i',im]
        fil.append(f"[{k}:v]scale=1188:2112,zoompan=z='min(1+0.0009*on,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={F},setsar=1,format=yuv420p[v{k}]")
    prev='v0'; off=0
    for k in range(1,len(imgs)):
        off+=durs[k-1]; fil.append(f"[{prev}][v{k}]xfade=transition=fade:duration={fade}:offset={off-fade*0 if False else off}[x{k}]"); prev=f'x{k}'
    total=sum(durs)+fade
    a=len(imgs); args+=['-ss',str(start),'-t',str(total),'-i',music]
    fil.append(f"[{a}:a]afade=t=in:d=1,afade=t=out:st={total-1.5}:d=1.5,volume=0.9[a]")
    cmd=['ffmpeg','-v','error','-y']+args+['-filter_complex',';'.join(fil),'-map',f'[{prev}]','-map','[a]','-c:v','libx264','-pix_fmt','yuv420p','-r',str(F),'-c:a','aac','-b:a','192k','-t',str(total),'-movflags','+faststart',out]
    subprocess.run(cmd,check=True)
if __name__=='__main__':
    j=json.loads(sys.argv[1]); make(**j)
