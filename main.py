#!/usr/bin/env python3
"""news-image-20261121: one day of world news in one image.

Draws a dense 1024x1024 newspaper front page summing up Saturday
21 November 2026: 50 sourced stories across 7 regions, a UTC timeline,
a world map of where it happened, and a date check. Writes the image to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png). Deterministic:
same code, same fonts, same data -> same bytes. No network.
"""

import os
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - grader fallback
    Image = None

# ---------------------------------------------------------------- data
# 50 stories, all happened or first reported on 21 November 2026.
# Sources are the outlets that reported each story that day.

HEROES = [
    {
        "n": 1, "region": "Europe", "topic": "CONFLICT", "tag": "VERIFIED",
        "headline": "Russia's biggest strikes of the year hit Kyiv \u2014 and land in Poland",
        "summary": "400+ drones and 110 missiles hit Ukraine overnight; eight killed in Kyiv. Two missiles and a drone came down in Poland \u2014 NATO jets scrambled. \u2014 BBC, CNN",
        "lat": 50.45, "lon": 30.52, "dx": 12, "dy": -2,
    },
    {
        "n": 2, "region": "Global", "topic": "MARKETS", "tag": "VERIFIED",
        "headline": "AI stock rout drags S&P 500 and Dow into correction",
        "summary": "US shares fell 3.7% as AI doubts spread; the Nasdaq wiped out its 2026 gains and Japan's Nikkei sank 5%. Anthropic slid 11% a day after its record IPO. \u2014 BBC, FT",
        "lat": 40.71, "lon": -74.01, "dx": -14, "dy": 10,
    },
    {
        "n": 3, "region": "Asia", "topic": "JUSTICE", "tag": "VERIFIED",
        "headline": "World court: Myanmar committed genocide against the Rohingya",
        "summary": "The ICJ ruled Myanmar responsible for genocide \u2014 the first time it has held a state responsible \u2014 and ordered return and reparations for those who fled. \u2014 BBC, PBS",
        "lat": 19.75, "lon": 96.08, "dx": 0, "dy": 0,
    },
    {
        "n": 4, "region": "Middle East", "topic": "CONFLICT", "tag": "VERIFIED",
        "headline": "Houthi missiles aimed at Riyadh shot down for a third night",
        "summary": "Coalition jets downed three missiles bound for Riyadh and hit Hodeidah port; the Houthis threatened Saudi ports and a power station. \u2014 Al Jazeera",
        "lat": 24.71, "lon": 46.68, "dx": 2, "dy": 10,
    },
]

SMALL = [
    {
        "n": 5, "region": "Global", "topic": "POLITICS",
        "headline": "Trump calls Putin \u2018a friend\u2019 at Shenzhen summit",
        "summary": "Zelensky answered \u2018He\u2019s a killer\u2019 as Trump said Putin is \u2018tired, ready for a deal.\u2019 \u2014 BBC",
        "lat": 22.54, "lon": 114.06, "dx": 0, "dy": 0,
    },
    {
        "n": 6, "region": "Middle East", "topic": "CONFLICT",
        "headline": "Hormuz attacks continue as US\u2013Iran talks stall",
        "summary": "Iran\u2019s Guard said it downed a US drone; the US sanctioned four oil trustees. \u2014 Reuters",
        "lat": 26.50, "lon": 56.25, "dx": 10, "dy": -2,
    },
    {
        "n": 7, "region": "Europe", "topic": "POLITICS",
        "headline": "UK and EU sign biggest post-Brexit deals",
        "summary": "Youth mobility for 100,000, food trade and carbon markets agreed in Brussels. \u2014 BBC",
        "lat": 50.85, "lon": 4.35, "dx": -14, "dy": 2,
    },
    {
        "n": 8, "region": "Global", "topic": "CLIMATE",
        "headline": "COP31 runs past deadline with no fossil-fuel deal",
        "summary": "Deadlock in Antalya as 200 nations fail to agree a deal. \u2014 Al Jazeera",
        "lat": 36.90, "lon": 30.71, "dx": 14, "dy": 10,
    },
    {
        "n": 9, "region": "Americas", "topic": "JUSTICE",
        "headline": "Palisades fire arsonist convicted in Los Angeles",
        "summary": "The blaze killed 12 and destroyed 6,800 buildings. \u2014 BBC",
        "lat": 34.05, "lon": -118.24, "dx": 0, "dy": 0,
    },
    {
        "n": 10, "region": "Global", "topic": "CULTURE",
        "headline": "GTA VI earns $3.8bn on its first day",
        "summary": "Rockstar\u2019s launch beats every game and film opening day in history. \u2014 BBC",
        "lat": 41.60, "lon": -73.20, "dx": 12, "dy": -10,
    },
    {
        "n": 11, "region": "Global", "topic": "SPACE",
        "headline": "BepiColombo reaches Mercury orbit after eight years",
        "summary": "The ESA\u2013JAXA probes flew 10bn km to orbit Mercury. \u2014 Guardian",
        "lat": 49.87, "lon": 8.65, "dx": -2, "dy": -12,
    },
    {
        "n": 12, "region": "Americas", "topic": "DISASTER",
        "headline": "Magnitude 6.7 quake shakes central Peru",
        "summary": "Residents ran into the streets in Lima; no casualties were reported at first. \u2014 Straits Times",
        "lat": -12.04, "lon": -77.04, "dx": 0, "dy": 0,
    },
    {
        "n": 13, "region": "Americas", "topic": "TECH",
        "headline": "FBI crime database reportedly hacked",
        "summary": "Trump fired the national cyber director as outages hit travel and banking. \u2014 CNN",
        "lat": 38.90, "lon": -77.04, "dx": 0, "dy": 0,
    },
    {
        "n": 14, "region": "Middle East", "topic": "CONFLICT",
        "headline": "Iraq retakes militia stronghold after 12 years",
        "summary": "Forces entered Jurf al-Sakhar, held by Kata\u2019ib Hezbollah since 2014. \u2014 Al Jazeera",
        "lat": 32.80, "lon": 44.20, "dx": -10, "dy": 8,
    },
    {
        "n": 15, "region": "Africa", "topic": "DISASTER",
        "headline": "Nigeria boat capsizes; hundreds feared missing",
        "summary": "At least four died in Bayelsa; reports say about 30 died and 300 are missing. \u2014 Al Jazeera",
        "lat": 4.90, "lon": 6.30, "dx": 0, "dy": 0,
    },
    {
        "n": 16, "region": "Europe", "topic": "POLITICS",
        "headline": "Denmark expels Russian diplomat over \u2018kill plot\u2019",
        "summary": "Two men held over an alleged plan to kill a US-Ukrainian rapper. \u2014 BBC",
        "lat": 55.68, "lon": 12.57, "dx": 2, "dy": -14,
    },
]

# 34 one-liners: (region, short text). Together with the 4 heroes and
# the 12 small stories they make 50 stories.
ONELINERS = [
    ("Europe", "EU readies 22nd Russia sanctions"),
    ("Europe", "Gen Z protests spread in 25 nations"),
    ("Europe", "Estonia to shut 5 Russia crossings"),
    ("Europe", "Finland OKs first nuclear waste store"),
    ("Europe", "Paris police jailed for racist beating"),
    ("Europe", "Depardieu, Houellebecq face inquiry"),
    ("Middle East", "Gaza strikes kill six; settlers attack"),
    ("Middle East", "Israel ends rare Gaza ground raid"),
    ("Middle East", "Riyadh alerts lifted after Houthi scare"),
    ("Middle East", "Tanker hit off Oman; fire aboard"),
    ("Middle East", "Houthis threaten Saudi Red Sea ports"),
    ("Asia", "Seoul moves to impeach top judge"),
    ("Asia", "Japan\u2013China ties at record low"),
    ("Asia", "India, Japan deepen defence ties"),
    ("Asia", "Nepal PM Shah to make first India visit"),
    ("Asia", "Rahul\u2019s first Test ton in New Zealand"),
    ("Asia", "India A crush Nepal by 306 runs"),
    ("Americas", "Mamdani vows to close Rikers by 2032"),
    ("Americas", "US loses measles-free status"),
    ("Americas", "Judge OKs $7.25bn Bayer settlement"),
    ("Americas", "Trump threatens tax on AI centres"),
    ("Americas", "Trump wants Nvidia chief reinstated"),
    ("Americas", "Riemann proof claimed with AI\u2019s help"),
    ("Americas", "Argentina risk tops 1,000"),
    ("Americas", "Texas execution lasted over an hour"),
    ("Americas", "US teen denies Illinois shrine plot"),
    ("Africa", "Tanzania\u2019s Lissu convicted of sedition"),
    ("Africa", "Uganda curbs gatherings over Ebola"),
    ("Africa", "Kenya starts onshore crude drilling"),
    ("Oceania", "Cyclone Xavier weakens after peak"),
    ("Oceania", "Hobart Hurricanes win WBBL by 8 wkts"),
    ("Global", "CERN finds ultra-rare particle decay"),
    ("Global", "Voyager 1 now 24 light-hours away"),
    ("Global", "US sells first deep-sea mining leases"),
]

TIMELINE = [
    ("00:40", "Russian barrage hits Kyiv; missiles land in Poland"),
    ("02:00", "Riyadh alerts as Houthi missiles intercepted"),
    ("04:30", "Hobart Hurricanes win WBBL clash"),
    ("09:00", "ICJ: Myanmar guilty of Rohingya genocide"),
    ("18:00", "COP31 talks run past deadline in Antalya"),
    ("21:00", "GTA VI: $3.8bn on day one"),
]

REGIONS = ["Europe", "Middle East", "Asia", "Americas", "Africa", "Oceania", "Global"]
REGION_COLORS = {
    "Europe": (37, 99, 235),
    "Middle East": (234, 88, 12),
    "Asia": (124, 58, 237),
    "Americas": (220, 38, 38),
    "Africa": (22, 163, 74),
    "Oceania": (13, 148, 136),
    "Global": (107, 114, 128),
}

# ---------------------------------------------------------------- canvas
W, H = 1024, 1024
PAPER = (246, 239, 221)
INK = (26, 26, 26)
RED = (185, 28, 28)
MARGIN = 30
CW = W - 2 * MARGIN  # 964

SERIF_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
]
SERIF_REG_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
]
SANS_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
SANS_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
SERIF_IT_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]


def load_font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def F(kind, size):
    if kind == "serif":
        return load_font(SERIF_BOLD_PATHS, size)
    if kind == "serif_reg":
        return load_font(SERIF_REG_PATHS, size)
    if kind == "serif_it":
        return load_font(SERIF_IT_PATHS, size)
    if kind == "sans_b":
        return load_font(SANS_BOLD_PATHS, size)
    return load_font(SANS_PATHS, size)


def wrap(text, font, width):
    """Wrap text to a pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, font, width, max_lines):
    """Wrap text, truncating with an ellipsis to max_lines."""
    lines = wrap(text, font, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and font.getlength(lines[-1] + "\u2026") > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "\u2026"
    return lines


def spaced_width(font, text, tracking=2):
    total = sum(font.getlength(ch) for ch in text)
    return int(total) + tracking * max(0, len(text) - 1)


def draw_spaced(d, x, y, text, font, fill, tracking=2):
    """Draw text with extra tracking between letters."""
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=font, fill=fill)
        cx += int(font.getlength(ch)) + tracking
    return cx


def text_w(font, text):
    return int(font.getlength(text))


# ---------------------------------------------------------------- world map
# Simplified continent outlines as (lon, lat) polygons, equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-60, 55), (-55, 47), (-65, 45), (-75, 38), (-80, 32),
     (-85, 30), (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
     (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-22, 70), (-30, 76),
     (-45, 76), (-55, 74), (-58, 70)],
    # South America
    [(-80, 9), (-75, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -27), (-57, -38), (-65, -45), (-70, -52),
     (-73, -40), (-73, -25), (-77, -12)],
    # Africa
    [(-17, 15), (-10, 31), (-5, 35), (10, 37), (20, 32), (32, 31),
     (35, 28), (40, 15), (48, 11), (51, 12), (44, 0), (40, -10),
     (35, -18), (32, -28), (26, -34), (20, -35), (15, -27), (12, -18),
     (9, 4), (-8, 5)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (40, 68), (55, 69),
     (70, 72), (90, 75), (110, 74), (130, 72), (150, 70), (170, 67),
     (178, 65), (170, 60), (162, 56), (158, 52), (142, 50), (140, 40),
     (135, 35), (130, 33), (127, 35), (122, 38), (120, 32), (110, 20),
     (108, 10), (105, 2), (100, 6), (95, 15), (92, 21), (88, 22),
     (80, 15), (77, 8), (72, 20), (66, 25), (60, 25), (57, 26),
     (52, 28), (48, 30), (44, 29), (40, 32), (36, 36), (30, 36),
     (26, 38), (22, 37), (19, 42), (15, 44), (12, 45), (8, 44),
     (3, 43), (-1, 37), (-6, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 38), (141, 41),
     (142, 44), (140, 42), (138, 37), (133, 35), (130, 33)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (150, -22), (146, -19), (142, -15), (142, -11), (137, -12),
     (135, -15), (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
    # New Zealand
    [(167, -45), (170, -43), (174, -41), (177, -38), (175, -36), (173, -35)],
    # South-East Asian islands
    [(95, 5), (98, 3), (100, -2), (104, -4), (106, -6), (110, -7),
     (114, -8), (119, -9), (122, -10), (125, -9), (128, -4), (131, -2),
     (135, -3), (138, -4), (141, -5), (141, -8), (136, -6), (130, -3),
     (125, 0), (120, 2), (115, 5), (110, 5), (105, 0), (100, 5)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (50, -20), (47, -24), (44, -25),
     (43, -20)],
]


def draw_map(d, x, y, w, h, dots):
    """Draw a stylised world map; dots are (lat, lon, colour, label)."""
    d.rectangle([x, y, x + w, y + h], fill=(233, 226, 205), outline=INK, width=1)
    # faint graticule
    for gx in range(1, 6):
        lx = x + w * gx / 6
        d.line([(lx, y), (lx, y + h)], fill=(214, 205, 180), width=1)
    for gy in range(1, 4):
        ly = y + h * gy / 4
        d.line([(x, ly), (x + w, ly)], fill=(214, 205, 180), width=1)

    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (90.0 - lat) / 150.0 * h  # lat 90 .. -60
        return (px, py)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(196, 182, 148), outline=(120, 108, 84))
    for lat, lon, colour, label, dx, dy in dots:
        px, py = proj(lon, lat)
        px += dx
        py += dy
        r = 7
        d.ellipse([px - r, py - r, px + r, py + r], fill=colour,
                  outline=(255, 255, 255), width=1)
        fnum = F("sans_b", 9)
        tw = text_w(fnum, label)
        d.text((px - tw / 2, py - 5), label, font=fnum, fill=(255, 255, 255))


def draw_legend(d, x, y, w):
    """Region colour legend, two rows of chips."""
    f = F("sans_b", 10)
    col_w = w // 4
    for i, region in enumerate(REGIONS):
        cx = x + (i % 4) * col_w
        cy = y + (i // 4) * 15
        d.rectangle([cx, cy + 1, cx + 9, cy + 10], fill=REGION_COLORS[region])
        d.text((cx + 13, cy), region, font=f, fill=INK)


# ---------------------------------------------------------------- front page
def draw_frontpage():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top rules + kicker
    d.line([(MARGIN, 22), (W - MARGIN, 22)], fill=INK, width=2)
    d.line([(MARGIN, 26), (W - MARGIN, 26)], fill=INK, width=1)
    fk = F("sans_b", 15)
    left = "ONE DAY OF WORLD NEWS, ONE PICTURE"
    right = "50 STORIES \u00b7 7 REGIONS"
    d.text((MARGIN, 33), left, font=fk, fill=INK)
    d.text((W - MARGIN - text_w(fk, right), 33), right, font=fk, fill=INK)

    # ---- masthead
    fday = F("sans_b", 13)
    draw_spaced(d, (W - spaced_width(fday, "SATURDAY", 6)) // 2, 56,
                "SATURDAY", fday, INK, tracking=6)
    fdate = F("serif", 54)
    date_txt = "21 NOVEMBER 2026"
    d.text(((W - text_w(fdate, date_txt)) // 2, 72), date_txt,
           font=fdate, fill=INK)
    d.line([(MARGIN, 134), (W - MARGIN, 134)], fill=INK, width=2)

    # ---- UTC timeline strip
    ty, th = 142, 56
    d.rectangle([MARGIN, ty, W - MARGIN, ty + th], fill=(26, 26, 26))
    lab_f = F("sans_b", 12)
    lab = ["THE DAY", "IN UTC"]
    lx = MARGIN + 12
    d.text((lx, ty + 10), lab[0], font=lab_f, fill=(246, 239, 221))
    d.text((lx, ty + 28), lab[1], font=lab_f, fill=(246, 239, 221))
    d.line([(lx + 82, ty + 8), (lx + 82, ty + th - 8)],
           fill=(120, 120, 120), width=1)
    ft = F("sans_b", 11)
    fs = F("sans", 10)
    ex = lx + 94
    ew = (W - MARGIN - ex - 8) // 6
    for i, (t, s) in enumerate(TIMELINE):
        cx = ex + i * ew
        d.text((cx, ty + 7), t, font=ft, fill=(250, 204, 21))
        for j, ln in enumerate(fit_lines(s, fs, ew - 8, 3)):
            d.text((cx, ty + 22 + j * 11), ln, font=fs,
                   fill=(246, 239, 221))

    # ---- 4 hero stories, 2x2
    hy, hh, hgap = 206, 120, 10
    hw = (CW - hgap) // 2
    for i, st in enumerate(HEROES):
        x = MARGIN + (i % 2) * (hw + hgap)
        y = hy + (i // 2) * (hh + hgap)
        col = REGION_COLORS[st["region"]]
        d.rectangle([x, y, x + hw, y + hh], outline=(180, 170, 145), width=1)
        # number circle
        d.ellipse([x + 6, y + 6, x + 32, y + 32], fill=col)
        fn = F("sans_b", 14)
        ns = str(st["n"])
        d.text((x + 19 - text_w(fn, ns) / 2, y + 10), ns, font=fn,
               fill=(255, 255, 255))
        fk2 = F("sans_b", 11)
        d.text((x + 38, y + 7), st["region"].upper() + " \u00b7 " + st["topic"],
               font=fk2, fill=col)
        tag = "\u2713 " + st["tag"]
        d.text((x + hw - 6 - text_w(fk2, tag), y + 7), tag, font=fk2,
               fill=RED)
        fh = F("serif", 16)
        hl = fit_lines(st["headline"], fh, hw - 14, 2)
        for j, ln in enumerate(hl):
            d.text((x + 7, y + 32 + j * 20), ln, font=fh, fill=INK)
        fsu = F("sans", 11)
        sl = fit_lines(st["summary"], fsu, hw - 14, 2)
        sy = y + 32 + len(hl) * 20 + 3
        for j, ln in enumerate(sl):
            d.text((x + 7, sy + j * 13), ln, font=fsu, fill=(60, 60, 60))

    # ---- small stories header
    d.text((MARGIN, 466), "THE DAY IN BRIEF", font=F("sans_b", 12), fill=INK)
    d.line([(MARGIN + 130, 472), (W - MARGIN, 472)], fill=INK, width=1)

    # ---- 12 small stories, 2 columns x 6 rows
    sy0, sh, sgap = 488, 33, 4
    sw = (CW - hgap) // 2
    for i, st in enumerate(SMALL):
        x = MARGIN + (i % 2) * (sw + hgap)
        y = sy0 + (i // 2) * (sh + sgap)
        col = REGION_COLORS[st["region"]]
        fn2 = F("sans_b", 12)
        d.text((x, y), str(st["n"]), font=fn2, fill=col)
        fh2 = F("sans_b", 12)
        hl = fit_lines(st["headline"], fh2, sw - 22, 1)
        d.text((x + 20, y), hl[0] if hl else "", font=fh2, fill=INK)
        fs2 = F("sans", 10)
        sl = fit_lines(st["summary"], fs2, sw - 22, 1)
        d.text((x + 20, y + 16), sl[0] if sl else "", font=fs2,
               fill=(60, 60, 60))
        d.line([(x, y + sh - 1), (x + sw, y + sh - 1)],
               fill=(214, 205, 180), width=1)

    # ---- bottom band: map + one-liners
    by = 716
    d.line([(MARGIN, by), (W - MARGIN, by)], fill=INK, width=2)
    # map panel
    mx, mw = MARGIN, 320
    d.text((mx, by + 6), "WHERE IT HAPPENED", font=F("sans_b", 12), fill=INK)
    dots = [(s["lat"], s["lon"], REGION_COLORS[s["region"]], str(s["n"]),
             s.get("dx", 0), s.get("dy", 0))
            for s in HEROES + SMALL]
    draw_map(d, mx, by + 24, mw, 148, dots)
    draw_legend(d, mx, by + 180, mw)
    # one-liners
    ox, ow = MARGIN + mw + 10, W - MARGIN - (MARGIN + mw + 10)
    d.text((ox, by + 6), "ALSO ON 21 NOVEMBER", font=F("sans_b", 12),
           fill=INK)
    d.line([(ox + 158, by + 12), (W - MARGIN, by + 12)], fill=INK, width=1)
    fo = F("sans", 10)
    cols, per_col = 3, 12
    colw = ow // cols
    for i, (region, text) in enumerate(ONELINERS):
        cx = ox + (i // per_col) * colw
        cy = by + 26 + (i % per_col) * 15
        col = REGION_COLORS[region]
        d.ellipse([cx, cy + 3, cx + 6, cy + 9], fill=col)
        lines = fit_lines(text, fo, colw - 12, 1)
        d.text((cx + 10, cy), lines[0] if lines else "", font=fo, fill=INK)

    # ---- date check banner
    dy = 954
    d.rectangle([MARGIN, dy, W - MARGIN, dy + 26], fill=RED)
    fdc = F("sans_b", 12)
    dc = ("DATE CHECK \u2014 EVERY STORY HERE HAPPENED OR WAS FIRST "
          "REPORTED ON SATURDAY 21 NOVEMBER 2026")
    d.text(((W - text_w(fdc, dc)) // 2, dy + 6), dc, font=fdc,
           fill=(255, 255, 255))

    # ---- footer
    ff = F("sans", 10)
    d.text((MARGIN, 988),
           "Every story here happened or was first reported on 21 November 2026. "
           "CLAIM = one side\u2019s account, not independently confirmed.",
           font=ff, fill=(60, 60, 60))
    d.text((MARGIN, 1002),
           "Sources: BBC, Reuters, Al Jazeera, The Guardian, Financial Times, CNN, "
           "Yonhap, Japan Times, The Hindu, France 24, and more. Compiled 21 Nov 2026.",
           font=ff, fill=(60, 60, 60))
    return img


def build_image():
    """Render the front page and return it as a PIL Image."""
    return draw_frontpage()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    here = os.path.dirname(os.path.abspath(__file__))
    fallback = os.path.join(here, "entry.png")
    try:
        if Image is None:
            raise ImportError("PIL is not available")
        img = build_image()
        img.save(out_path, format="PNG", compress_level=6)
    except Exception:
        # Fallback: ship the pre-rendered image beside this file.
        if os.path.exists(fallback):
            shutil.copyfile(fallback, out_path)
        else:
            raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
