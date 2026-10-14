import numpy as np, cv2, json, re, pymupdf
from raster import *
from common import sheet2ft
fps=json.load(open('footprints.json'))
def fp_mask():
    m=np.zeros((H,W),np.uint8)
    for fp in fps:
        a=np.array(fp); u,v=to_px(a[:,0],a[:,1]); cv2.fillPoly(m,[np.stack([u,v],1).round().astype(np.int32)],255)
    return m
def labels(pg):
    d=pymupdf.open('plans.pdf'); p=d[pg]; out=[]
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            t=' '.join(s['text'] for s in l['spans']).strip()
            if re.fullmatch(r'[WE]\d{3}[A-Z]?(\.\d)?',t):
                bb=l['bbox']; x,y=sheet2ft((bb[0]+bb[2])/2,(bb[1]+bb[3])/2); out.append((t,float(x),float(y)))
    return out
def segment(pg, door=5):
    w=wall_raster(pg,1)
    wall=cv2.morphologyEx(w,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    fm=fp_mask()
    closed=cv2.dilate(wall,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(door,door)))
    free=((fm>0)&(closed==0)).astype(np.uint8)
    n,lab=cv2.connectedComponents(free,connectivity=4)
    return wall,fm,lab,n
from skimage.segmentation import watershed
def rooms(pg, door=3, extra=()):
    w=wall_raster(pg,1)
    wall=cv2.morphologyEx(w,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    if door>1: wall=cv2.dilate(wall,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(door,door)))
    fm=fp_mask()
    free=(fm>0)&(wall==0)
    L=labels(pg)+list(extra)
    mk=np.zeros((H,W),np.int32); names=['']
    for t,x,y in L:
        u,v=to_px(x,y); u,v=int(round(u)),int(round(v))
        if 0<=u<W and 0<=v<H:
            # snap to nearest free px
            ys,xs=np.nonzero(free[max(0,v-12):v+13,max(0,u-12):u+13])
            if len(xs)==0: continue
            k=np.argmin((xs-12-(0 if u>=12 else u-12))**2+(ys-12)**2)
            vv=max(0,v-12)+ys[k]; uu=max(0,u-12)+xs[k]
            names.append(t); mk[vv,uu]=len(names)-1
    lab=watershed(np.zeros((H,W)),mk,mask=free)
    return lab,names,wall,fm
