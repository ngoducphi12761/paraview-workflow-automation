import os
import traceback
import ntpath
import posixpath
from paraview.simple import *

IMG_EXT = "png"
LAYOUT_RES = [1512, 753]
TRANSPARENT_BG = 0

# Leave as None to auto-detect output folder from loaded .foam file
OUT_DIR = None


def mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def sanitize_filename(name):
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "_")
    return name.replace(" ", "_").strip("_").strip()


def get_loaded_foam_file():
    """
    Find the loaded .foam file from ParaView sources.
    """
    for src in GetSources().values():
        if hasattr(src, "FileName"):
            fname = src.FileName

            if isinstance(fname, (list, tuple)) and fname:
                for f in fname:
                    if isinstance(f, str) and f.lower().endswith(".foam"):
                        return f

            elif isinstance(fname, str) and fname.lower().endswith(".foam"):
                return fname

    return None


# def get_output_folder():
#     """
#     Create output folder based on loaded .foam file location.
#     Example:
#     R:\...\RUN14_xxx_1400W.foam
#     -->
#     R:\...\pp\_paraview_screenshots
#     """
#     foam_file = get_loaded_foam_file()

#     if foam_file:
#         case_dir = os.path.dirname(foam_file)
#         out_dir = os.path.join(case_dir, "pp", "_paraview_screenshots")
#         return out_dir, foam_file

#     fallback_dir = os.path.join(os.getcwd(), "_paraview_screenshots")
#     return fallback_dir, None
def get_output_folder():
    """
    Create output folder based on loaded .foam file location.

    Windows example:
    R:\...\RUN14_xxx_1400W.foam
    ->
    R:\...\pp\_paraview_screenshots

    Linux example:
    /home/shared/.../RUN14_xxx_1400W.foam
    ->
    /home/shared/.../pp/_paraview_screenshots
    """
    foam_file = get_loaded_foam_file()

    if foam_file:
        # Detect which path module matches the loaded file path
        pathmod = posixpath if "/" in foam_file and "\\" not in foam_file else ntpath

        case_dir = pathmod.dirname(foam_file)
        out_dir = pathmod.join(case_dir, "pp", "_paraview_screenshots")
        return out_dir, foam_file

    fallback_dir = os.path.join(os.getcwd(), "_paraview_screenshots")
    return fallback_dir, None

def get_layout_proxies():
    L = GetLayouts()

    if isinstance(L, dict):
        try:
            return [L[k] for k in sorted(L.keys(), key=lambda x: str(x))]
        except:
            return list(L.values())

    if isinstance(L, (list, tuple)):
        proxies = []
        for item in L:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                proxies.append(item[1])
            else:
                proxies.append(item)
        return proxies

    try:
        return list(L)
    except:
        return []


def get_layout_name_safe(lproxy, idx):
    """
    Try to get the actual ParaView layout/tab name.
    """
    try:
        name = GetLayoutName(lproxy)
        if name:
            return sanitize_filename(name)
    except:
        pass

    try:
        name = lproxy.GetXMLLabel()
        if name:
            return sanitize_filename(name)
    except:
        pass

    return "Layout{0:02d}".format(idx)


# ----------------------------
# Auto output folder
# ----------------------------
if OUT_DIR is None:
    OUT_DIR, foam_file = get_output_folder()
else:
    foam_file = get_loaded_foam_file()

mkdir(OUT_DIR)

print("Loaded .foam file :", foam_file)
print("Output folder     :", OUT_DIR)
print("Writable?         :", os.access(OUT_DIR, os.W_OK))

# ----------------------------
# Layouts
# ----------------------------
layout_proxies = get_layout_proxies()
print("Found layout proxies:", len(layout_proxies))

if not layout_proxies:
    raise RuntimeError("No layouts found. Make sure you have at least one layout open.")

# Render before saving
try:
    RenderAllViews()
except:
    pass

saved_count = 0
used_names = set()

# Use case name from .foam file
case_name = "case"
if foam_file:
    case_name = sanitize_filename(os.path.splitext(os.path.basename(foam_file))[0])

for i, lproxy in enumerate(layout_proxies, start=1):
    layout_name = get_layout_name_safe(lproxy, i)

    out_png = os.path.join(
        OUT_DIR,
        "{}_{}_{:02d}.{}".format(case_name, layout_name, i, IMG_EXT)
    )

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
            print("WARNING: file not found after SaveScreenshot:", out_png)

    except Exception as e:
        print("ERROR saving", layout_name, ":", e)
        traceback.print_exc()

print("DONE. Saved files:", saved_count, "in", OUT_DIR)