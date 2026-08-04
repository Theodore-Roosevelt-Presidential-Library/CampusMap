# CampusMap

Web-based 3D model of the Theodore Roosevelt Presidential Library campus.

Live site: **https://campus.labs.trlibrary.com**

## What's here

| File | Purpose |
|------|---------|
| `index.html` | The viewer (Google `<model-viewer>`, self-contained) |
| `TRPL_campus_web.glb` | Web-optimized campus model — Draco-compressed, GPU-instanced (7.7 MB) |
| `img/TRPL_Wordmark_Black_RGB.svg` | Logo shown lower-left, links to trlibrary.com |
| `CNAME` | Custom domain for GitHub Pages |
| `.github/workflows/deploy.yml` | Builds & deploys the site to GitHub Pages on every push to `main` |
| `source/TRPL_campus_20260730.gltf` | Original full-res GLTF export (338 MB), preserved via **Git LFS** |
| `.gitattributes` | Routes `*.gltf` through Git LFS |

## Source preservation

The original, full-resolution Cinema 4D GLTF export is kept in `source/` and tracked with **Git LFS** (`*.gltf`). It is the master the web model was derived from. It is intentionally excluded from the Pages deploy, so it never bloats the live site. Working with it requires Git LFS installed locally (`git lfs install`) — GitHub Desktop bundles it.

## Viewer features

- Starts framed on the Library and boardwalk (camera locked above the horizon so the underside isn't visible)
- Matte materials, white background so terrain blends into the page
- Manual +/− zoom (lower right) plus scroll/drag/pinch
- Click any point on the model to recenter the view there
- Responsive: the starting distance adapts to the viewport so it stays framed on narrow/portrait screens

## How it was built

Source was a Cinema 4D export (`.gltf`). Pipeline: convert to binary GLB → collapse ~102k scattered nodes into GPU instances → Draco geometry compression → matte, double-sided materials. Result is 7.7 MB (from 256 MB uncompressed).

## Deploying

Every push to `main` triggers the Pages workflow automatically. No build step is required — the site is static.

## Local preview

Serve the folder over HTTP (a browser won't load the GLB from a `file://` page):

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```
