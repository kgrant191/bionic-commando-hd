"""Area 1 fixture, effect and live results-screen replacements from feedback."""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def entries(root, n):
    return [(int(a[0]), int(a[1]), int(a[2]), a[3], int(a[4]), int(a[5]), int(a[6]))
            for a in (line.split(',') for line in
                      (root/f'capture/feedback-v050/{n:05d}.tiles').read_text().splitlines())]


def environment(root, indices, tile):
    result = {}; mapping = {}
    # The reference art uses the displayed 224-row viewport; native tile
    # coordinates still include the eight overscan rows at the top.
    for n, name, regions in [
        (60, 'cave-lift-v5.png', [(0x0F342303, (56, 96, 128, 240)),
                                (0x0F21110B, (88, 64, 128, 96)),
                                (0x0F261606, (120, 96, 160, 120))]),
        (960, 'cave-fixtures-v5.png', [(0x0F342303, (0, 8, 256, 232)),
                                     (0x0F261606, (136, 8, 153, 56)),
                                     (0x0F261606, (136, 164, 153, 232))]),
        (6180, 'reactor-reference-v5.png', [(0x0F332313, (160, 24, 256, 192)),
                                         (0x0F372716, (176, 24, 256, 192)),
                                         (0x0F221202, (0, 96, 24, 144))])]:
        native = np.array(Image.open(root/f'capture/feedback-v050/{n:05d}.png').convert('RGB'))
        art = Image.new('RGBA', (1024, 960), (0, 0, 0, 255))
        art.paste(Image.open(root/'art'/name).convert('RGBA').resize((1024, 896), Image.Resampling.LANCZOS), (0, 32))
        for palette, (x0, y0, x1, y1) in regions:
            locations = {}
            for y in range(y0, min(y1, 233)):
                for x in range(x0, min(x1, 249)):
                    locations.setdefault(native[y:y+8, x:x+8].tobytes(), (x, y))
            for k, p in sorted({(e[3], e[4]) for e in entries(root, n) if e[0] == 0 and e[4] == palette}):
                if len(np.unique(indices(k))) < 2: continue
                xy = locations.get(np.array(tile(k, p).convert('RGB')).tobytes())
                if xy is None: continue
                x, y = xy
                im = art.crop((x*4, y*4, (x+8)*4, (y+8)*4))
                result[k, p] = im
                mapping[f'{k}:{p:08X}'] = [n, x, y, name]
    # Spencer occludes the gate header in the still. Metadata supplies the
    # complete four-by-four native tile grid, including its arrow indicator.
    cave = Image.open(root/'art/cave-lift-v5.png').convert('RGBA').resize((1024,896),Image.Resampling.LANCZOS)
    for ly,x,y,k,p,h,v in entries(root,60):
        if ly==0 and 92<=x<124 and 64<=y<96 and np.any(indices(k)):
            result[k,p]=cave.crop((x*4,(y-8)*4,(x+8)*4,y*4))
            mapping[f'{k}:{p:08X}']=[60,x,y,'cave-lift-v5.png']
    # The final-room entrance uses a two-tile-wide slatted door.
    # Repeated native slats get repeatable metal shutter strips, rather than
    # repeating a full door badge at each occurrence of a shared pattern.
    panel = cave.crop((240,356,432,388)).resize((64,32),Image.Resampling.LANCZOS)
    room = root/'capture/feedback-v050/03660.tiles'
    if room.exists():
        for a in (l.split(',') for l in room.read_text().splitlines()):
            x, y, k, p = int(a[1]), int(a[2]), a[3], int(a[4])
            if a[0] == '0' and 64 <= x < 80 and 160 <= y < 192:
                result[k, p] = panel.crop(((x-64)*4, 0, (x-56)*4, 32))
                mapping[f'{k}:{p:08X}'] = [3660, x, y, 'cave-lift-v5.png']
    (root/'validation/level_polish_mapping.json').write_text(json.dumps(mapping, indent=2)+'\n')
    return result


def fade_palette(p, steps):
    values = [(p >> s) & 255 for s in (24, 16, 8, 0)]
    for _ in range(steps):
        values = [values[0]] + [c-16 if c >= 16 else 15 for c in values[1:]]
    return sum(c << s for c, s in zip(values, (24, 16, 8, 0)))


def fade_aliases(painted):
    aliases = {}
    for k, p in painted:
        if p >> 24 != 15: continue
        for step in (1, 2, 3):
            faded = fade_palette(p, step)
            if faded != p and faded != 0x0F0F0F0F and (k, faded) not in painted:
                aliases.setdefault((k, faded), (p, (0.62, 0.32, 0.12)[step-1]))
    return aliases


def effects(root):
    sheet = Image.open(root/'art/effects-v5.png').convert('RGBA')
    # Generated cells occupy slightly different fractions of the wide atlas.
    cells = [(0, 0, 510, 736), (510, 0, 1090, 736),
             (1090, 0, 1640, 736), (1640, 0, 2208, 736)]
    cells = [tuple(round(v*(sheet.width/2208 if i%2 == 0 else sheet.height/736)) for i,v in enumerate(box)) for box in cells]
    art = []
    for box in cells:
        im = sheet.crop(box); bounds = im.getchannel('A').point(lambda a: 255 if a > 32 else 0).getbbox()
        art.append(im.crop(bounds))
    result = {}
    # Source effect cells are reflected by OAM; cutting only their canonical
    # halves retains the native expanding/contracting animation and timing.
    small = art[0].resize((64, 64), Image.Resampling.LANCZOS)
    large = art[1].resize((128, 96), Image.Resampling.LANCZOS)
    ring = art[2].resize((128, 96), Image.Resampling.LANCZOS)
    patterns = [
        ('00800804030381000018540B04044201', large, 0, 0),
        ('6000037D0100400C110F7C827E012101', large, 0, 32),
        ('0040203218036FF844A4564DE7FC9007', large, 32, 0),
        ('B3373F3F3733189C4CC8C0C0C8CCE763', large, 32, 32),
        ('CF73805C23066048308C7FA3DCF80C04', large, 32, 64),
        ('00102000000182023060414307064408', ring, 0, 0),
        ('0000080C0C4806040008121212909808', ring, 0, 32),
        ('000336E0C01820001F7CC0001C204000', ring, 32, 0),
        ('0040200918130707C1A15D36272C1818', small, 0, 0),
        ('3703090718214000C83C1638275EB1C1', small, 0, 32)]
    for k, im, x, y in patterns: result[k] = im.crop((x,y,x+32,y+32))
    emitter = art[3].resize((64, 96), Image.Resampling.LANCZOS)
    for i, k in enumerate(['3FC73F0203030201C0F83F0302020301', '17F7977717183F751A9AFB78181F0F6C',
                           'F1D94324FBFCC24A38B9E02387BC8075']):
        result[k] = emitter.crop((0, i*32, 32, (i+1)*32))
    result['F1D94324FBFCC45538B9E02387BC806A'] = result['F1D94324FBFCC24A38B9E02387BC8075']
    cave=Image.open(root/'art/cave-lift-v5.png').convert('RGBA').resize((1024,896),Image.Resampling.LANCZOS)
    platform=cave.crop((496,372,624,436))
    for k,x,y in [('FF0000C0C040404000FFFFFFFFFFFFFF',0,0),
                  ('414143C3030704F8FFFFFF3FFFFFFCF8',0,32),
                  ('FF80E0E080E0E08080FFFFFFFFFFFFFF',32,0),
                  ('FFFFFFFFF1F10000FFFF991F11F10000',32,32)]:
        im=platform.crop((x,y,x+32,y+32))
        bits=np.unpackbits(np.frombuffer(bytes.fromhex(k),dtype=np.uint8)).reshape(16,8)
        solid=(bits[:8]+2*bits[8:])>0
        a=np.array(im);a[~np.repeat(np.repeat(solid,4,0),4,1),3]=0
        result[k]=Image.fromarray(a)
    def render(k, p):
        if k not in result or p >> 24 != 255: return None
        im = result[k]
        base = 0xFF30160F
        level = next((i for i in range(1,5) if fade_palette(base, i) == p), 0)
        if level:
            a = np.array(im); a[:,:,:3] = (a[:,:,:3].astype(float)*[1,.62,.32,.12,0][level]).astype('uint8'); im = Image.fromarray(a)
        return im
    return render, len(result)


def area_clear(root, out, keys, indices, scale):
    es = entries(root, 6842)
    # This blank/palette pair is present from the first results-screen frame,
    # before the header types in. Header-based triggers exposed the NES hero
    # during the opening pause. Verified against both Area 1 recordings.
    conditions = ['<condition>areaClear,tileAtPosition,0,0,00000000000000000000000000000000,0F200F0F,N']
    conditions += ['<condition>clearHeaderY0,positionCheckY,>=,40',
                   '<condition>clearHeaderY1,positionCheckY,<,48',
                   '<condition>clearHeaderX0,positionCheckX,>=,88',
                   '<condition>clearHeaderX1,positionCheckX,<,184']
    guard = 'areaClear'
    im = Image.new('RGBA', (1024,960), (7,15,20,255)); d = ImageDraw.Draw(im)
    font = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    mono = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
    d.rounded_rectangle((64,72,960,880), radius=16, fill=(18,31,34), outline=(114,137,131), width=3)
    d.rectangle((65,74,958,77), fill=(205,169,86))
    d.text((104,105),'MISSION DEBRIEF',font=ImageFont.truetype(font,20),fill=(167,190,178))
    d.text((192,176),'AREA',anchor='lm',font=ImageFont.truetype(mono,29),fill=(233,231,211))
    d.text((392,176),'CLEAR',anchor='lm',font=ImageFont.truetype(mono,29),fill=(233,231,211))
    d.line((104,220,918,220),fill=(64,88,89),width=2)
    d.rounded_rectangle((104,260,616,344),radius=8,fill=(9,22,27),outline=(68,93,94),width=2)
    d.rounded_rectangle((104,416,648,600),radius=8,fill=(9,22,27),outline=(68,93,94),width=2)
    d.text((128,384),'RECOVERED SUPPLIES',font=ImageFont.truetype(font,17),fill=(211,177,103))
    d.text((104,824),'BIONIC COMMANDO  /  FIELD OPERATIONS',font=ImageFont.truetype(font,16),fill=(135,160,155))
    hero = Image.open(root/'art/area-clear-spencer-v5.png').convert('RGBA')
    hero = hero.crop(hero.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox())
    hero.thumbnail((318,570), Image.Resampling.LANCZOS)
    im.alpha_composite(hero,(636+(318-hero.width)//2,292)); im.save(out/'area-clear.png')
    glyphs = {}
    lines = [(72,40,'01AREA   CLEAR'), (40,72,'BONUS'),(120,72,'X10'),
             (32,112,"WE'VE OBTAINED"),(40,120,'ENERGY RECOVERY'),(40,128,'PILLS')]
    at = {(x,y): k for ly,x,y,k,p,h,v in es if ly==0}
    for x,y,text in lines:
        for i,c in enumerate(text):
            if c != ' ': glyphs[at[x+i*8,y]] = c
    glyphs.update(json.loads((root/'capture/debrief-glyphs.json').read_text()))
    # All live values retain native positions and timing; unknown letters
    # remain transparent-ink fallbacks instead of being blanked.
    fonts = ImageFont.truetype(mono,29)
    from items import pickup_art
    bonus_bullet=pickup_art(root)[0]
    def render(k,p):
        if p >> 24 == 255: return Image.new('RGBA',(32,32))
        if p != 0x0F200F0F: return None
        if k=='18347A747A007A000000000000000000':return bonus_bullet
        a = np.zeros((8,8,4),dtype=np.uint8); a[indices(k)>0]=[231,233,216,255]
        tile = scale(Image.fromarray(a))
        if k in glyphs:
            tile = Image.new('RGBA',(32,32)); td=ImageDraw.Draw(tile)
            td.text((16,16),glyphs[k],anchor='mm',font=fonts,fill=(233,231,211))
        return tile
    return conditions, [f'[{guard}]<background>area-clear.png,1,0,0,10'], guard, render
