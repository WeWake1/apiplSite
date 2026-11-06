"""Draws the pallet markings as SVG and rasterises them to transparent PNGs (headless Chrome).

  IPPC / ISPM-15 mark: IPPC symbol (traced from the owner's reference artwork), vertical separator,
                       country-producer code and, centred under it, the treatment code, inside a
                       rectangular border (ISPM 15 Annex 2 layout)
  EPAL oval, EPAL with superscript 2 / 3 (EPAL 2 / EPAL 3 right-hand block)
  CP type marks CP1 ... CP9

Only brands that hold the matching licence/registration may use these marks.
usage: python3 make_stamps.py <brand.json>      -> stamps/<name>.png
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stamps")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
INK = "#21140c"
FONT = "'Arial Narrow', 'Helvetica Neue', Arial, sans-serif"


# The IPPC symbol, traced from the owner's reference artwork (800 x 800 px; these are its pixel coordinates).
# Strokes (stem, left rail, five rungs, right branch) as filled outlines; the letters I, P, P, C as traced outlines.
IPPC_BOX = (337.0, 201.0, 476.0, 652.0)   # ink bounding box: x0, y0, x1, y1
IPPC_STROKES = [
    [(397.12, 201.0), (409.2, 201.0), (409.2, 652.0), (397.12, 652.0)],
    [(343.0, 278.0), (403.16, 312.16), (403.16, 327.18), (343.0, 295.14)],
    [(343.0, 331.09), (403.16, 365.07), (403.16, 378.85), (343.0, 344.74)],
    [(343.0, 383.99), (403.16, 418.1), (403.16, 431.86), (343.0, 397.73)],
    [(343.0, 437.92), (403.16, 472.11), (403.16, 485.8), (343.0, 451.73)],
    [(337.0, 487.61), (403.16, 525.02), (403.16, 538.82), (337.0, 501.25)],
    [(337.0, 236.6), (349.0, 236.6), (349.0, 508.07), (337.0, 501.25)],
    [(403.16, 524.56), (458.8, 492.15), (464.83, 502.51), (403.16, 538.39)],
]
IPPC_LETTERS = [
    ('M451.50,261.09 445.50,261.08 444.41,260.50 444.41,219.50 444.93,218.50 445.50,218.26 451.50,218.26 '
     '452.07,219.50 452.07,260.50Z'),
    ('M451.50,327.07 445.50,327.06 444.35,326.50 444.50,285.03 444.76,284.50 445.50,284.17 459.50,284.16 '
     '463.50,284.46 466.50,285.12 470.50,287.50 472.50,289.69 474.03,292.50 474.78,294.50 474.99,298.50 '
     '474.78,300.50 473.74,303.50 470.73,307.50 467.50,309.75 463.50,310.84 452.50,311.00 452.05,311.50 '
     '452.06,326.50ZM462.28,303.50 464.95,302.50 465.93,301.50 467.04,299.50 467.29,297.50 467.06,295.50 '
     '466.77,294.50 465.98,293.50 464.50,292.30 461.50,291.60 453.50,291.47 452.50,291.69 452.07,292.50 '
     '452.05,302.50 452.29,303.50 453.50,303.76 458.50,303.79Z'),
    ('M451.50,393.07 445.50,393.10 444.40,392.50 444.50,351.23 444.77,350.50 445.50,350.16 460.50,350.19 '
     '463.50,350.42 466.50,351.10 468.50,352.09 470.46,353.50 472.50,355.72 473.66,357.50 474.79,360.50 '
     '474.90,361.50 474.95,365.50 474.50,367.30 473.62,369.50 471.64,372.50 470.50,373.73 467.50,375.69 '
     '463.50,376.81 453.50,376.93 452.50,377.02 452.06,377.50 452.06,392.50ZM462.16,369.50 464.50,368.85 '
     '466.66,366.50 467.28,363.50 466.81,360.50 466.01,359.50 464.50,358.24 461.50,357.55 452.50,357.65 '
     '452.07,358.50 452.07,368.50 452.41,369.50 460.50,369.76Z'),
    ('M463.50,456.80 459.50,457.20 456.50,457.10 454.50,456.93 451.50,455.82 448.50,453.81 446.26,451.50 '
     '444.36,448.50 443.27,444.50 443.12,428.50 443.30,426.50 444.06,423.50 446.40,419.50 448.50,417.40 '
     '451.50,415.31 454.50,414.19 458.50,413.86 462.50,414.14 465.50,415.14 467.50,416.27 469.98,418.50 '
     '471.64,420.50 472.78,422.50 473.91,425.50 474.06,426.50 473.50,427.36 466.50,427.22 464.89,424.50 '
     '462.50,422.30 459.50,421.33 458.50,421.31 455.50,422.02 453.50,423.30 452.34,424.50 451.06,427.50 '
     '450.80,435.50 451.03,443.50 452.29,446.50 453.50,447.93 456.51,449.50 457.50,449.81 459.50,449.83 '
     '462.50,448.86 463.50,448.08 464.98,446.50 466.50,444.22 473.50,444.08 474.00,444.50 473.80,446.50 '
     '472.50,449.47 471.18,451.50 467.50,454.91Z'),
]


def ippc_symbol(x, y, h):
    """The IPPC symbol, h tall, with the top-left corner of its ink at (x, y). Returns (svg, width)."""
    x0, y0, x1, y1 = IPPC_BOX
    s = h / (y1 - y0)
    strokes = "".join("M" + " ".join(f"{px},{py}" for px, py in poly) + "Z" for poly in IPPC_STROKES)
    return (f'<g transform="translate({x - x0 * s:.3f} {y - y0 * s:.3f}) scale({s:.5f})" fill="{INK}">'
            f'<path d="{strokes}"/><path fill-rule="evenodd" d="{"".join(IPPC_LETTERS)}"/></g>'), (x1 - x0) * s


def ippc_svg(country, code, treatment):
    """IPPC symbol | country-producer code with the treatment code centred under it. The box is only as
    wide as the symbol and the code need; render_pallet.py takes the mark's proportions from the PNG."""
    text = f"{country}-{code}"
    h, sym_h, pad, code_w = 150, 124, 13, 178      # code_w: width of the "IN-083" line (its textLength)
    inner = 6.25                                   # inside edge of the 4.5-wide border drawn at 4
    sym, sym_w = ippc_symbol(inner + pad, (h - sym_h) / 2, sym_h)
    sep = inner + pad + sym_w + pad + 2            # centre of the 4-wide separator
    w = round(sep + 2 + 16 + code_w + 16 + inner)
    cx = (sep + 2 + w - inner) / 2                 # middle of the right-hand panel
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w * 2}" height="{h * 2}" viewBox="0 0 {w} {h}">
<rect x="4" y="4" width="{w - 8}" height="{h - 8}" rx="5" fill="none" stroke="{INK}" stroke-width="4.5"/>
<line x1="{sep:.2f}" y1="4" x2="{sep:.2f}" y2="{h - 4}" stroke="{INK}" stroke-width="4"/>
{sym}
<g font-family="{FONT}" font-weight="700" fill="{INK}">
  <text x="{cx - code_w / 2:.2f}" y="72" font-size="54" letter-spacing="2" textLength="{code_w}" lengthAdjust="spacingAndGlyphs">{text}</text>
  <text x="{cx:.2f}" y="128" font-size="54" letter-spacing="3" text-anchor="middle">{treatment}</text>
</g>
</svg>'''


def epal_svg(sup=""):
    w = 300 if not sup else 336
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w * 2}" height="300" viewBox="0 0 {w} 150">
<ellipse cx="150" cy="77" rx="140" ry="64" fill="none" stroke="{INK}" stroke-width="9"/>
<text x="150" y="107" font-family="{FONT}" font-weight="700" font-size="88" fill="{INK}" text-anchor="middle"
      textLength="200" lengthAdjust="spacingAndGlyphs">EPAL</text>
{f'<text x="304" y="44" font-family="{FONT}" font-weight="700" font-size="44" fill="{INK}">{sup}</text>' if sup else ''}
</svg>'''


def cp_svg(n):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="440" height="220" viewBox="0 0 220 110">
<text x="110" y="86" font-family="{FONT}" font-weight="700" font-size="88" fill="{INK}" text-anchor="middle">CP{n}</text>
</svg>'''


def rasterise(svg, path):
    import re
    w, h = (int(v) for v in re.search(r'width="(\d+)" height="(\d+)"', svg).groups())
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "s.html")
        with open(src, "w") as f:
            f.write(f'<!doctype html><html><body style="margin:0;background:transparent">{svg}</body></html>')
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={w},{h}", "--default-background-color=00000000",
                        f"--screenshot={path}", "file://" + src], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    brand = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "brand.json")))
    os.makedirs(OUT, exist_ok=True)
    ip = brand["ippc"]
    jobs = {f"ippc_{ip['country']}-{ip['code']}_{ip['treatment']}": ippc_svg(ip["country"], ip["code"], ip["treatment"])}
    if brand.get("epal"):
        jobs.update({"epal": epal_svg(), "epal2": epal_svg("2"), "epal3": epal_svg("3")})
        jobs.update({f"cp{n}": cp_svg(n) for n in range(1, 10)})
    for name, svg in jobs.items():
        rasterise(svg, os.path.join(OUT, name + ".png"))
        print("stamp", name)


if __name__ == "__main__":
    main()
