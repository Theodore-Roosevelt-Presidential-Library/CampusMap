# CampusMap

Web-based 3D model of the Theodore Roosevelt Presidential Library campus.

Live site: **https://campus.labs.trlibrary.com**

## What's here

| File | Purpose |
|------|---------|
| `index.html` | The viewer (Google `<model-viewer>`, self-contained) |
| `pois.json` | Points of interest — pin coordinates + panel content (title, image, description, CTA) |
| `TRPL_campus_web.glb` | Web-optimized campus model — Draco-compressed, GPU-instanced (7.7 MB) |
| `img/` | Logo (`TRPL_Wordmark_Black_RGB.svg`) and POI images (`img/poi/`) |
| `CNAME` | Custom domain for GitHub Pages |
| `.github/workflows/deploy.yml` | Builds & deploys the site to GitHub Pages on every push to `main` |
| `View TRPL Campus.command` | Double-click (macOS) to run a local server from this folder |
| `source/TRPL_campus_20260730.gltf` | Original full-res GLTF export (338 MB), preserved via **Git LFS** |
| `.gitattributes` | Routes `*.gltf` through Git LFS |

## Viewer features

- Starts framed on the Library and boardwalk (camera locked above the horizon so the underside isn't visible)
- Matte materials, white background so terrain blends into the page
- Manual +/− zoom, POI show/hide toggle, and a full-screen button (lower right); plus scroll/drag/pinch and a touch-aware controls guide
- Double-click (or double-tap) a point to recenter the view there
- Points of interest: subdued markers that open a slide-out info panel; markers hide when a building or berm blocks the line of sight (via a precomputed `heightfield.json`)
- Shareable views: camera angle, zoom, target, and open POI are encoded in a short `?v=` URL token, updated live in the address bar
- Embeddable into any web page (see Embedding below), preserving the starting view
- Responsive: starting distance adapts to the viewport; works on touch devices

## Points of interest (POIs)

POIs live in `pois.json`. Each entry:

```json
{
  "id": "library",
  "title": "The Library",
  "image": "img/poi/library.jpg",   // optional; place images in img/poi/
  "description": "Short description shown in the panel.",
  "cta": { "label": "Plan your visit", "url": "https://www.trlibrary.com" },  // optional; opens in a new tab
  "position": "-30.55 2.06 -76.40",  // X Y Z on the 3D model
  "normal": "-0.811 -0.002 0.585"    // surface normal
}
```

Clicking a marker slides an info panel out from the right. `image` and `cta` are optional. The sample copy in `pois.json` is placeholder — replace with final text and add images to `img/poi/`.

### Authoring new POIs (coordinate picker)

Open the viewer with `?edit` in the URL (e.g. `http://localhost:8734/?edit` or `https://campus.labs.trlibrary.com/?edit`), then **right-click** any point on the model. A readout shows the `position` and `normal` and a **Copy POI JSON** button that copies a ready-to-paste entry. Coordinates are seated onto the surface automatically (lifted, upright normal). (Right-click does nothing visible for normal visitors — the picker only appears in `?edit` mode.)

### Visual POI editor

For building a whole set without touching JSON, open **`/editor.html`** (e.g. `https://campus.labs.trlibrary.com/editor.html`). Right-click the map to drop markers (they seat themselves on the surface), fill in each point's title, description, image, and CTA in the side panel, then click **Download pois.json**. **Import JSON** loads an existing set to keep editing, and the map updates live as you type. The finished file works either as the site's default `pois.json` or as a custom set in an embed (`data-pois`).

## Embedding

The viewer can be dropped into any web page. Frame the view you want, click **Embed** (top-left), and copy the snippet — it carries the current camera angle, zoom, and open POI via the `?v=` token.

```html
<script src="https://campus.labs.trlibrary.com/embed.js" data-view="VIEW_TOKEN" data-height="600"></script>
```

`embed.js` inserts a responsive, full-screen-capable iframe in place of the script tag. `data-view` is optional — omit it to open the default view; `data-height` and `data-width` are also optional (px or any CSS length).

### Custom points of interest in an embed

An embedded map can show its own POIs instead of the default set — same campus model, different markers and panels. Two ways:

**Hosted JSON** — point `data-pois` at a URL returning the same shape as `pois.json` (a `{ "pois": [...] }` object, or a bare array). It must be served with CORS so the map can fetch it.

```html
<script src="https://campus.labs.trlibrary.com/embed.js"
        data-pois="https://example.org/my-pois.json"
        data-height="600"></script>
```

**postMessage (no CORS needed)** — inject POIs directly from the host page after the iframe loads:

```html
<script src="https://campus.labs.trlibrary.com/embed.js" data-height="600"></script>
<script>
  const map = document.querySelector('iframe[src*="campus.labs.trlibrary.com"]');
  map.addEventListener('load', () => {
    map.contentWindow.postMessage({
      type: 'trpl:setPOIs',
      pois: [
        { id: 'my-stop', title: 'My Stop', description: '…',
          position: '-30 1.4 -75', normal: '0 1 0' }
      ]
    }, '*');
  });
</script>
```

Each POI uses the same fields as the default set (`id`, `title`, `image`, `description`, `cta`, `position`, `normal`); coordinates are on the shared campus model, so use the `?edit` coordinate picker to grab new ones.

## Source preservation

The original full-resolution GLTF export is kept in `source/` and tracked with **Git LFS** (`*.gltf`). It is the master the web model was derived from, and is excluded from the Pages deploy so it never bloats the live site. Working with it requires Git LFS installed locally (`git lfs install`) — GitHub Desktop bundles it.

## Fonts

The viewer uses the TRPL brand type system — **Dharma Gothic E** (display / titles / CTAs), **Clearface** (body copy), and **Frutiger** (small UI text) — loaded by `@font-face` directly from the fonts self-hosted on `trlibrary.com`. Referencing them (rather than copying the files into this repo) keeps the licensed fonts out of version control. If the main site ever moves its theme paths, the `@font-face` URLs in `index.html` would need updating (or the woff2 files can be self-hosted here for full independence).

The POI images in `img/poi/` are placeholder badlands renders — replace with real photography.

## How it was built

Source was a Cinema 4D export (`.gltf`). Pipeline: convert to binary GLB → collapse ~102k scattered nodes into GPU instances → Draco geometry compression → matte, double-sided materials. Result is 7.7 MB (from 256 MB uncompressed).

## Local preview

Double-click **`View TRPL Campus.command`**, or from a terminal:

```bash
python3 -m http.server 8734
# then open http://localhost:8734/   (add ?edit to author POIs)
```

A local server is required because browsers won't load the GLB or `pois.json` from a `file://` page.

## Deploying

Every push to `main` triggers the Pages workflow automatically. No build step is required — the site is static. The workflow publishes `index.html`, `pois.json`, `TRPL_campus_web.glb`, `img/`, and `CNAME`.
