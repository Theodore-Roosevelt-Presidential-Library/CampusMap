import numpy as np, cv2, json
from skimage.segmentation import watershed
from raster import *
from seg import fp_mask, wall_raster
lab=np.load('lab1.npy'); pub=np.load('pub1.npy')
# fix: W197 cell claiming narrative-corridor bottom; reassign pixels of W197 above plan y=? using website blue/route stops
names=json.load(open('names1.json'))
fm=fp_mask()>0
w=wall_raster(0,1)
wall=cv2.morphologyEx(w,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))>0
free=fm&~wall
mk=np.zeros(lab.shape,np.int32)
mk[pub]=1
mk[(lab>0)&~pub]=2
res=watershed(np.zeros(lab.shape),mk,mask=free)
pubf=(res==1)
np.save('pubF.npy',pubf)
cv2.imwrite('pubF.png',(pubf*200+wall*55).astype(np.uint8))
