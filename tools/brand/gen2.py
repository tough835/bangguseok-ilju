import sys, os, base64, io
sys.path.insert(0,'/home/claude/brand'); from mark import *
FG=Image.open('/home/claude/brand/old_fg_volt.png').convert('RGBA')   # 예전 X 그림(볼트색)
def xmark(n, bg=True, circle=False, zoom=1.5, rr=0.22):
    c=Image.new('RGBA',(n,n),(0,0,0,0)); d=ImageDraw.Draw(c)
    if bg:
        if circle: d.ellipse([0,0,n-1,n-1],fill=CH)
        else: d.rounded_rectangle([0,0,n-1,n-1],radius=int(n*rr),fill=CH)
    s=FG.resize((int(n*zoom),int(n*zoom)),Image.LANCZOS); o=int(n*(zoom-1)/2)
    c.alpha_composite(s.crop((o,o,o+n,o+n))); return c
R='/home/claude/bangguseok-ilju/app/android/app/src/main/res'
for k,f in {'mdpi':1,'hdpi':1.5,'xhdpi':2,'xxhdpi':3,'xxxhdpi':4}.items():
    n=int(48*f); xmark(n).save(f'{R}/mipmap-{k}/ic_launcher.png'); xmark(n,circle=True).save(f'{R}/mipmap-{k}/ic_launcher_round.png')
    FG.resize((int(108*f),)*2,Image.LANCZOS).save(f'{R}/mipmap-{k}/ic_launcher_foreground.png')
def splash(w,h,p):
    im=Image.new('RGB',(w,h),CH); m=int(min(w,h)*0.34); mk=xmark(m,bg=False,zoom=1.5)
    im.paste(mk,((w-m)//2,int(h*0.5-m*0.75)),mk); d=ImageDraw.Draw(im)
    f=font(int(min(w,h)*0.075)); t='방구석러너'; tw=d.textlength(t,font=f); d.text(((w-tw)/2,h*0.5+m*0.35),t,font=f,fill=(255,255,255))
    f2=font(int(min(w,h)*0.032)); tw=d.textlength('Re:2',font=f2); d.text(((w-tw)/2,h*0.92),'Re:2',font=f2,fill=MUT); im.save(p)
for root,_,fs in os.walk(R):
    for fn in fs:
        if fn=='splash.png': p=os.path.join(root,fn); splash(*Image.open(p).size,p)
W='/home/claude/bangguseok-ilju'
xmark(192).save(f'{W}/icon-192.png'); xmark(512).save(f'{W}/icon-512.png')
ic=Image.new('RGB',(512,512),CH); m=xmark(512,rr=0); ic.paste(m,(0,0),m); ic.save(f'{W}/store/icon-512.png')
g=Image.new('RGB',(1024,500),CH); d=ImageDraw.Draw(g)
m=xmark(320,bg=False); g.paste(m,(60,90),m)
d.text((410,150),'방구석러너',font=font(92),fill=(255,255,255)); d.text((414,280),'러닝머신·100대명산 가상코스',font=font(40),fill=VT); d.text((416,345),'운동한 만큼 실제 길 위를 여행하세요',font=font(28),fill=(170,173,178))
g.save(f'{W}/store/feature-1024x500.png')
b=io.BytesIO(); xmark(160,bg=False).save(b,'PNG'); open('/home/claude/brand/boot_b64.txt','w').write(base64.b64encode(b.getvalue()).decode())
print('ok', len(b.getvalue()))
