# Windows version: save all layout screenshots into ONE folder (no timestamp subfolder)

import os
import traceback
from datetime import datetime
from paraview.simple import *

IMG_EXT = "png"
LAYOUT_RES = [1512, 753]
TRANSPARENT_BG = 0

# ----------------------------
# CONFIG (Windows paths)
# ----------------------------
# Option 1 (recommended): set a fixed output folder on your Windows drive
OUT_DIR = r"R:\PROJECTS\Sharkninja\Nano_Main\_Runs\RUN21_NanoMain_HD1000_CSFinal_noBaffle_RotatedHeater240_32CFM_1400W\pp\_paraview_screenshots"

# Option 2: if you prefer output next to your loaded file, leave OUT_DIR=None
# OUT_DIR = None

def mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def sanitize_filename(name):
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "_")
    return name.replace(" ", "_").strip("_").strip()

def get_case_directory_windows():
    """
    Try to detect directory from any source FileName; fallback to cwd.
    This is only used if OUT_DIR is None.
    """
    for src in GetSources().values():
        if hasattr(src, "FileName"):
            fname = src.FileName
            if isinstance(fname, (list, tuple)) and fname:
                return os.path.dirname(fname[0])
            if isinstance(fname, str) and fname:
                return os.path.dirname(fname)
    return os.getcwd()

def get_layout_proxies():
    L = GetLayouts()

    # ParaView 5.10 often returns dict {id: proxy}
    if isinstance(L, dict):
        # sort keys for stable naming
        try:
            return [L[k] for k in sorted(L.keys(), key=lambda x: str(x))]
        except:
            return list(L.values())

    # list/tuple fallback
    if isinstance(L, (list, tuple)):
        proxies = []
        for item in L:
            # sometimes item is (id, proxy)
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                proxies.append(item[1])
            else:
                proxies.append(item)
        return proxies

    # final fallback
    try:
        return list(L)
    except:
        return []

# ----------------------------
# Output folder (single level)
# ----------------------------
if OUT_DIR is None:
    case_dir = get_case_directory_windows()
    OUT_DIR = os.path.join(case_dir, "_paraview_screenshots")

mkdir(OUT_DIR)

print("Output folder :", OUT_DIR)
print("Writable?     :", os.access(OUT_DIR, os.W_OK))

# ----------------------------
# Layouts
# ----------------------------
layout_proxies = get_layout_proxies()
print("Raw GetLayouts():", type(GetLayouts()))
print("Found layout proxies:", len(layout_proxies))

if not layout_proxies:
    raise RuntimeError("No layouts found. Make sure you have at least one layout open.")

# Sometimes saving needs a render first
try:
    RenderAllViews()
except:
    pass

saved_count = 0

for i, lproxy in enumerate(layout_proxies, start=1):
    layout_name = sanitize_filename("Layout{0:02d}".format(i))
    out_png = os.path.join(OUT_DIR, "{0}_FULL.{1}".format(layout_name, IMG_EXT))

    print("Saving ->", out_png)
    try:
        SaveScreenshot(
            out_png,
            layout=lproxy,
            SaveAllViews=1,
            ImageResolution=list(LAYOUT_RES),
            TransparentBackground=TRANSPARENT_BG
        )

        if os.path.isfile(out_png):
            saved_count += 1
            print("OK:", out_png)
        else:
            print("WARNING: SaveScreenshot returned but file not found:", out_png)

    except Exception as e:
        print("ERROR saving", layout_name, ":", e)
        traceback.print_exc()

print("DONE. Saved files:", saved_count, "in", OUT_DIR)
