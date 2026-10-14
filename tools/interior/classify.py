import numpy as np, cv2, re
from seg import *
PUBLIC_L1 = set('''W100 W100A W100B W199 W110 W110A W130 W131 W132 W133 W134 W120 W174 W180
W150 W151 W152 W153 W154 W155 W156 W157 W158 W160 W161 W162 W163 W164 W165 W166 W167 W170 W171 W172 W173
W175 W176 W177 W181 W182 W183 W184 W185
E100 E101 E110 E110A E110B E110C E110D E199 E130 E131 E140 E141 E142 E143 E144 E192 E193 E194'''.split())
def public_mask_L1(extra_seeds=()):
    lab,names,wall,fm=rooms(0, extra=extra_seeds)
    pub=np.zeros(lab.shape,bool)
    for i,t in enumerate(names):
        if i==0: continue
        if t in PUBLIC_L1 or t.startswith('PUB'): pub|=(lab==i)
    return pub,lab,names,wall,fm
def web_masks():
    w=cv2.imread('web_warp.png')[:,:,::-1].astype(int)
    beige=(np.abs(w-np.array([234,230,222])).max(2)<=7).astype(np.uint8)
    beige=cv2.morphologyEx(beige,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    white=(w.min(2)>=248)
    blue=(np.abs(w-np.array([191,205,220])).max(2)<=12)
    return beige>0, white, blue
def public_mask_L1b():
    pub,lab,names,wall,fm=public_mask_L1()
    beige,white,blue=web_masks()
    for i,t in enumerate(names):
        if i==0: continue
        c=(lab==i); n=c.sum()
        if n==0: continue
        if (white[c].sum()+blue[c].sum())/n>0.6: pub|=c
    pub&=~beige
    pub=cv2.morphologyEx(pub.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))>0
    return pub,lab,names,wall,fm,blue
import json
_M=np.array(json.load(open('web2ft.json')))
def web2ft(px,py): 
    v=np.array([px,py,1.0])@_M; return float(v[0]),float(v[1])
PRIV_WEB=[(130,200),(130,330),(130,450),(130,600),(140,720),(125,820),(1500,330),(1560,450),(1600,600),(1620,780),(1285,630),(1470,640),(1480,560)]
def seeds():
    ex=[]
    for i,(x,y) in enumerate(PRIV_WEB):
        fx,fy=web2ft(x,y); ex.append((f'PRIV{i}',fx,fy))
    return ex
PRIV_RASTER=[(115,300),(115,380),(115,460),(105,500),(100,430),(98,400),(98,480),(870,330),(880,360),(860,480),(870,520),(815,170),(840,180),(845,300),(855,420)]
def seeds2():
    from raster import to_ft
    ex=seeds()
    for i,(u,v) in enumerate(PRIV_RASTER):
        fx,fy=to_ft(u,v); ex.append((f'PRIVR{i}',float(fx),float(fy)))
    return ex
