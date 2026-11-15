"""Shared XP bullet and flare-bomb pickup artwork."""
from PIL import Image

def pickup_art(root):
    sheet=Image.open(root/'art/bullet-flare-bomb-v071.png').convert('RGBA')
    cw=sheet.width//2;icons=[]
    for col,size in [(0,32),(1,64)]:
        # Ignore the sheet divider; it is outside both object silhouettes.
        im=sheet.crop((col*cw+cw//25,0,(col+1)*cw-cw//25,sheet.height))
        im=im.crop(im.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox())
        im.thumbnail((size,size),Image.Resampling.LANCZOS)
        icon=Image.new('RGBA',(size,size));icon.alpha_composite(im,((size-im.width)//2,(size-im.height)//2))
        if col==0:
            im=Image.open(root/'art/bullet-v072.png').convert('RGBA')
            im=im.crop(im.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox())
            im.thumbnail((30,32),Image.Resampling.LANCZOS)
            icon=Image.new('RGBA',(32,32));icon.alpha_composite(im,((32-im.width)//2,(32-im.height)//2))
        icons.append(icon)
    return icons
