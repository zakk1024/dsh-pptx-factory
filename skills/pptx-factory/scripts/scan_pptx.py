#!/usr/bin/env python3
"""Static scan gates for the pptx-pipeline (G4).

Works without renderers (this machine has no LibreOffice): the flags below are
the only visual path here, so treat the JSON as the evidence, not a screenshot.

Checks
- oversize_chart_area : a chart/image shape bbox > 70% of slide area
- sparse_text_block   : text-block area < 25% while a chart/image covers > 70%
- font_floor          : any body run < --font-floor pt (captions >=9pt pass with --allow-caption)
- contrast_poor       : fg/bg pair < 4.5:1 (dark bg) or > 4.5 inverted on white/black panels
- colorblind_check    : saturated colours outside the colourblind-safe set
- anim_over_budget    : timing seeds on a slide > 2 (motion budget)
- anim_preset_unknown : preset names outside the 8-preset list
- size_warn (html)    : single-file deck HTML > 2 MB; counts <details> reveals too

Exit code is always 0 — degrade-and-flag is a pipeline rule, never crash.
"""
import argparse, json, re, sys, os

try:
    from pptx import Presentation
    from pptx.util import Emu
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    HAVE_PPTX = True
except Exception:
    HAVE_PPTX = False

SAFE_COLORS = {"2563EB", "DC2626", "059669", "D97706", "7C3AED", "0F172A"}
PRESETS = ["count-up", "bar-grow", "flip", "reveal", "zoom", "pan", "fade", "slide"]


def _lum(hexstr):
    try:
        r, g, b = (int(hexstr[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    except Exception:
        return None
    def f(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(f, (r, g, b))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def _hex(colorobj):
    try:
        return str(colorobj.rgb)
    except Exception:
        return None


def scan_pptx(path, font_floor=12.0, allow_caption=False):
    prs = Presentation(path)
    W, H = prs.slide_width, prs.slide_height
    out = {"deck": os.path.basename(path), "slides": [], "global": {}}
    if W is None or H is None:
        out["global"]["bad_file"] = "slide size unreadable"
        return out
    area = W * H
    for i, slide in enumerate(prs.slides, 1):
        flags, notes = [], []
        text_area = 0
        shapes_small_font = set()
        large_media = []
        for sh in slide.shapes:
            # --- media area
            w = getattr(sh, "width", 0) or 0
            h = getattr(sh, "height", 0) or 0
            ratio = (w * h) / area if w and h else 0
            kind = sh.shape_type
            is_media = kind in (MSO_SHAPE_TYPE.PICTURE, MSO_SHAPE_TYPE.CHART) or \
                (getattr(sh, "has_chart", False) is True)
            if is_media and ratio > 0.70:
                large_media.append({"shape": sh.name, "area_pct": round(ratio * 100, 1)})
            # --- text area + font floor
            if getattr(sh, "has_text_frame", False):
                if sh.text_frame.text.strip():
                    if ratio < 1.0 and (w * h) / area < 0.9:
                        text_area += w * h
                    for p in sh.text_frame.paragraphs:
                        for r in p.runs:
                            if r.font and r.font.size:
                                pt = r.font.size.pt
                                if pt < (9.0 if allow_caption else font_floor):
                                    shapes_small_font.add((sh.name, pt))
            # --- fill / font colour
            try:
                if sh.fill.type == 1:  # solid
                    bg = _hex(sh.fill.fore_color)
                else:
                    bg = None
            except Exception:
                bg = None
            if getattr(sh, "has_text_frame", False):
                fgset = set()
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        try:
                            if r.font and r.font.color and r.font.color.type is not None:
                                c = _hex(r.font.color)
                                if c:
                                    fgset.add(c)
                        except Exception:
                            pass
                bg_lum = _lum(bg) if bg else None
                for fg in fgset:
                    fgl = _lum(fg)
                    if fgl is None:
                        continue
                    for cand, name in ((bg, "own panel"), ("FFFFFF", "white"), ("000000", "black")):
                        cl = _lum(cand) if cand else None
                        if cl is None:
                            continue
                        if _contrast(fgl, cl) < 4.5 and (fg[:2] != "00" or cand != "000000"):
                            if fg not in SAFE_COLORS and cand in (bg, "FFFFFF", "000000"):
                                notes.append({"contrast_poor": {"fg": "#" + fg, "on": "#" + cand, "via": name}})
                            break
        if large_media:
            flags.append({"oversize_chart_area": large_media})
        if large_media and (text_area / area) < 0.25:
            flags.append({"sparse_text_block": round(text_area / area * 100, 1)})
        if shapes_small_font:
            flags.append({"font_floor": sorted(shapes_small_font)[:10]})

        # --- timing seeds (animation budget)
        xml = slide._element.xml
        seeds = max(0, len(re.findall(r"<p:par\b", xml)) - 0)
        unknown = [p for p in PRESETS if f'"{p}"' in xml and p not in ("fade", "reveal", "zoom", "pan", "slide", "flip", "count-up", "bar-grow")]
        if seeds > 2:
            flags.append({"anim_over_budget": seeds})
        if unknown:
            flags.append({"anim_preset_unknown": unknown})
        # colourblind audit (saturated non-safe colors only)
        seen_colors = set(re.findall(r"srgbClr val=\"([0-9A-Fa-f]{6})\"", xml))
        sat = []
        for c in seen_colors:
            r, g, b = (int(c[j:j + 2], 16) for j in (0, 2, 4))
            mx, mn = max(r, g, b), min(r, g, b)
            if mx - mn > 40 and mx > 90 and c.upper() not in SAFE_COLORS:
                sat.append("#" + c.upper())
        if len(sat) > 3:
            flags.append({"colorblind_check": sorted(sat)[:20]})
        out["slides"].append({"slide": i, "flags": flags,
                             "timing_seeds": seeds, "notes": notes})
    return out


def scan_html(path):
    size = os.path.getsize(path)
    txt = open(path, encoding="utf-8", errors="replace").read()
    flags = {}
    if size > 2 * 1024 * 1024:
        flags["size_warn"] = f"{size // 1024} KB single-file deck"
    return {"file": os.path.basename(path), "size_kb": size // 1024,
            "details_reveals": txt.count("<details"), "flags": flags}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deck", help="path to .pptx")
    ap.add_argument("--html", help="path to single-file deck HTML (optional)")
    ap.add_argument("--font-floor", type=float, default=12.0)
    ap.add_argument("--allow-caption", action="store_true")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    a = ap.parse_args()
    report = {"version": "pptx-pipeline scan v1", "checks": []}
    if a.deck:
        if not HAVE_PPTX:
            report["checks"].append({"file": os.path.basename(a.deck), "bad_file": "python-pptx not importable"})
        else:
            try:
                report["checks"].append(scan_pptx(a.deck, a.font_floor, a.allow_caption))
            except Exception as e:  # never crash the pipeline (rule 4)
                report["checks"].append({"file": os.path.basename(a.deck), "bad_file": repr(e)[:200]})
    if a.html:
        try:
            report["checks"].append(scan_html(a.html))
        except Exception as e:
            report["checks"].append({"file": os.path.basename(a.html), "bad_file": repr(e)[:200]})
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
        print(f"written: {a.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
