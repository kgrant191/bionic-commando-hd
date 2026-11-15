"""Shared health indicator styling; native color, count and timing stay live."""
import numpy as np
from PIL import Image
HEALTH='7EC381818181C37E003C7E7E7E7E3C00'
def health_tile(k,p,tile):
    if k!=HEALTH or p>>24!=255:return None
    # Antialiased circular bezel and inset lens, shared by player and enemies.
    yy,xx=np.mgrid[:128,:128];x=(xx+.5)/4;y=(yy+.5)/4
    r=np.sqrt((x-16)**2+(y-16)**2)
    a=np.zeros((128,128,4),dtype='uint8')
    rim=np.clip(170-(x+y)*2.7+45*np.exp(-((x+y-14)/8)**2),45,210)
    a[:,:,:3]=np.stack([rim*.88,rim*.96,rim],axis=2).astype('uint8')
    lens=r<10.8;edge=(r>=10.8)&(r<12.2)
    color=np.array(tile('0000000000000000FFFFFFFFFFFFFFFF',p))[0,0,:3].astype(float)
    light=np.clip(1.22-(x+y)/55,.36,1.2)
    a[lens,:3]=np.clip(color[None,:]*light[lens,None],0,255)
    a[edge,:3]=[18,27,30]
    shine=((x-12)**2+(y-11)**2)<7
    a[shine,:3]=np.clip(a[shine,:3]*.6+np.array([215,242,221])*.4,0,255)
    a[:,:,3]=np.where(r<15.3,255,0)
    return Image.fromarray(a).resize((32,32),Image.Resampling.LANCZOS)
