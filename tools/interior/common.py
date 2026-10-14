import numpy as np, json
REG=[0.7052178241391996, 1.0, -0.25, 11.045162516431702, 319.5696482422586]
Z=16/72
def pt2ft(xs,ys):
    s,m,ang,tx,ty=REG; a=np.deg2rad(ang)
    u=np.asarray(xs)*Z; v=np.asarray(ys)*Z
    mx=u-tx; my=-(v-ty)
    x=mx*np.cos(a)+my*np.sin(a); y=(-mx*np.sin(a)+my*np.cos(a))*m
    return x,y
# CampusMap transform: feet (x,y,z) -> CM (X,Y,Z)
A=np.array([[25.720819446257327,21.20260734259213],[-21.20260734259213,25.720819446257327]])
T=np.array([2609.6351988962733,1344.5456666231719])
Ainv=np.linalg.inv(A)
def ft2cm(x,y,z=0):
    a=np.stack([np.asarray(x,float)-T[0], -np.asarray(y,float)-T[1]],0)
    X,Zc=Ainv@a.reshape(2,-1)
    return X.reshape(np.shape(x)), (np.asarray(z,float)+38.3)/33.333333333, Zc.reshape(np.shape(x))
_R=json.load(open('sheetreg.json'))
def sheet2ft(x,y):
    R=_R; t=np.deg2rad(R['ang']); c,sn=np.cos(t),np.sin(t); K=R['K']; s=R['s']
    x=np.asarray(x,float); y=np.asarray(y,float)
    u=K*s*(c*x-sn*y)-R['u0']+R['loc'][0]; v=K*s*(sn*x+c*y)-R['v0']+R['loc'][1]
    return u/K+R['X0'], R['Y1']-v/K
