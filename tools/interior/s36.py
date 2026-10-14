import numpy as np, pickle
def segs(pg, wmin=0.35, wmax=0.37, box=None):
    dr=pickle.load(open(f'dr{pg}.pkl','rb')); out=[]
    for g in dr:
        if g['type']!='s' or not (wmin<=(g.get('width') or 0)<=wmax): continue
        for it in g['items']:
            if it[0]=='l': out.append((it[1].x,it[1].y,it[2].x,it[2].y))
            elif it[0]=='c':
                p0,p1,p2,p3=it[1],it[2],it[3],it[4]; prev=(p0.x,p0.y)
                for t in np.linspace(0,1,9)[1:]:
                    x=(1-t)**3*p0.x+3*(1-t)**2*t*p1.x+3*(1-t)*t*t*p2.x+t**3*p3.x
                    y=(1-t)**3*p0.y+3*(1-t)**2*t*p1.y+3*(1-t)*t*t*p2.y+t**3*p3.y
                    out.append((prev[0],prev[1],x,y)); prev=(x,y)
            elif it[0]=='re':
                r=it[1]; out+= [(r.x0,r.y0,r.x1,r.y0),(r.x1,r.y0,r.x1,r.y1),(r.x1,r.y1,r.x0,r.y1),(r.x0,r.y1,r.x0,r.y0)]
            elif it[0]=='qu':
                q=it[1]; P=[q.ul,q.ur,q.lr,q.ll]
                for i in range(4): out.append((P[i].x,P[i].y,P[(i+1)%4].x,P[(i+1)%4].y))
    a=np.array(out)
    if box: x0,y0,x1,y1=box; m=(a[:,[0,2]].min(1)>x0)&(a[:,[0,2]].max(1)<x1)&(a[:,[1,3]].min(1)>y0)&(a[:,[1,3]].max(1)<y1); a=a[m]
    return a
