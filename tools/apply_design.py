#!/usr/bin/env python3
"""Apply the Evidence Folio design system to the DLMP AI Policy Explorer.

    python3 tools/apply_design.py [SOURCE_HTML] [OUTPUT_HTML]

Defaults: source/DLMP_AI_Policy_Explorer.original.html -> DLMP_AI_Policy_Explorer.html

The transform is presentation-only. It replaces the stylesheet, adds presentational
wrappers, labels and decorative marks, moves the footer out of <main>, and appends a
presentation-only script. The embedded page-data JSON and the page's main script are
copied byte for byte, and the run stops without writing if either would change, or if
any expected anchor is missing. Standard library only.
"""

import datetime
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = ROOT / "source" / "DLMP_AI_Policy_Explorer.original.html"
DEFAULT_OUT = ROOT / "DLMP_AI_Policy_Explorer.html"
CSS_PATH = ROOT / "design-system" / "explorer.css"
JS_PATH = ROOT / "design-system" / "explorer-enhancements.js"
CHECKS_PATH = ROOT / "design-system" / "design-pass-checks.json"

SECTION_NUMBERS = {
    "overview": "01", "explorer": "02", "comparison": "03", "mission": "04",
    "workbench": "05", "international": "06", "methods": "07",
}
WATERMARKS = {
    "overview": "synthesis", "explorer": "evidence", "comparison": "conditions",
    "mission": "competence", "workbench": "deliberation", "international": "context",
    "methods": "method",
}
# Lane copy for the three competency modes, taken from the AI_Policy_Workflow film.
LANES = [
    ("Perform independently", "i", "Independent competence",
     "Practice interpretation and judgement before relying on an AI answer."),
    ("Use AI with verification", "ii", "Supported work",
     "Check evidence, uncertainty, and applicability of an assisted result."),
    ("Oversee / audit AI", "iii", "Critical oversight",
     "Recognize failure, monitor performance, and know when to escalate."),
]
DATE_LABELS = {
    "publication date": "Published", "adoption date": "Adopted", "effective date": "Effective",
    "established date": "Established", "document date": "Document", "review date": "Review",
}

RINGS_HERO = (
    '<svg class="hero-rings" aria-hidden="true" focusable="false" viewBox="0 0 760 760" fill="none">'
    '<circle cx="380" cy="380" r="379" stroke="#b7a57a" stroke-opacity=".5"/>'
    '<circle cx="380" cy="380" r="322" stroke="#b7a57a" stroke-opacity=".32"/>'
    '<circle cx="380" cy="380" r="265" stroke="#b7a57a" stroke-opacity=".22"/>'
    '<circle cx="380" cy="380" r="208" stroke="#b7a57a" stroke-opacity=".15"/>'
    '<circle cx="380" cy="380" r="151" stroke="#b7a57a" stroke-opacity=".1"/>'
    '<path d="M380 1a379 379 0 0 1 379 379" stroke="#b7a57a" stroke-width="3"/></svg>'
)
RINGS_FOOT = (
    '<svg class="foot-rings" aria-hidden="true" focusable="false" viewBox="0 0 520 520" fill="none">'
    '<circle cx="260" cy="260" r="259" stroke="#b7a57a" stroke-opacity=".35"/>'
    '<circle cx="260" cy="260" r="200" stroke="#b7a57a" stroke-opacity=".22"/>'
    '<circle cx="260" cy="260" r="141" stroke="#b7a57a" stroke-opacity=".14"/></svg>'
)


class TransformError(SystemExit):
    pass


def replace_once(text, old, new, count=1):
    found = text.count(old)
    if found != count:
        raise TransformError(f"expected {count} occurrence(s) of {old[:80]!r}, found {found}")
    return text.replace(old, new)


def sub_exact(pattern, repl, text, count, flags=0):
    new, found = re.subn(pattern, repl, text, flags=flags)
    if found != count:
        raise TransformError(f"expected {count} match(es) for {pattern[:80]!r}, found {found}")
    return new


def cap(text):
    return text[:1].upper() + text[1:] if text else text


def glyph(stance):
    return f'<span class="st st-{stance}" aria-hidden="true"></span>'


def page_data(doc):
    match = re.search(r'<script id="page-data" type="application/json">(.*?)</script>', doc, re.S)
    if not match:
        raise TransformError("page-data script not found")
    return match.group(0), json.loads(match.group(1))


def main_script(doc):
    start = doc.rfind("<script>")
    end = doc.find("</script>", start)
    if start < 0 or end < 0 or "const data=JSON.parse" not in doc[start:end]:
        raise TransformError("main script not found")
    return doc[start:end + len("</script>")]


def kicker(section_id, label, extra=""):
    num = SECTION_NUMBERS[section_id]
    return (f'<span class="watermark" aria-hidden="true">{WATERMARKS[section_id]}</span>'
            f'<div class="kicker"><span class="eyebrow"><span class="sec-num" aria-hidden="true">{num}</span>'
            f'{label}</span>{extra}</div>')


def transform_sections(doc):
    doc = replace_once(
        doc,
        '<section class="section" id="overview" aria-labelledby="overview-title"><div class="eyebrow">Executive synthesis · analyst interpretation</div>',
        '<section class="section" id="overview" aria-labelledby="overview-title">'
        + kicker("overview", "Executive synthesis", '<span class="badge badge-analyst">Analyst interpretation</span>'))
    doc = replace_once(
        doc,
        '<section class="section" id="explorer" aria-labelledby="explorer-title"><div class="extension">Extension A · evidence & uncertainty explorer</div>',
        '<section class="section" id="explorer" aria-labelledby="explorer-title">'
        + kicker("explorer", "Policy explorer",
                 '<span class="extension" data-letter="A">Extension A · evidence &amp; uncertainty explorer</span>'))
    doc = replace_once(
        doc,
        '<section class="section" id="comparison"><div class="eyebrow">Categorical comparison · passage-level coding</div><h2>',
        '<section class="section" id="comparison" aria-labelledby="comparison-title">'
        + kicker("comparison", "Categorical comparison", '<span class="badge badge-analyst">Passage-level coding</span>')
        + '<h2 id="comparison-title">')
    doc = replace_once(
        doc,
        '<section class="section" id="mission"><div class="extension">Extension B · mission-to-competency map</div><h2>',
        '<section class="section" id="mission" aria-labelledby="mission-title">'
        + kicker("mission", "DLMP competencies",
                 '<span class="extension" data-letter="B">Extension B · mission-to-competency map</span>'
                 '<span class="badge badge-draft">Draft proposals</span>')
        + '<h2 id="mission-title">')
    doc = replace_once(
        doc,
        '<section class="section" id="workbench"><div class="extension">Extension C · faculty deliberation workbench</div><h2>',
        '<section class="section" id="workbench" aria-labelledby="workbench-title">'
        + kicker("workbench", "Deliberate",
                 '<span class="extension" data-letter="C">Extension C · faculty deliberation workbench</span>')
        + '<h2 id="workbench-title">')
    doc = replace_once(
        doc,
        '<section class="section" id="international"><div class="eyebrow">International & regulatory supplement</div><h2>',
        '<section class="section" id="international" aria-labelledby="international-title">'
        + kicker("international", "International &amp; regulatory supplement",
                 '<span class="badge badge-external">External context</span>')
        + '<h2 id="international-title">')
    doc = replace_once(
        doc,
        '<section class="section" id="methods"><div class="eyebrow">Methods, evolution & limitations</div><h2>',
        '<section class="section" id="methods" aria-labelledby="methods-title">'
        + kicker("methods", "Methods, evolution &amp; limitations")
        + '<h2 id="methods-title">')
    return doc


def transform_masthead_and_hero(doc):
    doc = replace_once(
        doc,
        '<div class="edition">Public reconstruction<br>Research: 5 October 2026</div>',
        '<div class="edition"><span>Public reconstruction · Research: 5 October 2026</span>'
        '<span class="badge badge-draft">Draft for discussion</span></div>')
    doc = replace_once(doc, '<div class="hero"><div class="hero-inner">',
                       '<div class="hero">' + RINGS_HERO + '<div class="hero-inner">')
    doc = replace_once(doc, '<h1>What are we here<br>together to do?</h1>',
                       '<h1>What are we here <span class="accent">together</span> to do?</h1>')
    creed = [
        ("i", "Preserve the judgment learners must develop.", "Perform independently"),
        ("ii", "Teach the assistance they can verify.", "Use AI with verification"),
        ("iii", "Build the expertise to supervise AI.", "Oversee and audit AI"),
    ]
    items = "".join(
        f'<li><span class="num" aria-hidden="true">{n}</span><span class="text">{text}</span>'
        f'<span class="mode">{mode}</span></li>' for n, text, mode in creed)
    doc = replace_once(
        doc,
        '<p>Preserve the judgment learners must develop. Teach the assistance they can verify. Build the expertise to supervise AI.</p>',
        f'<ol class="creed">{items}</ol>')
    return doc


def coverage_and_nav(doc, data):
    cov = data["coverage"]
    public, assigned = cov["public_replacement"], cov["assigned_corpus"]
    if assigned["received"] != 0 or cov["original_collection_match"] != "unverified":
        raise TransformError("coverage label below assumes the chair's collection was not received")
    nav_match = re.search(r'<nav class="nav" aria-label="Page sections">.*?</nav>', doc, re.S)
    if not nav_match:
        raise TransformError("nav not found")
    nav = nav_match.group(0)
    doc = replace_once(doc, nav, "")
    for section_id, num in SECTION_NUMBERS.items():
        nav = replace_once(nav, f'<a href="#{section_id}">',
                           f'<a href="#{section_id}"><span class="nav-num" aria-hidden="true">{num}</span>')

    notice = re.search(r'<div class="notice">(<strong>.*?</strong>.*?)</div>', doc, re.S)
    if not notice:
        raise TransformError("coverage notice not found")
    def ticks(done, total):
        return "".join("<i></i>" if k < done else '<i class="off"></i>' for k in range(total))

    filled = ticks(public["analyzed"], public["expected"])
    empty = ticks(assigned["received"], assigned["expected"])
    title = (f'Public replacement collection: {public["analyzed"]} of {public["expected"]} positions analyzed; '
             'chair’s original collection not available for matching.')
    coverage = (
        '<div class="coverage-shell"><section class="coverage" aria-labelledby="coverage-title">'
        '<div class="coverage-gauges"><div><p class="eyebrow">Corpus coverage</p>'
        f'<h2 class="coverage-title" id="coverage-title">{title}</h2></div>'
        '<div class="gauge"><span class="gauge-label">Public replacement<small>user-authorized reconstruction</small></span>'
        f'<span class="ticks" aria-hidden="true">{filled}</span>'
        f'<span class="gauge-value"><strong>{public["analyzed"]}</strong> of {public["expected"]} analyzed</span></div>'
        '<div class="gauge gauge-empty"><span class="gauge-label">Chair’s original collection<small>match unverified</small></span>'
        f'<span class="ticks" aria-hidden="true">{empty}</span>'
        f'<span class="gauge-value"><strong>{assigned["received"]}</strong> of {assigned["expected"]} received</span></div>'
        '</div>'
        f'<div class="coverage-note">{notice.group(1)}</div></section></div>' + nav)
    return replace_once(doc, notice.group(0), coverage)


def transform_evlinks(doc, evidence):
    pattern = re.compile(r'<a class="evlink" data-evidence="([^"]+)" href="#\1">(.*?) <span aria-hidden="true">↗</span>\s*</a>', re.S)

    def link(m):
        eid, label = m.group(1), m.group(2)
        stance = evidence.get(eid, {}).get("stance")
        if not stance:
            return m.group(0)
        spoken = "" if label.strip() == stance else f'<span class="sr-only"> ({stance})</span>'
        return (f'<a class="evlink" data-evidence="{eid}" href="#{eid}">{glyph(stance)}{label}{spoken} '
                '<span aria-hidden="true">↗</span></a>')

    doc, count = pattern.subn(link, doc)
    if count != doc.count('class="evlink"'):
        raise TransformError("some evidence links were not recognized")
    return doc


def transform_insights(doc):
    counter = iter(range(1, 4))

    def insight(m):
        body = m.group(1)
        body = re.sub(r'</p>(<a class="evlink".*)$', r'</p><div class="chips">\1</div>', body, flags=re.S)
        return f'<article class="insight"><span class="insight-num" aria-hidden="true">0{next(counter)}</span>{body}</article>'

    return sub_exact(r'<article class="insight">(.*?)</article>', insight, doc, 3, re.S)


def date_rail(text):
    """Turn 'publication date: X; ...; version: V. Retrieved D.' into a labelled date rail."""
    retrieved = re.search(r"Retrieved (\d{1,2} [A-Z][a-z]+ \d{4})\.", text)
    pairs = re.findall(r"([a-z]+ date|version): ([^;]+?)(?=; |\. Retrieved|$)", text)
    if not retrieved or not pairs:
        return None
    known, unknown, version = [], [], None
    for key, value in pairs:
        value = value.strip()
        if key == "version":
            version = value
        elif value == "unknown":
            unknown.append(key)
        else:
            known.append((value, DATE_LABELS.get(key, cap(key))))
    known.sort(key=lambda kv: kv[0])
    iso = datetime.datetime.strptime(retrieved.group(1), "%d %B %Y").date().isoformat()
    cells = "".join(f'<div><dt>{label}</dt><dd><time datetime="{value}">{value}</time></dd></div>'
                    for value, label in known)
    cells += f'<div class="retrieved"><dt>Retrieved</dt><dd><time datetime="{iso}">{iso}</time></dd></div>'
    notes = []
    if version and version != "unknown":
        notes.append(f"Version {html.escape(version)}")
    elif version == "unknown":
        unknown.append("version")
    if unknown:
        notes.append("Unknown: " + ", ".join(unknown))
    meta = f'<p class="date-unknowns">{" · ".join(notes)}</p>' if notes else ""
    return f'<dl class="date-rail" aria-label="Document dates">{cells}</dl>{meta}'


def transform_evidence_block(m):
    eid, head, body = m.group(1), m.group(2), m.group(3)
    parts = [p.strip() for p in html.unescape(head).split(" · ")]
    theme, status = parts[0], " · ".join(parts[1:])
    stance_match = re.search(r'<p class="small">Stance for this passage: ([a-z]+)\. ?([^<]*)</p>', body)
    if not stance_match:
        raise TransformError(f"stance line missing in {eid}")
    stance, conditions = stance_match.group(1), stance_match.group(2).strip()
    conditions_html = (f'<p class="ev-conditions"><span class="field-label">Conditions</span>{conditions}</p>'
                       if conditions else "")
    body = body.replace(stance_match.group(0), conditions_html)
    body = body.replace('<p class="small">', '<p class="ev-source">', 1)
    body = sub_exact(r"<p><strong>Interpretation\.</strong> (.*?)</p>",
                     r'<div class="interpretation"><p class="interp-label">Interpretation</p><p>\1</p></div>',
                     body, 1, re.S)
    new_head = (f'<div class="ev-head"><span class="ev-theme">{html.escape(cap(theme))}</span>'
                f'<span class="ev-status">{html.escape(cap(status))}</span>'
                f'<span class="ev-stance">{glyph(stance)}<span class="sr-only">Stance for this passage: </span>{cap(stance)}</span></div>')
    return f'<div class="evidence" id="{eid}" tabindex="-1">{new_head}{body}</div>'


def transform_sources(doc, stances):
    def source(m):
        art = m.group(0)
        art = re.sub(r'<span class="small">Date not stated</span>',
                     '<span class="date-chip date-unknown">Date not stated</span>', art, count=1)
        art = re.sub(r'<span class="small">([A-Z][a-z]+) (\d{4}(?:-\d{2}){0,2})</span>',
                     r'<span class="date-chip">\1 <time datetime="\2">\2</time></span>', art, count=1)
        if "date-chip" not in art:
            raise TransformError("source date not recognized")
        art = replace_once(art, '<p class="authority">', '<p class="authority"><span class="field-label">Authority</span>')
        art = sub_exact(r'(<div class="source-top">.*?</div>)(<h3>.*?</h3>)(<p class="authority">.*?</p>)',
                        r'<div class="source-meta">\1\3</div>\2', art, 1, re.S)
        ids = re.findall(r'<div class="evidence" id="([^"]+)"', art)
        strip = "".join(glyph(stances[i]) for i in ids)
        art = sub_exact(r"<summary>(Evidence &(?:amp;)? scope · \d+ passages?)</summary>",
                        rf'<summary>\1<span class="stance-strip" aria-hidden="true">{strip}</span></summary>', art, 1)
        dates = re.search(r'<p class="small">(publication date: [^<]*)</p>', art)
        if dates:
            rail = date_rail(dates.group(1))
            if rail:
                art = art.replace(dates.group(0), rail, 1)
        art = sub_exact(r'<div class="evidence" id="([^"]+)" tabindex="-1"><div class="eyebrow">([^<]*)</div>(.*?)</div>(?=<div class="evidence"|</details>)',
                        transform_evidence_block, art, len(ids), re.S)
        first = art.find('<div class="evidence"')
        art = art[:first] + '<div class="passages">' + art[first:]
        return replace_once(art, "</details></article>", "</div></details></article>")

    return sub_exact(r'<article class="source" id="source-[^"]+" data-id="[^"]+">.*?</article>', source, doc, 17, re.S)


def transform_explorer_layout(doc):
    doc = replace_once(
        doc, '<div class="filters"><div class="filter-grid">',
        '<div class="explorer-layout"><div class="filters" role="search" aria-labelledby="filters-title">'
        '<h3 class="filters-title" id="filters-title">Filter the collection</h3><div class="filter-grid">')
    return replace_once(
        doc, '<p id="empty" class="empty hidden">No positions match these combined filters. Try fewer filters or reset them.</p></section>',
        '<p id="empty" class="empty hidden">No positions match these combined filters. Try fewer filters or reset them.</p></div></section>')


def transform_comparison(doc, evidence):
    key = ('<div class="stance-key" aria-label="Key to stance marks"><span class="key-label">Key</span>'
           + "".join(f'<span>{glyph(s)}{cap(s)}</span>' for s in ("encouraged", "permitted", "conditional", "discouraged"))
           + '<span class="key-sep" aria-hidden="true"></span>'
           + "".join(f'<span>{glyph(s)}{cap(s)}</span>' for s in ("required", "prohibited"))
           + '<span class="key-sep" aria-hidden="true"></span>'
           + f'<span>{glyph("unclear")}Unclear</span><span class="key-none">{glyph("none")}Not coded</span></div>')
    doc = replace_once(doc, '<div class="table-wrap" role="region" aria-label="Scrollable evidence comparison" tabindex="0">',
                       key + '<div class="table-wrap" role="region" aria-label="Scrollable evidence comparison" tabindex="0">')
    doc = replace_once(doc, '<span class="uncoded">Not coded</span>',
                       f'<span class="uncoded">{glyph("none")}<span class="sr-only">Not coded</span></span>',
                       count=doc.count('<span class="uncoded">Not coded</span>'))

    note = re.search(r'<div class="matrix-note"><strong>(A real difference in detector guidance\.)</strong><p>(.*?)</p>'
                     r'(<a class="evlink" data-evidence="ubc-detection".*?</a>)(<a class="evlink" data-evidence="unsw-detection".*?</a>)'
                     r'<p><strong>(An authority warning from Brown\.)</strong> (.*?)</p>'
                     r'(<a class="evlink" data-evidence="P-BROWN-authority-error".*?</a>)</div>', doc, re.S)
    if not note:
        raise TransformError("matrix note not found")
    title, para, ubc_link, unsw_link, aw_title, aw_para, brown_link = note.groups()

    def side(eid, institution):
        e = evidence[eid]
        return (f'<figure class="tension-side"><figcaption><span class="t-inst">{institution}</span>'
                f'<span class="ev-stance">{glyph(e["stance"])}<span class="sr-only">Stance: </span>{cap(e["stance"])}</span></figcaption>'
                f'<blockquote>{html.escape(e["exact_excerpt"], quote=False)}</blockquote>'
                f'<p class="locator">{html.escape(e["locator"], quote=False)}</p></figure>')

    brown = evidence["P-BROWN-authority-error"]
    block = (
        '<div class="tensions"><article class="tension" aria-labelledby="tension-title">'
        f'<h3 id="tension-title">{title}</h3><div class="tension-pair">{side("ubc-detection", "UBC")}'
        '<div class="tension-sep" aria-hidden="true"><span>≠</span></div>'
        f'{side("unsw-detection", "UNSW Sydney")}</div><p class="tension-note">{para}</p>'
        f'<div class="chips">{ubc_link}{unsw_link}</div></article>'
        '<aside class="authority-warning" aria-labelledby="aw-title">'
        f'<p class="eyebrow">Authority check</p><p class="aw-title" id="aw-title">{aw_title}</p><p>{aw_para}</p>'
        f'<p class="locator">{html.escape(brown["locator"], quote=False)}</p>{brown_link}</aside></div>')
    return doc.replace(note.group(0), block, 1)


def transform_competencies(doc):
    grid = re.search(r'<div class="grid" id="competencies">(.*?)</div><p id="mission-empty"', doc, re.S)
    if not grid:
        raise TransformError("competency grid not found")
    cards = re.findall(r'<article class="competency".*?</article>', grid.group(1), re.S)
    if len(cards) != 7:
        raise TransformError(f"expected 7 competency cards, found {len(cards)}")
    lanes = []
    used = 0
    for index, (mode, numeral, label, desc) in enumerate(LANES, start=1):
        members = [c for c in cards if f'<span class="tag">{mode}</span>' in c]
        used += len(members)
        converted = []
        for card in members:
            card = replace_once(card, f'<span class="tag">{mode}</span>', f'<span class="tag mode-tag sr-only">{mode}</span>')
            card = sub_exact(r"<h3>(.*?)</h3>", r"<h4>\1</h4>", card, 1, re.S)
            card = sub_exact(r'<p class="small">([^<]*?) · draft proposal</p>',
                             r'<p class="comp-meta"><span>\1</span><span class="badge badge-draft">Draft proposal</span></p>', card, 1)
            converted.append(card)
        lanes.append(
            f'<div class="lane"><div class="lane-head"><div><span class="lane-num" aria-hidden="true">{numeral}</span>'
            f'<span class="lane-label">{label}</span></div><h3 id="lane-{index}">{mode}</h3><p>{desc}</p></div>'
            + "".join(converted) + "</div>")
    if used != len(cards):
        raise TransformError("a competency card has an unexpected mode")
    return doc.replace(grid.group(0), '<div class="lanes" id="competencies">' + "".join(lanes)
                       + '</div><p id="mission-empty"', 1)


def transform_international(doc):
    def card(m):
        art = m.group(0)
        art = sub_exact(r'<div class="eyebrow">([^<]*?) · external context</div>',
                        r'<div class="kicker"><span class="eyebrow">\1</span><span class="badge badge-external">External context</span></div>',
                        art, 1)
        line = re.search(r'<details><summary>Evidence, dates &(?:amp;)? applicability</summary><p class="small">'
                         r'((?:[A-Z][^:<]*: \d{4}(?:-\d{2}){0,2})(?: · [A-Z][^:<]*: \d{4}(?:-\d{2}){0,2})*)</p>', art)
        if line:
            entries = sorted((v, k) for k, v in (p.split(": ", 1) for p in line.group(1).split(" · ")))
            cells = "".join(
                ('<div class="retrieved">' if k == "Retrieved" else "<div>")
                + f'<dt>{k}</dt><dd><time datetime="{v}">{v}</time></dd></div>' for v, k in entries)
            art = art.replace(line.group(0), f'<dl class="date-rail" aria-label="Source dates">{cells}</dl>'
                              + line.group(0).replace(f'<p class="small">{line.group(1)}</p>', ""), 1)
        return art

    return sub_exact(r'<article class="international">.*?</article>', card, doc, 9, re.S)


def ledger(title, rows):
    items = "".join(
        f'<li><span class="status status-{r["status"]}" aria-hidden="true"></span>'
        f'<span>{html.escape(r["label"])}<span class="sr-only"> — {r["status"]}</span></span>'
        f'<span class="val{" word" if not any(ch.isdigit() for ch in r["value"]) else ""}">{html.escape(r["value"])}</span></li>'
        for r in rows)
    return f'<div class="ledger"><p class="ledger-title">{html.escape(title)}</p><ul>{items}</ul></div>'


def transform_methods(doc, data, checks):
    start_tag = '<div class="methods">'
    start = doc.find(start_tag)
    end = doc.find("</div></section><footer")
    if start < 0 or end < 0:
        raise TransformError("methods block not found")
    inner = doc[start + len(start_tag):end]
    design = (f'<p><strong>Visual design pass.</strong> On {checks["date_text"]}, {checks["tool"]} applied the Evidence Folio design system: '
              'typography, color, layout and presentational markup, plus a presentation-only script for section highlighting, '
              'active-filter states and printing every disclosure. Evidence records, coding, embedded page data and the page’s main '
              f'script were not changed. {html.escape(checks["summary"])}</p>')
    inner = sub_exact(r"(<p><strong>Actual execution\.</strong>.*?</p>)", lambda m: m.group(1) + design, inner, 1, re.S)
    round_one = [
        {"status": "passed", "label": "Evidence excerpts audited", "value": "68 + 30"},
        {"status": "passed", "label": "Static data, asset, encoding and palette checks", "value": "19 / 19"},
        {"status": "passed", "label": "Deterministic function checks", "value": "8 / 8"},
        {"status": "passed", "label": "Negative contract fixtures", "value": "5 / 5"},
        {"status": "partial", "label": "Keyboard focus, labels and 320 / 768 / 1280 px", "value": "sampled"},
        {"status": "unverified", "label": "Direct file opening, downloads and print", "value": "unverified"},
        {"status": "unverified", "label": "Full WCAG, screen readers and devices", "value": "unverified"},
    ]
    queue = "".join(
        f'<div class="queue-item"><p>{html.escape(q["question"])}</p>'
        f'<p class="meta"><b>{html.escape(q["priority"].replace("-", " "))}</b> · checked {q["last_checked"]} · {html.escape(q["status"])}</p></div>'
        for q in data["maintenance_queue"])
    aside = ('<aside class="methods-aside" aria-label="Verification and renewal records">'
             + ledger("Recorded in round 1 · Codex", round_one)
             + ledger(f'Design pass · {checks["tool"]} · {checks["date"]}', checks["rows"])
             + f'<div class="queue"><p class="queue-title">Renewal queue</p>{queue}</div></aside>')
    return doc[:start] + '<div class="methods"><div class="methods-main">' + inner + "</div>" + aside + doc[end:]


def transform_footer(doc):
    foot = re.search(r'<footer class="foot">(.*?)<br>(.*?)</footer></main>', doc, re.S)
    if not foot:
        raise TransformError("footer not found")
    first, second = foot.groups()
    new = ('</main><footer class="foot">' + RINGS_FOOT + '<div class="foot-inner"><div>'
           '<p class="foot-mark" aria-hidden="true">What are we here <span class="accent">together</span> to do?</p>'
           f'<p>{first}</p></div><div><p>{second}</p>'
           '<p><a href="#main">Back to top <span aria-hidden="true">↑</span></a></p></div></div></footer>')
    return doc.replace(foot.group(0), new, 1)


def main(argv):
    src = Path(argv[1]) if len(argv) > 1 else DEFAULT_SRC
    out = Path(argv[2]) if len(argv) > 2 else DEFAULT_OUT
    doc = src.read_text(encoding="utf-8")
    css = CSS_PATH.read_text(encoding="utf-8")
    js = JS_PATH.read_text(encoding="utf-8")
    checks = json.loads(CHECKS_PATH.read_text(encoding="utf-8"))
    checks["date_text"] = datetime.date.fromisoformat(checks["date"]).strftime("%-d %B %Y")
    if "</style" in css.lower() or "</script" in js.lower():
        raise TransformError("stylesheet or script would close its own element")

    data_block, data = page_data(doc)
    script_block = main_script(doc)
    evidence = {e["evidence_id"]: e for e in data["evidence"]}
    dom_stances = dict(re.findall(r'<div class="evidence" id="([^"]+)" tabindex="-1">.*?Stance for this passage: ([a-z]+)\.', doc, re.S))

    doc = sub_exact(r"<style>.*?</style>", lambda _: "<style>\n" + css + "</style>", doc, 1, re.S)
    doc = transform_masthead_and_hero(doc)
    doc = coverage_and_nav(doc, data)
    doc = transform_sections(doc)
    doc = transform_evlinks(doc, evidence)
    doc = transform_insights(doc)
    doc = transform_explorer_layout(doc)
    doc = transform_sources(doc, dom_stances)
    doc = transform_comparison(doc, evidence)
    doc = transform_competencies(doc)
    doc = transform_international(doc)
    doc = transform_methods(doc, data, checks)
    doc = transform_footer(doc)
    doc = replace_once(doc, "</body>", "<script>\n" + js + "</script></body>")

    if data_block not in doc or script_block not in doc:
        raise TransformError("page data or main script changed; refusing to write")
    for needle, count in (('<article class="source"', 17), ('<div class="evidence" id=', 68), ('<article class="competency"', 7),
                          ('<article class="scenario"', 6), ('<article class="international">', 9), ("<style>", 1)):
        if doc.count(needle) != count:
            raise TransformError(f"expected {count} of {needle!r} in output, found {doc.count(needle)}")
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} "
          f"({len(doc.encode('utf-8')):,} bytes, sha256 {hashlib.sha256(doc.encode('utf-8')).hexdigest()[:16]}…)")


if __name__ == "__main__":
    main(sys.argv)
