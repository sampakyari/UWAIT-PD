/* Evidence Folio 2.0 — presentation-only enhancements for DLMP_AI_Policy_Explorer.html.
   Inlined after the page's main script by tools/apply_design.py. It never reads or
   writes evidence data; every feature degrades silently when unsupported. */
(function () {
  'use strict';

  function currentSection() {
    var links = [].slice.call(document.querySelectorAll('.nav a[href^="#"]'));
    var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
    if (!('IntersectionObserver' in window) || targets.some(function (t) { return !t; })) return;
    var inView = {};
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { inView[e.target.id] = e.isIntersecting; });
      var active = null;
      targets.forEach(function (t) { if (active === null && inView[t.id]) active = t.id; });
      links.forEach(function (a, i) {
        if (active !== null && targets[i].id === active) a.setAttribute('aria-current', 'location');
        else a.removeAttribute('aria-current');
      });
    }, { rootMargin: '-80px 0px -55% 0px', threshold: 0 });
    targets.forEach(function (t) { observer.observe(t); });
  }

  function activeFilters() {
    var defaults = { sort: 'institution' };
    var ids = ['search', 'institution', 'authority', 'theme', 'domain', 'date-filter', 'sort', 'specialty', 'stage'];
    function mark() {
      ids.forEach(function (id) {
        var el = document.getElementById(id);
        var box = el && el.closest('.filter');
        if (!box) return;
        var resting = Object.prototype.hasOwnProperty.call(defaults, id) ? defaults[id] : '';
        box.classList.toggle('is-set', el.value.trim() !== resting);
      });
    }
    document.addEventListener('input', mark, true);
    document.addEventListener('change', mark, true);
    if ('MutationObserver' in window) {
      ['result-status', 'mission-status'].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) new MutationObserver(mark).observe(el, { childList: true, characterData: true, subtree: true });
      });
    }
    mark();
  }

  function printDisclosures() {
    var opened = [];
    window.addEventListener('beforeprint', function () {
      [].slice.call(document.querySelectorAll('details:not([open])')).forEach(function (d) {
        d.open = true;
        opened.push(d);
      });
    });
    window.addEventListener('afterprint', function () {
      opened.forEach(function (d) { d.open = false; });
      opened = [];
    });
  }

  [currentSection, activeFilters, printDisclosures].forEach(function (feature) {
    try { feature(); } catch (err) { /* presentation only: never interrupt the page */ }
  });
})();
