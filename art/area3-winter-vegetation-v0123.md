# Area 3 winter vegetation

Source: `area3-winter-vegetation-v0123.png`, generated with the built-in image
generator for the requested replacement of decorative wall mesh. This is a
source texture; the install pack uses only its compiled atlas cells.

Prompt:

> Use case: stylized-concept. Asset type: seamless square game texture for a richly painted 16-bit-style HD side-view action platformer. Create a single edge-to-edge seamless tile of winter alpine vegetation covering a recessed vertical cliff face: dense dark blue-green cushion moss with clearly readable short sprigs of hardy creeping juniper and tiny leathery evergreen leaves, a few fine brown rootlets, subtle scattered frost and very small powder-snow deposits caught on the upper leaf tips. Rich hand-painted game sprite shading, cohesive fine detail, crisp organic silhouettes within the texture, muted deep forest green and teal shadows with restrained frosty pale blue accents. It must read as soft vegetation, darker than snowy ledges and brown solid rocks. Flat orthographic front-facing texture, even diffuse light. Dense uniform coverage all the way to every edge; tile seamlessly on all four edges with no border, no center focal point, no grid, no diamond or mesh pattern, no large snow clumps, no visible stones or rock slabs, no icicles, no trunks, no flowers, no sky, no objects, no text. Design to remain legible reduced to a 32 by 32 pixel repeating tile: use a handful of medium-size foliage clumps rather than microscopic photographic noise. Full opaque square canvas, no transparency.

Integration uses a 64-by-64 source tile split into four 32-by-32 quadrants.
The native pattern adjacency determines the quadrant, preserving continuous
texture alignment while the camera moves. Native contour alpha is retained.
