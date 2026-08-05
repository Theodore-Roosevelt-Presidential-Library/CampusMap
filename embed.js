/*
 * TRPL Campus 3D Map — embed loader.
 * Usage: <script src="https://campus.labs.trlibrary.com/embed.js" data-view="..." data-height="600"></script>
 * Optional data attributes:
 *   data-view    the "v" permalink token (camera angle, zoom, open POI). Omit for the default view.
 *   data-height  iframe height in px (default 600), or any CSS length (e.g. "80vh").
 *   data-width   iframe width (default 100%).
 */
(function () {
  var s = document.currentScript;
  if (!s) return;
  var origin = new URL(s.src).origin;
  var view = s.getAttribute('data-view') || '';
  var height = s.getAttribute('data-height') || '600';
  var width = s.getAttribute('data-width') || '100%';
  if (/^\d+$/.test(height)) height += 'px';
  if (/^\d+$/.test(width)) width += 'px';

  var src = origin + '/' + (view ? '?v=' + encodeURIComponent(view) : '');
  var iframe = document.createElement('iframe');
  iframe.src = src;
  iframe.title = 'Theodore Roosevelt Presidential Library — Campus 3D Map';
  iframe.loading = 'lazy';
  iframe.setAttribute('allowfullscreen', '');
  iframe.setAttribute('allow', 'fullscreen');
  iframe.style.cssText = 'display:block;border:0;width:' + width + ';height:' + height + ';';
  s.parentNode.insertBefore(iframe, s);
})();
