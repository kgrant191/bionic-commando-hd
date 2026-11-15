"""Live gunshots use dedicated art independent of character damage palettes."""
from PIL import Image

SHOT = '000010383810000000106CC6C66C1000'
GUARD = '!title&!worldmap&!equipment&!radio&!areaClear'


def make_projectile(root):
    source = Image.open(root/'art/projectile-v074.png').convert('RGBA')
    bounds = source.getchannel('A').point(lambda a: 255 if a > 32 else 0).getbbox()
    assert bounds, 'Projectile art must have a visible alpha silhouette'
    # The native projectile occupies x=0..6 and y=1..6 of its 8x8 tile.
    # Keep the same centre, footprint and live OAM movement/flip flags.
    shot = Image.new('RGBA', (32, 32))
    shot.alpha_composite(source.crop(bounds).resize((28, 24), Image.Resampling.LANCZOS), (0, 4))

    def render(key, palette):
        # Normal Spencer, his invulnerability flash, red guards and white
        # guards share this CHR pattern but use different sprite palettes.
        # A palette change must not select clothing textures or NES artwork.
        return shot if key == SHOT and palette >> 24 == 255 else None

    return render


def extend_flares(root, keys, rule):
    """Type 7 in player-projectile slot 1 is the active illumination flare.

    RAM 0537/054A identifies it; 0570/05AA stores its screen centre. The
    frame snapshot includes the next camera step (C8/CA), so compensate it
    when selecting the rendered sprite rectangle. Do not recolor other shots.
    """
    bullet=make_projectile(root)
    source=Image.open(root/'art/flare-active-v075.png').convert('RGBA')
    bounds=source.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
    art=source.crop(bounds)
    art.thumbnail((26,32),Image.Resampling.LANCZOS)
    flare=Image.new('RGBA',(32,32))
    flare.alpha_composite(art,((32-art.width)//2,0))
    conditions=['<condition>flareActive,memoryCheckConstant,0537,==,01',
                '<condition>flareType,memoryCheckConstant,054A,==,07']
    camera_steps=[0]+[n for d in range(1,9) for n in (-d,d)]
    for axis,address,offset,camera in [('X',0x0570,4,0xC8),('Y',0x05AA,2,0xCA)]:
        for pos in range(256):
            conditions.append(f'<condition>flare{axis}{pos},memoryCheckConstant,{address:04X},==,{(pos+offset)&255:02X}')
            if axis=='X':
                # Horizontal origin checks in Mesen reflect tile offsets for
                # mirrored sprites. Screen-column bounds cover the full tile.
                conditions += [f'<condition>shotX{pos},positionCheckX,>=,{pos}',
                               f'<condition>shotXEnd{pos},positionCheckX,<,{pos+8}']
            else:
                conditions.append(f'<condition>shotY{pos},originPositionCheckY,==,{pos}')
        for step in camera_steps:
            conditions.append(f'<condition>flareCamera{axis}{step+8},memoryCheckConstant,{camera:04X},==,{step&255:02X}')
    guard=GUARD+'&area4&flareActive&flareType'
    for key,palette in keys:
        if key!=SHOT or palette not in {0xFF202A0F,0xFF202015}:continue
        # These returns precede position-dependent rules, preserving Mesen's
        # normal tile cache outside the short active flare sequence.
        for bypass in ('!area4','!flareActive','!flareType'):
            rule(key,palette,bullet(key,palette),GUARD+'&'+bypass)
        for step in camera_steps:
            for y in range(256):
                rule(key,palette,bullet(key,palette),f'flareY{(y+step)%256}&flareCameraY{step+8}&!shotY{y}&{guard}')
        for step in camera_steps:
            for x in range(256):
                rule(key,palette,flare,f'flareX{(x+step)%256}&flareCameraX{step+8}&shotX{x}&shotXEnd{x}&{guard}')
    return conditions
