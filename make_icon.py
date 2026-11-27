from PIL import Image, ImageDraw, ImageFilter
import math
K=2; S=1024*K
def s(v): return int(v*K)

# radial-ish gradient background: deep indigo -> magenta -> orange glow
bg=Image.new("RGB",(S,S))
px=bg.load()
for y in range(S):
    for x in range(S):
        t=(x*0.4+y*0.6)/S
        # indigo -> magenta -> orange
        if t<0.55:
            u=t/0.55; a=(49,46,129); b=(192,38,211)
        else:
            u=(t-0.55)/0.45; a=(192,38,211); b=(251,146,60)
        px[x,y]=tuple(int(a[i]+(b[i]-a[i])*u) for i in range(3))
img=bg.convert("RGBA")

# soft glow behind card
glow=Image.new("RGBA",(S,S),(0,0,0,0))
gd=ImageDraw.Draw(glow)
gd.ellipse((s(220),s(220),s(804),s(804)),fill=(255,255,255,70))
glow=glow.filter(ImageFilter.GaussianBlur(s(60)))
img=Image.alpha_composite(img,glow)

# tilted card with shadow
def card_layer():
    L=Image.new("RGBA",(s(520),s(520)),(0,0,0,0))
    d=ImageDraw.Draw(L)
    d.rounded_rectangle((0,0,s(520),s(520)),radius=s(96),fill=(255,255,255,255))
    n=s(460)
    inner=Image.new("RGBA",(n,n))
    ip=inner.load()
    for y in range(n):
        t=y/n
        c=(int(125+(253-125)*t),int(211+(186-211)*t),int(252+(116-252)*t),255)
        for x in range(n): ip[x,y]=c
    idr=ImageDraw.Draw(inner)
    idr.ellipse((s(270),s(60),s(370),s(160)),fill=(255,247,205,255))
    idr.polygon([(0,n),(s(140),s(210)),(s(250),s(360)),(s(330),s(270)),(n,n)],fill=(76,29,149,255))
    idr.polygon([(0,n),(s(90),s(330)),(s(190),n)],fill=(124,58,237,255))
    m=Image.new("L",(n,n),0)
    ImageDraw.Draw(m).rounded_rectangle((0,0,n,n),radius=s(70),fill=255)
    L.paste(inner,(s(30),s(30)),m)
    return L
card=card_layer().rotate(10,resample=Image.BICUBIC,expand=True)
sh=Image.new("RGBA",(S,S),(0,0,0,0))
cx,cy=(S-card.width)//2-s(30),(S-card.height)//2-s(30)
alpha=card.split()[3].point(lambda a:int(a*0.35))
shadow=Image.new("RGBA",card.size,(30,0,60,0)); shadow.putalpha(alpha)
sh.paste(shadow,(cx+s(18),cy+s(26)),shadow)
sh=sh.filter(ImageFilter.GaussianBlur(s(22)))
img=Image.alpha_composite(img,sh)
img.alpha_composite(card,(cx,cy))

# pencil
def pencil():
    W,H=s(620),s(120)
    P=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(P)
    x=0
    d.rounded_rectangle((x,s(4),x+s(70),H-s(4)),radius=s(30),fill=(244,114,182,255)); x+=s(70)   # eraser
    d.rectangle((x,s(4),x+s(40),H-s(4)),fill=(203,213,225,255))                                   # ferrule
    d.rectangle((x+s(12),s(4),x+s(16),H-s(4)),fill=(148,163,184,255))
    d.rectangle((x+s(26),s(4),x+s(30),H-s(4)),fill=(148,163,184,255)); x+=s(40)
    body_end=x+s(380)
    d.rectangle((x,s(4),body_end,H-s(4)),fill=(250,204,21,255))                                   # body
    d.rectangle((x,s(4),body_end,s(36)),fill=(253,224,71,255))
    d.rectangle((x,H-s(32),body_end,H-s(4)),fill=(234,179,8,255))
    x=body_end
    d.polygon([(x,s(4)),(x+s(100),H//2),(x,H-s(4))],fill=(253,230,190,255))                       # wood
    d.polygon([(x+s(70),H//2-s(20)),(x+s(130)-s(30),H//2),(x+s(70),H//2+s(20))],fill=(55,48,163,255)) # tip
    return P
P=pencil().rotate(-45,resample=Image.BICUBIC,expand=True)
psh=Image.new("RGBA",P.size,(20,0,40,0)); psh.putalpha(P.split()[3].point(lambda a:int(a*0.4)))
px0,py0=s(430),s(430)
tmp=Image.new("RGBA",(S,S),(0,0,0,0)); tmp.paste(psh,(px0+s(14),py0+s(20)),psh)
tmp=tmp.filter(ImageFilter.GaussianBlur(s(14)))
img=Image.alpha_composite(img,tmp)
img.alpha_composite(P,(px0,py0))

# sparkles
def spark(cx,cy,r,col=(255,255,255,255)):
    L=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(L)
    pts=[]
    for i in range(8):
        ang=math.pi/4*i-math.pi/2
        rr=r if i%2==0 else r*0.28
        pts.append((cx+rr*math.cos(ang),cy+rr*math.sin(ang)))
    d.polygon(pts,fill=col)
    return L
img=Image.alpha_composite(img,spark(s(185),s(235),s(58)))
img=Image.alpha_composite(img,spark(s(760),s(250),s(40),(255,240,200,255)))
img=Image.alpha_composite(img,spark(s(300),s(760),s(30),(255,255,255,230)))

out=img.convert("RGB").resize((1024,1024),Image.LANCZOS)
import os
for p in ["www/icon-512.png","assets/icon-only.png","assets/icon-foreground.png","assets/icon-background.png"]:
    os.makedirs(os.path.dirname(p),exist_ok=True)
    out.save(p)
print("icons generated")
