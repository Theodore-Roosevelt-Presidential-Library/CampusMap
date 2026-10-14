import json, numpy as np
S=json.load(open('slice.json'))
segs=np.array([s for k in ('building','building-BUILDING') for s in S[k]])
def dens(pl,step=3):
    out=[]
    for a,b in zip(pl[:-1],pl[1:]):
        a=np.array(a,float); b=np.array(b,float); n=max(1,int(np.ceil(np.linalg.norm(b-a)/step)))
        for t in np.linspace(0,1,n,endpoint=False): out.append(a+(b-a)*t)
    out.append(np.array(pl[-1],float)); return np.array(out)
def ray(p,d,maxd=25):
    best=None
    for x1,y1,x2,y2 in segs:
        e=np.array([x2-x1,y2-y1]); M=np.array([d,-e]).T
        if abs(np.linalg.det(M))<1e-9: continue
        t,s=np.linalg.solve(M,np.array([x1,y1])-p)
        if 0<=s<=1 and -15<t<maxd and (best is None or abs(t)<abs(best)): best=t
    return best
def project(pl, out=0.5):
    P=dens(pl); res=[]
    for i,p in enumerate(P):
        a=P[max(0,i-1)]; b=P[min(len(P)-1,i+1)]; d=b-a; d/=np.linalg.norm(d); n=np.array([-d[1],d[0]])  # left
        t=ray(p,n)
        if t is None: continue
        res.append((p+n*(t+out)).round(2).tolist())
    return res
lobby=[[186.5,213.3],[240.5,213.3],[250.5,211],[271,200],[278.5,193.5],[281.5,185],[281.5,60]]
aud=[[318,132],[321.9,155.3],[327.8,168],[331.7,172.9],[339.9,176],[350.6,173.4],[413.2,156.8]]
out={'lobby':project(lobby),'aud':[p for p in project(aud) if p[0]>325]}
bay=ray(np.array([94.6,205.0]),np.array([0,1.0])); out['bay_wall_y']=round(205+bay,2)
print(len(out['lobby']),len(out['aud']),out['bay_wall_y']); print(out['lobby'][:3],out['lobby'][-3:]); print(out['aud'][:3],out['aud'][-3:])
json.dump(out,open('glazing_ft.json','w'))
