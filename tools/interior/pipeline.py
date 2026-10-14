import numpy as np, cv2, json
import classify
from classify import *
classify.PUBLIC_L1.update(['W122C','W161A','W161B','W185A'])
PUB_WEB=[(460,723),(460,690),(430,735),(490,735),(440,560),(440,640)]
ex=seeds2()+[(f'PUB{i}',)+web2ft(x,y) for i,(x,y) in enumerate(PUB_WEB)]
pub,lab,names,wall,fm=public_mask_L1(extra_seeds=ex)
pub=cv2.morphologyEx(pub.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))>0
np.save('pub1.npy',pub); np.save('lab1.npy',lab); json.dump(names,open('names1.json','w'))
