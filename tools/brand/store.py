import sys; sys.path.insert(0,'/home/claude/brand'); from mark import *
OUT='/home/claude/bangguseok-ilju/store'
WHITE=(255,255,255); GRAY=(170,173,178)
caps=[('ss1','방에서 떠나는 세계 일주','러닝머신·계단·자전거가 여행이 됩니다'),
      ('ss2','산림청 100대명산 99곳','실제 등산로 그대로, 계단으로 오르기'),
      ('ss3','계단 오른 만큼 진짜 산을','실제 높이 그래프 · 대피소 · 기온까지'),
      ('ss4','롯데월드타워에서 부르즈 할리파까지','층별 이야기 · 창밖 실제 항공사진'),
      ('ss5','칼로리까지 한눈에','주간·월간 운동 기록')]
def rounded(im, r):
    m=Image.new('L',im.size,0); ImageDraw.Draw(m).rounded_rectangle([0,0,im.size[0]-1,im.size[1]-1],radius=r,fill=255); im.putalpha(m); return im
for i,(f,h,sub) in enumerate(caps,1):
    c=Image.new('RGB',(1080,1920),CH); d=ImageDraw.Draw(c)
    fh=font(70 if len(h)<14 else 58); tw=d.textlength(h,font=fh); d.text(((1080-tw)/2,96),h,font=fh,fill=VT)
    fs=font(38); tw=d.textlength(sub,font=fs); d.text(((1080-tw)/2,206),sub,font=fs,fill=GRAY)
    sh=Image.open(f'/home/claude/test15/{f}.png').convert('RGBA').resize((860,1529),Image.LANCZOS); sh=rounded(sh,44)
    d.rounded_rectangle([110-4,320-4,110+860+3,320+1529+3],radius=48,fill=(52,55,60))
    c.paste(sh,(110,320),sh); c.save(f'{OUT}/screenshot-{i}.png')
# 대표 그림 1024x500
g=Image.new('RGB',(1024,500),CH); d=ImageDraw.Draw(g)
pts=bez((-40,430),(260,520),(420,250),(700,330),60)+bez((700,330),(900,390),(980,160),(1100,120),60)[1:]
stroke(d,pts,10,(44,47,52))
m=mark(300,bg=False); g.paste(m,(70,100),m)
f1=font(92); d.text((410,150),'방구석러너',font=f1,fill=WHITE)
f2=font(40); d.text((414,280),'러닝머신·100대명산 가상코스',font=f2,fill=VT)
f3=font(28); d.text((416,345),'운동한 만큼 실제 길 위를 여행하세요',font=f3,fill=GRAY)
g.save(f'{OUT}/feature-1024x500.png')
print('ok')
