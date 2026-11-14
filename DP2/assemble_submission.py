"""Assemble the DP2 submission from the report PDF exported from VibeWrite.

Usage:  python3 assemble_submission.py <report.pdf> [out.pdf]

1. Inserts the Onshape shaft drawing (solution/cad/DP2-S01_Rotor_Shaft.pdf) as its own page right after the last page
   of the "Design Drawing and Bill of Materials" section, i.e. just before the page on which "Acceptable and
   Economically Viable Design" starts, so every Gradescope section stays on consecutive pages.
2. Stamps page numbers in the style-guide format: bottom-right corner, Roboto 11, "page/total" (e.g. 2/20). The cover
   page and the drawing sheet are counted but not stamped.

Needs poppler (pdftotext), pypdf and matplotlib (used only to set the page numbers in Roboto).
"""
import io, os, re, subprocess, sys

from pypdf import PdfReader, PdfWriter

HERE = os.path.dirname(os.path.abspath(__file__))
DRAWING = os.path.join(HERE, "solution", "cad", "DP2-S01_Rotor_Shaft.pdf")
ROBOTO = os.path.join(HERE, "FBD_report", "fonts", "Roboto-Regular.ttf")
MARGIN = 72.0          # 1 in page margin, points
BASELINE = 40.0        # page-number baseline above the bottom edge, points


def page_texts(pdf):
    out = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    return out.split("\f")[:-1] if out.endswith("\f") else out.split("\f")


def stale_numbers(pdf, n_pages):
    """Hand-typed "n/N" footers left in the export: {page index: [(xMin, yMin, xMax, yMax) from the top-left, points]}."""
    out = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    found = {}
    for i, page in enumerate(out.split("<page ")[1:n_pages + 1]):
        h = float(re.search(r'height="([\d.]+)"', page).group(1))
        for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(\d+/\d+)</word>', page):
            x0, y0, x1, y1 = map(float, m.groups()[:4])
            if y0 > h - MARGIN:                      # only inside the bottom margin
                found.setdefault(i, []).append((x0, y0, x1, y1))
    return found


def number_overlay(label, width, height, cover=()):
    """One transparent PDF page, the size of the target page: the page number, over white patches that hide any
    stale footer number listed in `cover`."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    plt.rcParams["pdf.fonttype"] = 42
    fig = plt.figure(figsize=(width / 72.0, height / 72.0))
    for x0, y0, x1, y1 in cover:
        fig.patches.append(plt.Rectangle(((x0 - 3) / width, (height - y1 - 3) / height), (x1 - x0 + 6) / width,
                                         (y1 - y0 + 6) / height, transform=fig.transFigure, fc="white", ec="none"))
    fig.text((width - MARGIN) / width, BASELINE / height, label, ha="right", va="baseline", fontsize=11,
             fontproperties=fm.FontProperties(fname=ROBOTO, size=11), color="black")
    buf = io.BytesIO()
    fig.savefig(buf, format="pdf", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return PdfReader(buf).pages[0]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    report = args[0]
    out = args[1] if len(args) > 1 else os.path.join(HERE, "DP2_submission.pdf")
    pages = page_texts(report)
    norm = [" ".join(p.split()) for p in pages]
    start = next((i for i, p in enumerate(norm) if "Acceptable and Economically Viable Design" in p
                  and "Table 7" in p), None)
    if start is None:
        sys.exit("Could not find the page where 'Acceptable and Economically Viable Design' starts.")
    bom = max(i for i, p in enumerate(norm[:start + 1]) if "Bill of materials" in p or "Bill of Materials" in p)
    if not (bom < start):
        sys.exit("The BOM and the next section share a page; add a page break before the next section first.")

    rep, drw = PdfReader(report), PdfReader(DRAWING)
    if len(rep.pages) != len(pages):
        sys.exit(f"Page count mismatch: pdftotext {len(pages)}, pypdf {len(rep.pages)}.")
    seq = [(p, True) for p in rep.pages[:start]] + [(p, False) for p in drw.pages] + [(p, True) for p in rep.pages[start:]]
    total = len(seq)
    has_cover = "AUTHOR" in norm[0]
    # Hand-typed footer numbers left in the export do not count the drawing page: hide them under the new ones.
    stale = stale_numbers(report, len(pages))
    if stale:
        print(f"Note: covered stale footer numbers on report page(s) {', '.join(str(k + 1) for k in sorted(stale))}.")
    index = list(range(start)) + [None] * len(drw.pages) + list(range(start, len(pages)))   # report index per page
    w = PdfWriter()
    stamped = 0
    for n, (page, stamp) in enumerate(seq, start=1):
        if stamp and not (n == 1 and has_cover):
            box = page.mediabox
            page.merge_page(number_overlay(f"{n}/{total}", float(box.width), float(box.height),
                                           cover=stale.get(index[n - 1], ())))
            stamped += 1
        w.add_page(page)
    with open(out, "wb") as f:
        w.write(f)

    def find(key):
        return next((i for i, p in enumerate(norm) if key in p), None)
    marks = [("1 Shaft Design Calculations", find("Geometry, Loads and Assumptions")),
             ("2 Key and Set Screw", find("Shaft Connection Hardware Design Calculations")),
             ("3 Pin and Retaining Ring", find("3. Pin")),
             ("4 Drawing and Bill of Materials", find("Design Drawing and Bill of Materials")),
             ("5 Economically Competitive Design", start)]
    shift = lambda i: i + 1 + (len(drw.pages) if i >= start else 0)      # report index -> submission page number
    print(f"{len(pages)} report pages + {len(drw.pages)} drawing page = {total}; drawing is page {start + 1}; "
          f"{stamped} pages numbered{' (cover not stamped)' if has_cover else ''}.")
    for k, (name, i) in enumerate(marks):
        if i is None:
            print(f"  {name}: heading not found"); continue
        nxt = next((j for _, j in marks[k + 1:] if j is not None), None)
        last = total if nxt is None else shift(nxt) - 1
        if name.startswith("4"):
            last = start + len(drw.pages)                                  # the drawing sheet closes section 4
        print(f"  {name}: pages {shift(i)}-{last}")
    print("Written:", out)


if __name__ == "__main__":
    main()
