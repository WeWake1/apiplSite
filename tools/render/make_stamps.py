"""Draws the pallet markings as SVG and rasterises them to transparent PNGs (headless Chrome).

  IPPC / ISPM-15 mark: wheat-ear symbol + "IPPC", vertical separator, country-producer code
                       and treatment code inside a rectangular border (ISPM 15 Annex 2 layout)
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


def wheat(cx, top, bottom):
    """Stylised IPPC wheat ear: stem + paired grains + top grain."""
    parts = [f'<line x1="{cx}" y1="{bottom}" x2="{cx}" y2="{top + 14}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>']
    step = (bottom - top - 40) / 4
    for i in range(4):
        y = top + 26 + i * step
        for side in (-1, 1):
            parts.append(f'<ellipse cx="{cx + side * 11}" cy="{y}" rx="7" ry="15" fill="{INK}" '
                         f'transform="rotate({side * 32} {cx + side * 11} {y})"/>')
    parts.append(f'<ellipse cx="{cx}" cy="{top + 9}" rx="6.5" ry="13" fill="{INK}"/>')
    return "\n".join(parts)


def ippc_svg(country, code, treatment):
    text = f"{country}-{code}"
    w, h = 340, 150
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w * 2}" height="{h * 2}" viewBox="0 0 {w} {h}">
<rect x="5" y="5" width="{w - 10}" height="{h - 10}" rx="5" fill="none" stroke="{INK}" stroke-width="8"/>
<line x1="122" y1="5" x2="122" y2="{h - 5}" stroke="{INK}" stroke-width="7"/>
{wheat(48, 20, 130)}
<g font-family="{FONT}" font-weight="700" font-size="25" fill="{INK}" text-anchor="middle">
  <text x="96" y="40">I</text><text x="96" y="68">P</text><text x="96" y="96">P</text><text x="96" y="124">C</text>
</g>
<g font-family="{FONT}" font-weight="700" fill="{INK}">
  <text x="138" y="70" font-size="56" textLength="{w - 160}" lengthAdjust="spacingAndGlyphs">{text}</text>
  <text x="138" y="130" font-size="56">{treatment}</text>
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
