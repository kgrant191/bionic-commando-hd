"""Palette-aware sprite materials. Keep every original pose and palette flash.

Painted heads and sampled painted materials supplement the exact live CHR masks.
This is a detail pass, not a replacement of the game's animation or geometry.
"""
import hashlib
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy.ndimage import distance_transform_edt, gaussian_filter

# All gameplay palette families observed across the full recording. Portraits
# and map/UI sprites are handled separately and never share this treatment.
FAMILIES={0xFF202A0F,0xFF36150F,0xFF36060F,0xFF302A0F,0xFF30160F,
          0xFF30210F,0xFF30260F,0xFF36062A,0xFF360627}
COLORS={0x20:(215,225,215),0x30:(234,239,223),0x2a:(100,145,46),
        0x36:(227,171,126),0x15:(113,36,71),0x06:(112,41,24),
        0x16:(164,60,37),0x21:(80,144,195),0x26:(224,122,59),
        0x27:(192,117,46),0x0f:(17,23,25)}

class CharacterMaterials:
    def __init__(self,root,indices,scale,tile):
        self.indices=indices;self.scale=scale;self.tile=tile
        # Material swatches sampled from the painted action sheet, resized to
        # wrap gently within each 8x8 source tile without expanding silhouettes.
        a=Image.open(root/'art/action-poses.png').convert('RGB').resize((1536,512),Image.Resampling.LANCZOS)
        self.cloth=np.asarray(a.crop((112,119,133,146)).resize((32,32),Image.Resampling.BICUBIC),dtype=float)
        self.enemy=np.asarray(a.crop((112,382,136,408)).resize((32,32),Image.Resampling.BICUBIC),dtype=float)
        # Face crop from the same painted Spencer. Canonical NES head faces left;
        # Mesen applies the native flip flags when he turns.
        self.head=a.crop((94,61,128,98)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        self.head_keys={'000102F17A797A7E52FFFE8F7E67064E'}
        self.rotated_head_keys={'0C131020202009060C1F1F3F3F3F0F06','0802307878787000383E6E7438180000'}
        self.enemyhead=a.crop((101,319,133,351))
        self.enemyhead_keys={'000000001E1F1F0F000F1F1F1F07120E'}
        import json
        self.enemykeys={k for k,p in json.loads((root/'capture/sprite-keys.json').read_text())if p=='FF36150F'}
        self.herokeys={k for k,p in json.loads((root/'capture/sprite-keys.json').read_text())if p=='FF202A0F'}

    def render(self,key,p):
        if p not in FAMILIES:return None
        ix=self.indices(key)
        orig=self.scale(self.tile(key,p));base=np.asarray(orig).copy()
        # Interpolated material masks use the same scaler as the baseline.
        masks=[]
        for c in range(4):
            rgb=np.zeros((8,8,4),np.uint8);rgb[:,:,:3]=((ix==c)*255)[:,:,None];rgb[:,:,3]=255
            masks.append(np.asarray(self.scale(Image.fromarray(rgb)))[:,:,0]/255.)
        weights=np.stack(masks,2);weights/=np.maximum(weights.sum(2,keepdims=True),1e-6)
        cols=np.array([(0,0,0)]+[COLORS.get((p>>s)&63,(160,160,160))for s in [16,8,0]],float)
        if p==0xFF36060F and key not in self.enemykeys|self.herokeys|self.head_keys|self.rotated_head_keys:
            cols[1]=[214,225,225];cols[2]=[102,125,129]
        rgb=weights@cols
        for c in [1,2,3]:
            mask=weights[:,:,c]>.45
            dist=distance_transform_edt(np.pad(mask,8,mode='edge'))[8:-8,8:-8]
            gy,gx=np.gradient(gaussian_filter(dist,1.2))
            shading=np.clip(.72+.35*(1-np.exp(-dist/2.4))-.20*gx-.24*gy,.48,1.36)
            rgb+=(shading-1)[:,:,None]*weights[:,:,c,None]*cols[c]
        # Soft material relief and fine grain, with no per-tile frame/border.
        alpha=base[:,:,3]/255.;solid=gaussian_filter(np.pad(alpha,4,mode='edge'),1.1)[4:-4,4:-4]
        gy,gx=np.gradient(solid)
        light=np.clip((gx+gy)*15,-12,14)
        seed=int(hashlib.sha256(key.encode()).hexdigest()[:8],16)
        grain=np.random.default_rng(seed).normal(0,1.4,(32,32))
        rgb+=light[:,:,None]+grain[:,:,None]
        if p in {0xFF202A0F,0xFF36150F}:
            tex=self.cloth if p==0xFF202A0F else self.enemy
            lum=tex.mean(2);lum=np.clip((lum-lum.mean())*.85,-34,36)
            rgb+=lum[:,:,None]*weights[:,:,2,None]
        base[:,:,:3]=np.clip(rgb,0,255).astype('uint8')
        if key in self.head_keys:
            # Fit within the original 8x8 head mask, never enlarge the hitbox.
            head=np.asarray(self.head.resize((32,32),Image.Resampling.LANCZOS)).copy()
            if p!=0xFF36060F:head=np.clip(head.astype(float)*[1.15,.72,.65],0,255).astype('uint8')
            base[:,:,:3]=head
        if key in self.enemyhead_keys:
            face=np.asarray(self.enemyhead.resize((32,32),Image.Resampling.LANCZOS)).copy()
            if p!=0xFF36150F:face=np.clip(face.astype(float)*[1.15,.72,.65],0,255).astype('uint8')
            base[:,:,:3]=face
        return Image.fromarray(base)
