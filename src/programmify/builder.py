# not really recommended because pyinstaller makes everything look like a virus
import argparse
import sys
from pathlib import Path

import yaml

from programmify.detect import detect_main_file, detect_icon
from programmify.png2ico import png_to_ico
from programmify.autoargparser import autoargparser

cfg_file = Path(__file__).parent / "programmify.cfg"
default_mode = "window"
default_name = None
default_icon = detect_icon()

@autoargparser
def build(file: str = None,
           name: str = default_name,
           dst: str = None,
           version: str = None,
           icon: str = default_icon,
           mode: str = default_mode,
           args: list = None,
           cmd: list = None,
           hidden_imports: list = None,
           extra_files: list = None,
           windowed: bool = True,
           cleanup: bool = True,
           show_cmd: bool = False,
           desktop: bool = False
           ):
    """Build a program from a python file.

    Args:
        file (str, optional): The file to build. If not specified, will try to detect the file to use.
        name (str, optional): The name of the program. Defaults to the class name.
        dst (str, optional): The destination directory for the built program. Defaults to the current working directory.
        version (str, optional): The version string to add to the end of the program name. e.g. "1" => "my_program v1"
        icon (str, optional): The path to the icon file. Defaults to attempting to detect the icon in the working directory.
        mode (str, optional): The mode of the program. Defaults to "window".
        args (list, optional): Additional arguments to pass to pyinstaller.
        cmd (list, optional): Expert level: command to run instead of pyinstaller.
        hidden_imports (list, optional): Hidden imports.
        extra_files (list, optional): Extra files to include.
        windowed (bool, optional): Whether to run in windowed mode. Defaults to True.
        cleanup (bool, optional): Whether to cleanup build files. Defaults to True.
        show_cmd (bool, optional): Whether to show the command that will be run instead of running it. Defaults to False.
        desktop (bool, optional): Whether to copy the file to the desktop. Defaults to False.
    """
    print(f"Building {file} as {name} with icon {icon}")
    if file is None:
        file = detect_main_file()
    if file in [".", "__file__"]:
        file = __file__
    if name is None:
        name = Path(file).stem
        if name in ["__main__", "main"]:
            name = Path(file).parent.name
    if version:
        name = f"{name} v{version}"

    if dst is None:
        dst = Path.cwd() / f"{name}.exe"
    dst = Path(dst).expanduser()

    if isinstance(hidden_imports, str):
        hidden_imports = [v.strip() for v in hidden_imports.replace(" ", ",").split(",")]
    if isinstance(extra_files, str):
        extra_files = [v.strip() for v in extra_files.replace(" ", ",").split(",")]

    if icon.endswith(".png"):
        icon = png_to_ico(icon)

    # make a temporary config
    with open(cfg_file, "w") as f:
        print("dumping", {"name": name, "mode": mode})
        f.write(yaml.dump({"name": name, "mode": mode}))
    print(f"dumped to {cfg_file}: {cfg_file.read_text()}")
    if cmd is None:
        cmd = ["pyinstaller", "--onefile", "--windowed",
               "--distpath", str(dst.parent.resolve()),
               f"--icon={icon}",
               "--add-data", f"{__file__};.",
               "--hidden-import", "setproctitle",
               "--hidden-import", "yaml"]
        if not windowed:
            cmd.remove("--windowed")
        for fn in Path(__file__).parent.glob("*"):
            cmd.extend(["--add-data", f"{fn};programmify"])

        for extra_file in extra_files or []:
            cmd.extend(["--add-data", f"{extra_file};."])
        for hidden_import in hidden_imports or []:
            cmd.extend(["--hidden-import", hidden_import])
        cmd.append(file)
    if args:
        cmd.extend(args)
    src = dst.parent / f"{Path(file).stem}.exe"
    return _build_from_cmd(cmd, src, dst, cleanup=cleanup, show_cmd=show_cmd, desktop=desktop)


def _build_from_cmd(cmd: list,
                    src,
                    dst,
                    cleanup: bool = True,
                    show_cmd: bool = False,
                    desktop: bool = False
                    ):
    if isinstance(cmd, str):
        cmd = [v.strip() for v in cmd.split(" ") if v.strip()]
    if show_cmd:
        print(" ".join(cmd))
        return cmd
    import shutil
    import subprocess

    # preclean
    if cleanup and Path("build").exists():
        raise Exception(
            "Build directory exists. Please remove it before building or use flag --nocleanup. Trying to avoid deleting files that you may want to keep.")

    # verify the name is not already a valid command
    if shutil.which(dst.stem) and not dst.exists():
        RED = "\033[91m"
        BOLD = "\033[1m"
        RESET = "\033[0m"
        print(f"{RED}{BOLD}{dst.stem}{RESET}{RED} is already a valid command. Please choose a different name{RESET}.")
        sys.exit(1)

    # build
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        RED = "\033[91m"
        BOLD = "\033[1m"
        RESET = "\033[0m"
        print(f"{RED}{BOLD}Failed to build {dst}{RESET}{RED}. Please check the error message above ^{RESET}.")
        sys.exit(1)

    print(f"Built {dst}")
    shutil.move(src, dst)
    if desktop:
        # copy the file to the desktop
        shutil.copy(dst, Path.home() / "Desktop" / dst.name)

    # cleanup
    if cleanup:
        shutil.rmtree("dist", ignore_errors=True)
        shutil.rmtree("build", ignore_errors=True)
        # remove all .spec files
        spec_file = f"{Path(src.stem)}.spec"
        if Path(spec_file).exists():
            Path(spec_file).unlink()
        if cfg_file.exists():
            cfg_file.unlink()

    print(f"Built {dst}")

    GRAY = "\033[90m"
    RESET = "\033[0m"

    print(f"""Built {dst}

To run the program:
    a. Open your File Explorer and double-click the file {dst}
    b. Open a command prompt and run the command `{GRAY}{dst}{RESET}
    c. In the command prompt if you are in the same directory as the file, you can run `{GRAY}{dst.stem}{RESET}`
""")


if __name__ == '__main__':
    build()
