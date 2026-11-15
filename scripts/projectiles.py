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
