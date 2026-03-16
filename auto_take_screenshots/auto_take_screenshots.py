import os
import sys
from paraview.simple import GetParaViewVersion, GetParaViewSourceVersion

SCRIPT_MAP = {
    (5, 6): "auto_take_screenshots_pv562.py",
    (5, 10): "auto_take_screenshots_pv5101.py",
}


def get_candidate_script_dirs():
    dirs = []

    appdata = os.environ.get("APPDATA")
    if appdata:
        dirs.append(os.path.join(appdata, "ParaView", "Macros"))

    home = os.path.expanduser("~")
    dirs.append(os.path.join(home, "AppData", "Roaming", "ParaView", "Macros"))
    dirs.append(os.path.join(home, ".config", "ParaView", "Macros"))

    if "__file__" in globals():
        dirs.append(os.path.dirname(os.path.abspath(__file__)))

    dirs.append(os.getcwd())

    out = []
    seen = set()
    for d in dirs:
        if d and d not in seen:
            out.append(d)
            seen.add(d)
    return out


def find_script(script_name):
    for folder in get_candidate_script_dirs():
        script_path = os.path.join(folder, script_name)
        if os.path.isfile(script_path):
            return script_path
    raise RuntimeError(
        "Script not found: {0}\nSearched in:\n- {1}".format(
            script_name,
            "\n- ".join(get_candidate_script_dirs())
        )
    )


def get_paraview_version():
    v = GetParaViewVersion()
    return (int(v.major), int(v.minor))


def get_target_script(version_tuple):
    major, minor = version_tuple

    if (major, minor) in SCRIPT_MAP:
        return SCRIPT_MAP[(major, minor)]

    raise RuntimeError(
        "Unsupported ParaView version: {0}.{1}".format(major, minor)
    )


def run_script(script_path):
    namespace = {
        "__name__": "__main__",
        "__file__": script_path,
    }

    if sys.version_info[0] < 3:
        execfile(script_path, namespace, namespace)
    else:
        with open(script_path, "rb") as f:
            code = compile(f.read(), script_path, "exec")
        exec(code, namespace, namespace)


def main():
    version = get_paraview_version()
    script_name = get_target_script(version)
    script_path = find_script(script_name)

    print("Detected ParaView version :", "{0}.{1}".format(*version))
    print("Source version string     :", GetParaViewSourceVersion())
    print("Loading screenshot script :", script_path)

    run_script(script_path)


main()
