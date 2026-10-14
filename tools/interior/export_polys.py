import numpy as np, cv2, json
from raster import *
from seg import fp_mask, wall_raster
from classify import web_masks
from common import ft2cm
pub=np.load('pubF.npy')
fm=fp_mask()>0
beige,white,blue=web_masks()
def polys(mask, eps=1.2, minarea=30):
    m=mask.astype(np.uint8)*255
    cs,hier=cv2.findContours(m,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
    out=[]
    if hier is None: return out
    hier=hier[0]
    for i,c in enumerate(cs):
        if hier[i][3]!=-1: continue
        if cv2.contourArea(c)<minarea: continue
        ring=[cv2.approxPolyDP(c,eps,True)[:,0,:]]
        j=hier[i][2]
        while j!=-1:
            if cv2.contourArea(cs[j])>=8: ring.append(cv2.approxPolyDP(cs[j],eps,True)[:,0,:])
            j=hier[j][0]
        rr=[]
        for r in ring:
            if len(r)<3: continue
            fx,fy=to_ft(r[:,0]+0.5,r[:,1]+0.5)  # pixel centers
            X,_,Z=ft2cm(fx,fy)
            rr.append(np.round(np.stack([X,Z],1),4).tolist())
        if rr: out.append(rr)
    return out
# L1
from raster import to_px
PRIV_RECTS=[(10,55,41,200)]
for x0,y0,x1,y1 in PRIV_RECTS:
    u0,v1=to_px(x0,y0); u1,v0=to_px(x1,y1); pub[int(v0):int(v1),int(u0):int(u1)]=False
floor=pub&fm
bl=cv2.morphologyEx((blue&floor).astype(np.uint8),cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
bl=cv2.morphologyEx(bl,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))>0
bl&=floor
mass=fm&~cv2.dilate(floor.astype(np.uint8),np.ones((2,2),np.uint8)).astype(bool)
mass=cv2.morphologyEx(mass.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))>0
# L2 (manual, feet)
def ftpoly_mask(pts, dx=5.0):
    m=np.zeros((H,W),np.uint8); a=np.array(pts,float); a[:,0]+=dx; u,v=to_px(a[:,0],a[:,1]); cv2.fillPoly(m,[np.stack([u,v],1).round().astype(np.int32)],255); return m>0
plate=ftpoly_mask([(319,110),(331,110),(347,104),(352,73),(385,73),(385,-6),(360,-3),(340,0),(328,4),(321,12),(319,20)])
board=ftpoly_mask([(320.5,20.4),(359,20.4),(359,1.5),(345,2),(333,4),(325,8.5),(321,14)])
recep=ftpoly_mask([(320.5,107),(333,107),(340,103),(340,94),(345,94),(351,88),(351,69),(336,69),(336,80),(320.5,80)])
l2floor=(board|recep)&plate
l2mass=plate&~cv2.dilate(l2floor.astype(np.uint8),np.ones((2,2),np.uint8)).astype(bool)
out={'L1':{'floor':polys(floor),'blue':polys(bl),'mass':polys(mass)},
     'L2':{'plate':polys(plate),'floor':polys(l2floor),'mass':polys(l2mass)}}
for k,v in out.items(): print(k,{a:(len(b),sum(len(r) for p in b for r in p)) for a,b in v.items()})
json.dump(out,open('interior_polys.json','w'))
vis=np.zeros((H,W,3),np.uint8); vis[mass]=(120,120,120); vis[floor]=(255,255,255); vis[bl]=(220,200,170); vis[plate&~l2floor]=(60,60,160); vis[l2floor]=(80,200,80)
cv2.imwrite('layers.png',vis)
