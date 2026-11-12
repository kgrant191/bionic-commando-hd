"""Live equipment icons and a menu surround anchored to native UI positions."""
import numpy as np
from PIL import Image,ImageDraw,ImageFont

def make_equipment(root,out,indices,scale):
    es=[l.split(',')for l in (root/'capture/ui/equipment.tiles').read_text().splitlines()]
    conditions=['<condition>equipment,tileAtPosition,32,56,00001E3F3F3E3C1800001E3121262418,0F201510,N',
                '<condition>equipmentEndXMin,positionCheckX,>=,184',
                '<condition>equipmentEndXMax,positionCheckX,<,216',
                '<condition>equipmentEndYMin,positionCheckY,>=,120',
                '<condition>equipmentEndYMax,positionCheckY,<,136']
    im=Image.new('RGBA',(1024,960),(8,14,18,255));d=ImageDraw.Draw(im)
    d.rounded_rectangle((64,64,960,704),radius=10,fill=(24,34,35),outline=(130,137,122),width=3)
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    d.text((128,112),'EQUIPMENT',font=ImageFont.truetype(font,34),fill=(233,215,164))
    d.text((128,161),'SELECT LOADOUT',font=ImageFont.truetype(font,15),fill=(142,166,163))
    for x,y in [(32,56),(80,56),(128,56),(32,104),(80,104),(176,104)]:
        x+=4;y+=5 # Native icon/cursor bounds begin inside the corner tiles.
        d.rounded_rectangle((x*4,y*4,(x+40)*4,(y+40)*4),radius=10,fill=(7,17,21),outline=(116,137,133),width=4)
        d.line((x*4+17,y*4+8,(x+40)*4-17,y*4+8),fill=(168,173,144),width=2)
    d.text((800,516),'END',anchor='mm',font=ImageFont.truetype(font,28),fill=(235,223,182))
    d.rounded_rectangle((64,704,640,896),radius=8,fill=(24,34,35),outline=(130,137,122),width=3)
    d.rectangle((96,736,608,864),fill=(5,12,15));im.save(out/'equipment.png')
    # Hide only the captured menu's frame/END glyphs. Text introduced by later
    # selections remains live, as do all item sprites and the moving cursor.
    end_keys={(a[3],int(a[4]))for a in es if a[0]=='0'and 184<=int(a[1])<216 and 120<=int(a[2])<136}
    end_keys.discard(('0'*32,0x0F201510))
    hidden={(a[3],int(a[4])):('equipment&equipmentEndXMin&equipmentEndXMax&equipmentEndYMin&equipmentEndYMax'
             if(a[3],int(a[4]))in end_keys else'equipment')for a in es if a[0]=='0'}
    asset=Image.open(root/'art/equipment-lamp-v4.png').convert('RGBA')
    icons={}
    for col,(ox,oy)in enumerate([(32,193),(128,193)]):
        cell=asset.crop((col*512,0,(col+1)*512,1024));ab=cell.getchannel('A').point(lambda a:255 if a>160 else 0).getbbox()
        crop=cell.crop(ab);crop.thumbnail((60,60),Image.Resampling.LANCZOS)
        icon=Image.new('RGBA',(64,64));icon.alpha_composite(crop,((64-crop.width)//2,(64-crop.height)//2))
        for a in es:
            x,y=int(a[1]),int(a[2])
            if a[0]=='1' and ox<=x<ox+16 and oy<=y<oy+16:
                icons[a[3],int(a[4])]=icon.crop(((x-ox)*4,(y-oy)*4,(x-ox+8)*4,(y-oy+8)*4))
    cursor_keys={a[3]for a in es if a[0]=='1'and int(a[1])>=176}
    def render(k,p):
        if (k,p)in icons:return icons[k,p]
        if k in cursor_keys and p>>24==255:
            ix=indices(k);a=np.zeros((8,8,4),np.uint8);a[ix>0]=[234,193,87,255]
            return scale(Image.fromarray(a))
    return conditions,['[equipment]<background>equipment.png,1,0,0,10'],hidden,render
