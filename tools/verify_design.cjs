#!/usr/bin/env node
/* Browser checks for the restyled DLMP AI Policy Explorer.

     NODE_PATH="$(npm root -g)" node tools/verify_design.cjs [HTML] [OUTPUT_DIR]

   Opens the file from disk with networking disabled and every non-file request
   aborted, then exercises the page's own interactions, measures layout and contrast,
   walks keyboard focus, prints to PDF and saves screenshots. Writes results.json
   and exits non-zero when a check fails. Requires Playwright with Chromium. */
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const file = path.resolve(process.argv[2] || 'DLMP_AI_Policy_Explorer.html');
const outDir = path.resolve(process.argv[3] || 'verification');
fs.mkdirSync(outDir, { recursive: true });
const results = [];
const record = (name, passed, detail) => results.push({ name, status: passed ? 'passed' : 'failed', detail });

async function contrastScan(page) {
  return page.evaluate(() => {
    const parse = (c) => { const m = c && c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[\s,/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
    const lum = ({ r, g, b }) => { const f = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
    const blend = (t, b) => ({ r: t.r * t.a + b.r * (1 - t.a), g: t.g * t.a + b.g * (1 - t.a), b: t.b * t.a + b.b * (1 - t.a), a: 1 });
    const bgOf = (el) => { const layers = []; for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; } } let base = { r: 250, g: 248, b: 244, a: 1 }; for (let i = layers.length - 1; i >= 0; i--) base = blend(layers[i], base); return base; };
    const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
    const failures = []; let checked = 0;
    for (const el of document.body.querySelectorAll('*')) {
      if (![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
      if (el.closest('[aria-hidden="true"], .sr-only, script, style, noscript, option')) continue;
      if (!el.getClientRects().length) continue;
      const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || Number(cs.opacity) === 0) continue;
      const fg = parse(cs.color); if (!fg) continue;
      const bg = bgOf(el); const fgc = fg.a < 1 ? blend(fg, bg) : fg;
      const size = parseFloat(cs.fontSize); const weight = Number(cs.fontWeight) || 400;
      const large = size >= 24 || (size >= 18.66 && weight >= 700);
      const r = ratio(fgc, bg); checked++;
      if (r < (large ? 3 : 4.5)) failures.push({ text: el.textContent.trim().slice(0, 60), cls: el.className && String(el.className), tag: el.tagName, ratio: Math.round(r * 100) / 100, size, large });
    }
    return { checked, failures };
  });
}

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, offline: true, acceptDownloads: true });
  const external = [];
  await context.route('**/*', (route) => { const u = route.request().url(); if (u.startsWith('file:')) return route.continue(); external.push(u); return route.abort(); });
  const page = await context.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto('file://' + file, { waitUntil: 'load' });
  await page.waitForTimeout(300);
  record('opens from disk offline', (await page.title()).length > 0, await page.title());

  const self = await page.evaluate(() => window.DLMP_APP.selfTest());
  record('embedded self-test', self.passed === self.total, `${self.passed}/${self.total}`);

  const status = () => page.textContent('#result-status');
  const visible = (sel) => page.$$eval(sel, (els) => els.filter((e) => !e.classList.contains('hidden')).length);
  record('initial count', (await status()) === '17 of 17 public positions', await status());

  await page.selectOption('#theme', 'supervision');
  const sup = await status();
  record('theme filter', sup === '4 of 17 public positions' && (await visible('.source')) === 4, sup);
  record('active filter state', await page.$eval('#theme', (e) => e.closest('.filter').classList.contains('is-set')), 'theme field marked active');

  await page.selectOption('#institution', 'MIT');
  await page.selectOption('#theme', 'privacy');
  record('combined filters reach empty state', (await status()) === '0 of 17 public positions' && !(await page.$eval('#empty', (e) => e.classList.contains('hidden'))), await status());

  await page.click('#reset');
  record('reset', (await status()) === '17 of 17 public positions' && !(await page.$eval('#theme', (e) => e.closest('.filter').classList.contains('is-set'))), await status());

  await page.click('.insight a[data-evidence="P-MIT-mission"]');
  await page.waitForTimeout(700);
  const landed = await page.evaluate(() => { const a = document.activeElement; const r = a.getBoundingClientRect(); const nav = document.querySelector('.nav').getBoundingClientRect(); return { id: a.id, open: a.closest('details').open, top: Math.round(r.top), navBottom: Math.round(nav.bottom) }; });
  record('evidence link opens and focuses passage below the sticky nav', landed.id === 'P-MIT-mission' && landed.open && landed.top >= landed.navBottom, landed);

  await page.selectOption('#specialty', 'Hematopathology');
  const mission = await page.textContent('#mission-status');
  record('competency filter', (await visible('.competency')) === 2 && /^2 of 7/.test(mission), mission);
  await page.selectOption('#specialty', '');

  await page.check('input[name="s1"][value="2"]');
  const reason = await page.textContent('#s1 .scenario-response');
  const expected = await page.evaluate(() => JSON.parse(document.getElementById('page-data').textContent).scenarios[0].options[2].reason);
  record('scenario rationale', reason.includes(expected), reason.slice(0, 80));

  await page.click('#generate-agenda');
  const agenda = await page.inputValue('#agenda-text');
  record('agenda generation', agenda.startsWith('# DLMP AI education: draft faculty agenda'), `${agenda.length} characters`);
  const [agendaDownload] = await Promise.all([page.waitForEvent('download'), page.click('#download-agenda')]);
  const agendaPath = path.join(outDir, agendaDownload.suggestedFilename());
  await agendaDownload.saveAs(agendaPath);
  record('agenda download', fs.readFileSync(agendaPath, 'utf8') === agenda, agendaDownload.suggestedFilename());
  const [ledgerDownload] = await Promise.all([page.waitForEvent('download'), page.click('#export-data')]);
  const ledgerPath = path.join(outDir, ledgerDownload.suggestedFilename());
  await ledgerDownload.saveAs(ledgerPath);
  const ledger = JSON.parse(fs.readFileSync(ledgerPath, 'utf8'));
  record('evidence JSON download', ledger.sources.length === 17 && ledger.evidence.length === 68, ledgerDownload.suggestedFilename());

  await page.evaluate(() => { document.querySelector('.agenda details').open = true; });
  await page.click('#export-state');
  await page.click('#import-state');
  record('save and restore discussion', (await page.textContent('#state-status')).startsWith('Saved discussion state applied'), await page.textContent('#state-status'));

  await page.click('#run-checks');
  record('run embedded data checks button', /passed/.test(await page.textContent('#check-status')), await page.textContent('#check-status'));

  await page.evaluate(() => document.getElementById('comparison').scrollIntoView());
  await page.waitForTimeout(600);
  record('nav marks the section in view', (await page.getAttribute('.nav a[href="#comparison"]', 'aria-current')) === 'location', await page.getAttribute('.nav a[href="#comparison"]', 'aria-current'));

  // Keyboard: skip link first, then every stop has a visible indicator and is not hidden under the sticky nav.
  await page.goto('file://' + file, { waitUntil: 'load' });
  await page.keyboard.press('Tab');
  const skip = await page.evaluate(() => { const a = document.activeElement; return { cls: a.className, top: a.getBoundingClientRect().top }; });
  record('skip link is the first stop and becomes visible', skip.cls === 'skip' && skip.top >= 0, skip);
  let noIndicator = 0, obscured = 0, stops = 0;
  for (let i = 0; i < 90; i++) {
    await page.keyboard.press('Tab');
    const s = await page.evaluate(() => { const a = document.activeElement; if (!a || a === document.body) return null; const cs = getComputedStyle(a); const r = a.getBoundingClientRect(); const nav = document.querySelector('.nav').getBoundingClientRect(); return { indicator: (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) || cs.boxShadow !== 'none', obscured: r.bottom <= nav.bottom && r.top < nav.bottom && !a.closest('.nav'), id: a.id || a.textContent.trim().slice(0, 30) }; });
    if (!s) continue; stops++; if (!s.indicator) noIndicator++; if (s.obscured) obscured++;
  }
  record('keyboard focus visible on every stop', noIndicator === 0, `${stops} stops, ${noIndicator} without an indicator`);
  record('focused elements not hidden by the sticky nav', obscured === 0, `${obscured} obscured`);

  // Layout: no page-wide horizontal overflow; screenshots.
  for (const width of [1440, 1024, 768, 390, 320]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('file://' + file, { waitUntil: 'load' });
    const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    record(`no horizontal overflow at ${width}px`, over <= 0, `${over}px`);
    await page.screenshot({ path: path.join(outDir, `viewport-${width}.png`) });
    if (width === 1440 || width === 390) await page.screenshot({ path: path.join(outDir, `full-${width}.jpg`), fullPage: true, type: 'jpeg', quality: 72 });
    if (width === 1440 || width === 390) {
      await page.evaluate(() => document.querySelectorAll('details').forEach((d) => { d.open = true; }));
      const scan = await contrastScan(page);
      record(`text contrast at ${width}px (all disclosures open)`, scan.failures.length === 0, { checked: scan.checked, failures: scan.failures.slice(0, 12) });
    }
  }

  // Gallery of expanded states for visual review.
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto('file://' + file, { waitUntil: 'load' });
  await page.evaluate(() => { document.querySelector('#source-P-UW-MED details').open = true; document.querySelector('#competencies .competency details').open = true; document.querySelector('#s1 details').open = true; });
  await page.check('input[name="s1"][value="2"]');
  await page.click('#generate-agenda');
  await page.addStyleTag({ content: '.nav{position:static!important}' });
  for (const [name, sel] of [['source-expanded', '#source-P-UW-MED'], ['coverage', '.coverage'], ['tensions', '.tensions'], ['lanes', '#competencies'], ['scenario', '#s1'], ['agenda', '.agenda'], ['international', '#international .grid'], ['methods', '.methods'], ['footer', '.foot']]) {
    await page.locator(sel).screenshot({ path: path.join(outDir, `el-${name}.png`) });
  }

  // Print: open every disclosure through beforeprint, render a PDF, restore afterwards.
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto('file://' + file, { waitUntil: 'load' });
  await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
  const openForPrint = await page.$$eval('details', (d) => d.every((x) => x.open));
  await page.emulateMedia({ media: 'print' });
  await page.screenshot({ path: path.join(outDir, 'print-preview.png') });
  const pdf = await page.pdf({ path: path.join(outDir, 'print.pdf'), format: 'Letter', printBackground: true });
  await page.emulateMedia({ media: 'screen' });
  await page.evaluate(() => window.dispatchEvent(new Event('afterprint')));
  const restored = await page.$$eval('details', (d) => d.every((x) => !x.open));
  record('print opens every disclosure and restores after', openForPrint && restored, `PDF ${Math.round(pdf.length / 1024)} KB`);

  await page.emulateMedia({ reducedMotion: 'reduce' });
  record('reduced motion disables smooth scrolling', (await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior)) === 'auto', 'scroll-behavior');

  record('no network requests', external.length === 0, external.slice(0, 5));
  record('no console or page errors', errors.length === 0, errors.slice(0, 5));

  await browser.close();
  fs.writeFileSync(path.join(outDir, 'results.json'), JSON.stringify(results, null, 2));
  const failed = results.filter((r) => r.status !== 'passed');
  for (const r of results) console.log(`${r.status === 'passed' ? 'PASS' : 'FAIL'}  ${r.name}${r.status === 'passed' ? '' : '  ' + JSON.stringify(r.detail)}`);
  console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
  process.exit(failed.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
