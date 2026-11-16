import sys, os
sys.path.insert(0,'/home/claude/brand'); from mark import *
R='/home/claude/bangguseok-ilju/app/android/app/src/main/res'
dens={'mdpi':1,'hdpi':1.5,'xhdpi':2,'xxhdpi':3,'xxxhdpi':4}
for k,f in dens.items():
    n=int(48*f); mark(n).save(f'{R}/mipmap-{k}/ic_launcher.png')
    mark(n,circle=True).save(f'{R}/mipmap-{k}/ic_launcher_round.png')
    fg=int(108*f); mark(fg,bg=False,pad=0.2).save(f'{R}/mipmap-{k}/ic_launcher_foreground.png')
def splash(w,h,path):
    im=Image.new('RGB',(w,h),CH); m=int(min(w,h)*0.30); mk=mark(m,bg=False)
    im.paste(mk,((w-m)//2,int(h*0.5-m*0.75)),mk); d=ImageDraw.Draw(im)
    f=font(int(min(w,h)*0.075)); t='방구석러너'; tw=d.textlength(t,font=f)
    d.text(((w-tw)/2,h*0.5+m*0.35),t,font=f,fill=(255,255,255))
    f2=font(int(min(w,h)*0.032)); t2='Re:2'; tw=d.textlength(t2,font=f2); d.text(((w-tw)/2,h*0.92),t2,font=f2,fill=MUT)
    im.save(path)
for root,_,files in os.walk(R):
    for fn in files:
        if fn=='splash.png':
            p=os.path.join(root,fn); w,h=Image.open(p).size; splash(w,h,p)
# 웹·스토어용
W='/home/claude/bangguseok-ilju'
mark(192).save(f'{W}/icon-192.png'); mark(512).save(f'{W}/icon-512.png')
os.makedirs(f'{W}/store',exist_ok=True)
ic=Image.new('RGB',(512,512),CH); m=mark(512,round_=0); ic.paste(m,(0,0),m); ic.save(f'{W}/store/icon-512.png')   # 스토어 아이콘: 꽉 찬 정사각(구글이 모서리 둥글게 자름)
print('ok')
