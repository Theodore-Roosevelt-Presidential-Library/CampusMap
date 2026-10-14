import pymupdf, numpy as np, cv2, sys
from common import sheet2ft
a=np.array(sheet2ft(0,0)); bx=np.array(sheet2ft(1,0))-a; by=np.array(sheet2ft(0,1))-a
Mx=np.array([bx,by]).T
def ft2sheet(fx,fy): return np.linalg.solve(Mx,np.array([fx,fy])-a)
def crop(pg, fx0,fy0,fx1,fy1, out, z=3, step=10):
    d=pymupdf.open('plans.pdf'); p=d[pg]
    s0=ft2sheet(fx0,fy1); s1=ft2sheet(fx1,fy0)
    clip=pymupdf.Rect(min(s0[0],s1[0]),min(s0[1],s1[1]),max(s0[0],s1[0]),max(s0[1],s1[1]))
    pix=p.get_pixmap(matrix=pymupdf.Matrix(z,z),clip=clip)
    img=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,pix.n)[:,:,:3].copy()
    for X in range(int(fx0)//step*step,int(fx1)+1,step):
        for Y in range(int(fy0)//step*step,int(fy1)+1,step):
            sx,sy=ft2sheet(X,Y); u=(sx-clip.x0)*z; v=(sy-clip.y0)*z
            if 0<u<img.shape[1] and 0<v<img.shape[0]:
                cv2.circle(img,(int(u),int(v)),3,(255,0,0),-1)
                if X%(2*step)==0 and Y%(2*step)==0: cv2.putText(img,f'{X},{Y}',(int(u)+3,int(v)-3),cv2.FONT_HERSHEY_PLAIN,1.0,(255,0,0),1)
    cv2.imwrite(out,img[:,:,::-1]); print(img.shape)
if __name__=='__main__':
    pg,x0,y0,x1,y1,out=sys.argv[1:7]; crop(int(pg),float(x0),float(y0),float(x1),float(y1),out,z=float(sys.argv[7]) if len(sys.argv)>7 else 3)
