"""Area 1 doorway, crate rewards and live POW effect corrections."""
from PIL import Image
import json

POW = ['FEFFC3DFD3FFFEC101003C3C3000013F',
       '804040404040800080C0C0C0C0C08000',
       'DED9DBDBDBD619E6393636363639FFE6',
       'D5555555552AD428ABABABABABD6FC28']
FLASK = ['040403030706060E0707030003020206',
         '3876C4C0C0703C0F0F397B7F7F3F0F00']
STAR = '0000020E16183800000121110907077F'


def doorway(root):
    """Map the complete open exterior frame, including the occluded header."""
    src = Image.open(root/'art/exterior-doorframe-v076.png').convert('RGBA').resize((128,128),Image.Resampling.LANCZOS)
    result = {}
    for frame,ox,oy in [(21720,126,126),(3960,170,30)]:
        for line in (root/f'capture/{frame:05d}.tiles').read_text().splitlines():
            a = line.split(','); layer,x,y,p = int(a[0]),int(a[1]),int(a[2]),int(a[4]); k=a[3]
            if layer == 0 and ox<=x<ox+32 and oy<=y<oy+32 and p==0x0F271505 and k!='0'*32:
                # The first communication entrance has a separate four-tile
                # header; its jambs are shared with the tower door. Repeated
                # side segments share a single continuous jamb texture.
                result.setdefault((k,p),src.crop(((x-ox)*4,(y-oy)*4,(x-ox+8)*4,(y-oy+8)*4)))
    (root/'validation/v076-doorframe-keys.json').write_text(json.dumps([[k,f'{p:08X}']for k,p in result],indent=2)+'\n')
    return result


def items(root, keys, rule):
    sheet=Image.open(root/'art/area1-pow-health-v076.png').convert('RGBA')
    cells=[]
    for i in range(3):
        im=sheet.crop((round(i*sheet.width/3),0,round((i+1)*sheet.width/3),sheet.height))
        im=im.crop(im.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox())
        im=im.resize((64,64),Image.Resampling.LANCZOS)
        cells.append(im)
    render={}
    for i,k in enumerate(POW):
        render[k]=cells[0].crop((i%2*32,i//2*32,i%2*32+32,i//2*32+32))
    # The original flask mirrors one left half. POW's eight-point star mirrors
    # one quadrant in both axes. Leave those live OAM transformations intact.
    for i,k in enumerate(FLASK): render[k]=cells[1].crop((0,i*32,32,i*32+32))
    render[STAR]=cells[2].crop((0,0,32,32))
    grenade=Image.open(root/'art/grenade-v076.png').convert('RGBA')
    grenade=grenade.crop(grenade.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox())
    grenade.thumbnail((32,32),Image.Resampling.LANCZOS)
    bomb=Image.new('RGBA',(32,32));bomb.alpha_composite(grenade,((32-grenade.width)//2,(32-grenade.height)//2))
    render['3C7EFFFFFFFF7E3C3C7EDFFFFFFF7E3C']=bomb
    for k,p in keys:
        if k in render and p>>24==255:
            # All observed damage palettes use the same readable item art;
            # the NES still controls orbit, flashes, collection and expiry.
            rule(k,p,render[k],'!title&!worldmap&!equipment&!radio&!areaClear')
    return render
