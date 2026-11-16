from PIL import Image, ImageDraw, ImageFont
import math
CH=(27,28,31); CH2=(38,40,44); VT=(215,245,72); MUT=(110,113,120)
FB='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def bez(p0,p1,p2,p3,n=60):
    out=[]
    for i in range(n+1):
        t=i/n; u=1-t
        out.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0], u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
    return out
def stroke(d, pts, w, col):
    """끊김 없는 굵은 선: 점마다 원을 찍어 이음"""
    r=w/2; dense=[]
    for i in range(len(pts)-1):
        (x0,y0),(x1,y1)=pts[i],pts[i+1]; n=max(1,int(math.hypot(x1-x0,y1-y0)/(r*0.25)))
        for j in range(n): dense.append((x0+(x1-x0)*j/n, y0+(y1-y0)*j/n))
    dense.append(pts[-1])
    for x,y in dense: d.ellipse([x-r,y-r,x+r,y+r], fill=col)
def mark(size, bg=True, pad=0.0, round_=0.22, circle=False):
    """방구석러너 표식: 회색 집(방) 문에서 나온 볼트 길이 구불구불 달려 나가 바깥 도착 핀에 닿음"""
    S=size*4; im=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    if bg:
        if circle: d.ellipse([0,0,S-1,S-1], fill=CH)
        else: d.rounded_rectangle([0,0,S-1,S-1], radius=int(S*round_), fill=CH)
    k=S*(1-2*pad); o=S*pad
    P=lambda x,y:(o+x*k, o+y*k)
    w=k*.05
    # 집: 지붕 + 벽 (문 자리는 비움)
    stroke(d,[P(.18,.55),P(.32,.42),P(.46,.55)], w, MUT)
    stroke(d,[P(.22,.52),P(.22,.76),P(.28,.76)], w, MUT)
    stroke(d,[P(.36,.76),P(.42,.76),P(.42,.52)], w, MUT)
    # 길: 문에서 나와 오른쪽 위로 구불구불
    pts=bez(P(.32,.76),P(.32,.90),P(.62,.92),P(.64,.70),40)+bez(P(.64,.70),P(.66,.52),P(.80,.56),P(.76,.36),40)[1:]
    stroke(d, pts, k*.075, VT)
    # 도착 핀 (물방울 모양)
    cx,cy=P(.74,.22); r=k*.095
    d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=VT)
    d.polygon([(cx-r*.82,cy+r*.5),(cx+r*.82,cy+r*.5),(cx,cy+r*1.75)], fill=VT)
    r2=k*.038; d.ellipse([cx-r2,cy-r2,cx+r2,cy+r2], fill=CH if bg else (0,0,0,0))
    return im.resize((size,size), Image.LANCZOS)
def font(sz): return ImageFont.truetype(FB, sz, index=1)
if __name__=='__main__':
    a=mark(512); b=mark(192,circle=True)
    o=Image.new('RGB',(760,540),(240,240,240)); o.paste(a,(10,14),a); o.paste(b,(550,20),b)
    sm=mark(96); o.paste(sm,(560,240),sm); sm=mark(48); o.paste(sm,(580,360),sm)
    o.save('/home/claude/brand/preview.png')
