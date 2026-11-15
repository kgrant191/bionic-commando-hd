"""Cover stale nametable fragments below Area 1's bottom water row."""
import json
from PIL import Image

def water_edge(root,rule):
    data=json.loads((root/'capture/water-edge-v072.json').read_text())
    source=Image.open(root/'art/level1-reference.png').convert('RGBA').resize((1024,960),Image.Resampling.LANCZOS)
    conditions=['<condition>waterEdgeArea,memoryCheckConstant,004D,==,01',
                '<condition>waterEdgeBottom,positionCheckY,>=,224']
    for i,above in enumerate(data['water_above']):
        name=f'waterEdgeAbove{i}'
        conditions.append(f'<condition>{name},tileNearby,0,-8,{above},0F302118,N')
        sx=(int(above[:8],16)%16)*32
        im=source.crop((sx,872,sx+32,904))
        for k,p in data['stale_pairs']:
            rule(k,int(p,16),im,f'waterEdgeArea&waterEdgeBottom&{name}&!title&!worldmap&!equipment&!radio&!areaClear')
    return conditions
