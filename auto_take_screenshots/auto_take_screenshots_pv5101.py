import os
import traceback
import ntpath
import posixpath

from paraview import servermanager
from paraview.simple import *

try:
    from paraview.modules.vtkRemotingCore import vtkPVSession
except ImportError:
    vtkPVSession = servermanager.vtkPVSession

try:
    from paraview.modules.vtkRemotingServerManager import vtkSMFileUtilities
    HAS_REMOTE_MKDIR = True
except ImportError:
    vtkSMFileUtilities = getattr(servermanager, "vtkSMFileUtilities", None)
    HAS_REMOTE_MKDIR = vtkSMFileUtilities is not None


IMG_EXT = "png"
LAYOUT_RES = [1512, 753]
TRANSPARENT_BG = 0

# Leave as None to auto-detect output folder from loaded .foam file
OUT_DIR = None


def sanitize_filename(name):
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "_")
    return name.replace(" ", "_").strip("_").strip()


def get_loaded_foam_file():
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


def get_path_module(path):
    if path and "/" in path and "\\" not in path:
        return posixpath
    return ntpath


def is_linux_remote_path(path):
    return isinstance(path, str) and path.startswith("/") and "\\" not in path


def get_save_location(path):
    if is_linux_remote_path(path):
        return vtkPVSession.DATA_SERVER
    return vtkPVSession.CLIENT


def mkdir_any(path):
    """
    Client-first behavior:
    - Windows path: always create locally
    - Linux path: create remotely only if ParaView exposes vtkSMFileUtilities
    """
    if is_linux_remote_path(path):
        if not HAS_REMOTE_MKDIR:
            print("WARNING: Remote mkdir is not available in this ParaView version.")
            print("WARNING: For ParaView 5.6.2, remote Linux output folders must already exist:")
            print("WARNING:", path)
            return

        session = servermanager.ActiveConnection.Session
        file_utils = vtkSMFileUtilities()
        file_utils.SetSession(session)

        ok = file_utils.MakeDirectory(path, vtkPVSession.DATA_SERVER_ROOT)
        if not ok:
            raise RuntimeError("Failed to create remote directory: {0}".format(path))

        print("Created remote directory:", path)
    else:
        if not os.path.isdir(path):
            os.makedirs(path)
            print("Created local directory :", path)


def save_screenshot_any(filename, view_or_layout, save_location, **params):
    """
    ParaView 5.6/5.10 compatible screenshot save.
    """
    controller = servermanager.ParaViewPipelineController()
    options = servermanager.misc.SaveScreenshot()
    controller.PreInitializeProxy(options)

    options.Layout = view_or_layout if view_or_layout.IsA("vtkSMViewLayoutProxy") else None
    options.View = view_or_layout if view_or_layout.IsA("vtkSMViewProxy") else None
    options.SaveAllViews = True if view_or_layout.IsA("vtkSMViewLayoutProxy") else False

    options.UpdateDefaultsAndVisibilities(filename)
    controller.PostInitializeProxy(options)

    params = dict(params)

    format_proxy = options.Format
    for prop in format_proxy.ListProperties():
        if prop in params:
            format_proxy.SetPropertyWithName(prop, params[prop])
            del params[prop]

    if "ImageQuality" in params:
        del params["ImageQuality"]

    SetProperties(options, **params)

    try:
        return options.WriteImage(filename, save_location)
    except TypeError:
        return options.WriteImage(filename)


def get_output_folder():
    foam_file = get_loaded_foam_file()

    if foam_file:
        pathmod = get_path_module(foam_file)
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


if OUT_DIR is None:
    OUT_DIR, foam_file = get_output_folder()
else:
    foam_file = get_loaded_foam_file()

pathmod = get_path_module(foam_file) if foam_file else os.path
save_location = get_save_location(OUT_DIR)

mkdir_any(OUT_DIR)

print("Loaded .foam file :", foam_file)
print("Output folder     :", OUT_DIR)
print("Save location     :", "DATA_SERVER" if save_location == vtkPVSession.DATA_SERVER else "CLIENT")
print("Remote mkdir      :", HAS_REMOTE_MKDIR)

layout_proxies = get_layout_proxies()
print("Found layout proxies:", len(layout_proxies))

if not layout_proxies:
    raise RuntimeError("No layouts found. Make sure you have at least one layout open.")

try:
    RenderAllViews()
except:
    pass

saved_count = 0

case_name = "case"
if foam_file:
    case_name = sanitize_filename(pathmod.splitext(pathmod.basename(foam_file))[0])

for i, lproxy in enumerate(layout_proxies, start=1):
    layout_name = get_layout_name_safe(lproxy, i)

    out_png = pathmod.join(
        OUT_DIR,
        "{}_{}_{:02d}.{}".format(case_name, layout_name, i, IMG_EXT)
    )

    print("Saving ->", out_png)
    try:
        ok = save_screenshot_any(
            out_png,
            lproxy,
            save_location,
            SaveAllViews=1,
            ImageResolution=list(LAYOUT_RES),
            TransparentBackground=TRANSPARENT_BG
        )

        if ok:
            print("OK:", out_png)
            saved_count += 1
        else:
            print("WARNING: WriteImage returned False:", out_png)

    except Exception as e:
        print("ERROR saving", layout_name, ":", e)
        traceback.print_exc()

print("DONE. Saved files:", saved_count, "in", OUT_DIR)
