import numpy as np, cv2, json
from raster import *
from classify import web2ft
from common import ft2cm
from skimage.graph import route_through_array
pub=np.load('pubF.npy')
G={1:(710,699),2:(659,701),3:(567,687),4:(328,726),5:(232,693),6:(232,528),7:(306,528),8:(336,675),9:(554,499),10:(569,576),11:(652,576),12:(659,504),13:(675,422),14:(678,255),15:(567,357),16:(501,378),17:(375,359),18:(303,359),19:(222,421),20:(212,275),21:(364,210),22:(258,169),23:(331,144),24:(534,137),25:(539,210),26:(626,199),27:(655,142),28:(831,139)}
L={'A':(460,723),'B':(460,603),'C':(460,413),'D':(460,174)}
SEQ=['ORIENT',1,2,3,'A',4,5,6,7,8,'B',9,10,11,12,13,14,15,16,'C',17,18,19,20,21,22,23,'D',24,25,26,27,28,'STORE']
EXTRA={'ORIENT':(790,727),'STORE':(960,250)}
def wpx(k): return G.get(k) or L.get(k) or EXTRA[k]
from seg import fp_mask
fm=fp_mask()>0
wr=np.load('webroute_r.npy')&fm
free=pub.astype(np.uint8)
dist=cv2.distanceTransform(free,cv2.DIST_L2,3)
cost=np.where(free>0,1+6/(1+dist),1e6)
cost=np.where(wr, np.where(free>0,0.3,40), cost)
def snap(u,v):
    ys,xs=np.nonzero(free); k=np.argmin((xs-u)**2+(ys-v)**2); return ys[k],xs[k]
pts=[]
for a,b in zip(SEQ[:-1],SEQ[1:]):
    fa=web2ft(*wpx(a)); fb=web2ft(*wpx(b))
    ua,va=to_px(*fa); ub,vb=to_px(*fb)
    s=snap(ua,va); e=snap(ub,vb)
    path,c=route_through_array(cost,s,e,fully_connected=True,geometric=True)
    if c>1e5: print('blocked',a,b)
    pts+= path if not pts else path[1:]
p=np.array(pts)[:,::-1].astype(np.float32)  # u,v
brush=np.zeros(pub.shape,np.uint8)
cv2.polylines(brush,[p.astype(np.int32)],False,1,9)
pub2=(pub|(brush>0))&fm
np.save('pubF.npy',pub2)
ap=cv2.approxPolyDP(p.reshape(-1,1,2),1.5,False)[:,0,:]
fx,fy=to_ft(ap[:,0],ap[:,1]); X,Y,Z=ft2cm(fx,fy,0.6)
json.dump(np.round(np.stack([X,Z],1),4).tolist(),open('route_cm.json','w'))
print(len(p),len(ap))
vis=cv2.cvtColor((free*200).astype(np.uint8),cv2.COLOR_GRAY2BGR)
cv2.polylines(vis,[ap.astype(np.int32)],False,(255,0,0),2)
for k in list(G)+list(L):
    u,v=to_px(*web2ft(*wpx(k))); cv2.putText(vis,str(k),(int(u)-4,int(v)+4),cv2.FONT_HERSHEY_PLAIN,0.8,(0,0,255),1)
cv2.imwrite('route.png',vis)
# stops
stops={}
for k in list(G)+list(L):
    fx,fy=web2ft(*wpx(k)); X,Y,Z=ft2cm(fx,fy,1.0); stops[str(k)]=[round(float(X),3),round(float(Y),3),round(float(Z),3)]
json.dump(stops,open('stops_cm.json','w'))
