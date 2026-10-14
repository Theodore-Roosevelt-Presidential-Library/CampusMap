# CampusMap

Web-based 3D model of the Theodore Roosevelt Presidential Library campus.

Live site: **https://campus.labs.trlibrary.com**

## What's here

| File | Purpose |
|------|---------|
| `index.html` | The viewer (Google `<model-viewer>`, self-contained) |
| `editor.html` | Visual POI editor — right-click to place markers, edit details, download `pois.json` |
| `embed.js` | Embed loader — inserts the map into any page and passes the view/POIs through |
| `pois.json` | Points of interest — pin coordinates + panel content (title, image, description, CTA) |
| `interior.json` | Inside the Library — interior stops (galleries, narrative galleries, public spaces) and visitor-information markers |
| `heightfield.json` | Precomputed terrain/building height map used to hide markers blocked from view |
| `TRPL_campus_web.glb` | Web-optimized campus model — Draco-compressed, GPU-instanced (7.7 MB) |
| `img/` | Logo (`TRPL_Wordmark_Black_RGB.svg`), POI images (`img/poi/`) and gallery photos (`img/poi/inside/`, from trlibrary.com) |
| `tools/interior/` | Scripts and data used to build the interior and exterior details (reference only) |
| `examples/` | Example host pages, e.g. the Maah Daah Hey 100 race-day mockup with a custom POI set |
| `CNAME` | Custom domain for GitHub Pages |
| `.github/workflows/deploy.yml` | Builds & deploys the site to GitHub Pages on every push to `main` |
| `View TRPL Campus.command` | Double-click (macOS) to run a local server from this folder |
| `source/TRPL_campus_20260730.gltf` | Original full-res GLTF export (338 MB), preserved via **Git LFS** |
| `.gitattributes` | Routes `*.gltf` through Git LFS |

## Viewer features

- Loading screen: a still of the opening view (`img/loading-wide.webp`, ~26 KB) shows immediately with the progress bar, then fades into the live model. The model is preloaded from the page head so the download starts before the viewer script runs.

- Starts framed on the Library and boardwalk (camera locked above the horizon so the underside isn't visible)
- Matte materials, white background so terrain blends into the page
- Manual +/− zoom, POI show/hide toggle, and a full-screen button (lower right); plus scroll/drag/pinch and a touch-aware controls guide
- Double-click (or double-tap) a point to recenter the view there
- Points of interest: subdued markers that open a slide-out info panel; markers hide when a building or berm blocks the line of sight (via a precomputed `heightfield.json`)
- Shareable views: camera angle, zoom, target, and open POI are encoded in a short `?v=` URL token, updated live in the address bar
- Embeddable into any web page (see Embedding below), preserving the starting view
- Responsive: starting distance adapts to the viewport; works on touch devices

## Inside the Library

**Outside | Inside** (top center): *Inside* lifts the roof and shows the Library's public spaces. Private areas (offices, security, IT, mechanical, storage, back of house) are drawn as solid blocks, the same way the exhibit map on [trlibrary.com/visit/maps](https://www.trlibrary.com/visit/maps) treats them.

- **Floors:** *Main floor* (galleries 1–28, Narrative Galleries A–D, lobby, Exhibit & Event Gallery, store, Salt+Scoria, lockers, auditorium, East Wing lobby, classrooms) and *Upper floor* (East Wing: Executive Board Room and the upstairs reception).
- **Stops:** numbered and lettered markers match the printed exhibit map. Each opens the side panel with a photo, a short description and a link to that gallery's section of the [exhibit guide](https://www.trlibrary.com/visit/exhibits/main). The content is in **`interior.json`**: edit text, images (`img/poi/inside/`) and links there.
- **Visitor information layers** (layers button, lower right): recommended route, restrooms and services, accessibility and elevators, and flashing-light alerts.
- **Deep links:** `?stop=in-the-arena` opens inside, on that stop. `?inside=1` or `?inside=2` opens on a floor. The shareable `?v=` token now also records inside/outside, the floor and the open interior stop, and older tokens still work.
- **Embeds:** `data-stop="museum-store"` or `data-inside="2"` on the `embed.js` script tag. Host pages can also `postMessage({type:'trpl:focus', id:'legacy'})` or `{type:'trpl:mode', inside:true, level:2}`.
- **Authoring:** with `?edit`, right-clicking while inside gives an interior-ready JSON snippet (it includes `level` and `kind`).

**How it was built.** The interior is part of `TRPL_campus_web.glb`, in the nodes `INT_L1`, `INT_L2` and `INT_ROUTE`, which the page shows or hides. The steps:
1. Walls came from the conformed sheets A201 and A202 (BIM 360 archive, Nov 2024 conformed set) as vector line work. They were registered to the campus model through the frame used by LBCSystems.
2. Rooms were split by their tags. Public versus private and the gallery numbering follow the published exhibit map, which was registered to the same frame.
3. The route follows the exhibit map's dotted route.
4. The scripts and intermediate data are in `tools/interior/`, for reference. They need the archive PDFs, which are not in this repo.

**Exterior details added from the drawings:**
- The People's Library and Main Lobby curtain wall on the north and east (A321).
- The auditorium stage window and the East Wing's northwest glazing (A320 CW13).
- The permanent-exhibit bay window on the north wall (A303).
- The West Patio alcove beside the roof stair, with its timber back wall and vestibule doors (A275).

These sit on the model's simplified facades, so they show where the features are; they are not exact-size.

**Known approximations:**
- The upper floor is placed from A202 and nudged about 5 ft east to sit inside the model's East Wing.
- Gallery partitions come from the architectural plan, so exhibit casework is not shown.
- Marker positions come from the published exhibit map.

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

`embed.js` inserts a responsive, full-screen-capable iframe in place of the script tag. `data-view` is optional — omit it to open the default view. `data-height` accepts a number (px, default 600), any CSS length (`80vh`, `calc(100vh - 120px)`), `100%` (fills the container **if the container has its own height**), or **`fill`** — which dynamically fills the visible area below the map and tracks window resizes (the simplest way to make it full-screen). `data-width` defaults to `100%`.

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
