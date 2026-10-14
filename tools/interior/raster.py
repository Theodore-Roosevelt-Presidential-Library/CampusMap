import numpy as np, cv2
K=2; X0,Y1=-30,260; W,H=600*K,330*K
def to_px(x,y): return (np.asarray(x)-X0)*K, (Y1-np.asarray(y))*K
def to_ft(u,v): return np.asarray(u)/K+X0, Y1-np.asarray(v)/K
def wall_raster(pg,th=1):
    s=np.load(f'segft{pg}.npy'); img=np.zeros((H,W),np.uint8)
    u1,v1=to_px(s[:,0],s[:,1]); u2,v2=to_px(s[:,2],s[:,3])
    for i in range(len(s)): cv2.line(img,(int(round(u1[i])),int(round(v1[i]))),(int(round(u2[i])),int(round(v2[i]))),255,th)
    return img
