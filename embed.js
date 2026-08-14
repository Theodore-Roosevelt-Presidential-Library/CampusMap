/*
 * TRPL Campus 3D Map — embed loader.
 * Usage: <script src="https://campus.labs.trlibrary.com/embed.js" data-view="..." data-height="600"></script>
 * Optional data attributes:
 *   data-view    the "v" permalink token (camera angle, zoom, open POI). Omit for the default view.
 *   data-pois    URL of a custom POI JSON file to use instead of the default set
 *                (must be CORS-accessible). See README for the JSON shape and the
 *                postMessage API for injecting POIs without CORS.
 *   data-height  iframe height. A number (px, default 600), any CSS length ("80vh",
 *                "calc(100vh - 120px)"), "100%" (fills its container if the container has
 *                a height; otherwise falls back to filling the viewport), or "fill"
 *                (dynamically fills the visible area below the map and tracks resizes).
 *   data-width   iframe width (default 100%).
 */
(function () {
  var s = document.currentScript;
  if (!s) return;
  var origin = new URL(s.src).origin;
  var view = s.getAttribute('data-view') || '';
  var pois = s.getAttribute('data-pois') || '';
  var height = s.getAttribute('data-height') || '600';
  var width = s.getAttribute('data-width') || '100%';
  if (/^\d+$/.test(width)) width += 'px';

  var params = new URLSearchParams();
  if (view) params.set('v', view);
  if (pois) params.set('pois', pois);
  var qs = params.toString();
  var src = origin + '/' + (qs ? '?' + qs : '');
  var iframe = document.createElement('iframe');
  iframe.src = src;
  iframe.title = 'Theodore Roosevelt Presidential Library — Campus 3D Map';
  iframe.loading = 'lazy';
  iframe.setAttribute('allowfullscreen', '');
  iframe.setAttribute('allow', 'fullscreen');
  iframe.style.cssText = 'display:block;border:0;width:' + width + ';';
  s.parentNode.insertBefore(iframe, s);

  // Dynamically fill the visible area from the map's top edge to the bottom of the window.
  function fillViewport(){
    var top = iframe.getBoundingClientRect().top;
    iframe.style.height = Math.max(320, Math.round(window.innerHeight - top)) + 'px';
  }
  function enableFill(){
    iframe.style.height = '400px';   // give it flow height, then measure
    fillViewport();
    setTimeout(fillViewport, 200);
    window.addEventListener('resize', fillViewport);
  }

  if (height === 'fill') {
    enableFill();
  } else {
    if (/^\d+$/.test(height)) height += 'px';
    iframe.style.height = height;    // e.g. 600, "80vh", "calc(100vh - 146px)", "100%"
    if (/%\s*$/.test(height)) {
      // A percentage height only resolves if the container has its own height;
      // if it collapses, fall back to filling the viewport so it never disappears.
      setTimeout(function(){ if (iframe.getBoundingClientRect().height < 40) enableFill(); }, 60);
    }
  }
})();
