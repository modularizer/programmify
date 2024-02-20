import argparse
import sys
from pathlib import Path
import setproctitle

import yaml
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow

cfg_file = Path(__file__).parent / "programmify.cfg"
default_mode = "window"
default_name = None


def png_to_ico(png_path: str, ico_path: str = None, size: int = 64):
    png_path = str(Path(png_path).resolve())
    if ico_path is None:
        # replace .png with .ico
        ico_path = png_path[:-4] + ".ico"
    from PIL import Image
    img = Image.open(png_path)
    img.save(ico_path, sizes=[(size, size)])
    return ico_path


def png2ico():
    """Command line utility to convert a .png file to a .ico file. Example usage:
        $: png2ico favicon.png
        $: png2ico favicon.png --size 32
        $: png2ico favicon.png --ico_path favicon.ico --size 32
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("png_path", help="Path to the .png file")
    parser.add_argument("--ico_path", help="Path to the .ico file")
    parser.add_argument("--size", type=int, default=64, help="Icon size")
    args = parser.parse_args()
    png_to_ico(args.png_path, args.ico_path, args.size)

# try to automatically find the default icon
programmify_icon = Path(__file__).parent / "favicon.ico"
default_icon = None


def detect_icon(folder=Path.cwd()):
    """Detect the default icon for the folder (uses current working directory by default)."""
    folder = Path(folder).expanduser()
    # if there is a favicon.ico file in the current directory, use it
    if (folder / "favicon.ico").exists():
        default_icon = str((folder / "favicon.ico").resolve())
    else:
        # if there is exactly one .ico file in the current directory, use it
        ico_files = list(folder.glob("*.ico"))
        if len(ico_files) == 1:
            default_icon = str(ico_files[0].resolve())
        else:
            # if there is only one .png file in the current directory, convert it to .ico and use it
            png_files = list(folder.glob("*.png"))
            if len(png_files) == 1:
                try:
                    default_icon = png_to_ico(png_files[0])
                except Exception as e:
                    print(f"Failed to convert {png_files[0]} to .ico: {e}")
            else:
                # if there is no .ico file in the current directory, use the default icon
                default_icon = None
    return default_icon


default_icon = detect_icon()

if default_icon is None:
    default_icon = detect_icon(Path(__file__).parent)
if default_icon is None:
    default_icon = str(programmify_icon.resolve())


if cfg_file.exists():
    with open(cfg_file) as f:
        cfg = yaml.safe_load(f)
        default_mode = cfg.get("mode", default_mode)
        default_name = cfg.get("name", default_name)
        default_icon = cfg.get("icon", default_icon)


def detect_main_file(folder=Path.cwd()):
    """Detect the main file to use for building the program."""
    folder = Path(folder).expanduser()
    # if there is only one .py file in the current directory, use it
    py_files = list(folder.glob("*.py"))
    py_files = [f for f in py_files if f.name != "__init__.py"]
    if len(py_files) == 1:
        return str(py_files[0].resolve())
    for test_path in ["main.py", "__main__.py", f"{folder.name}.py"]:
        if (folder / test_path).exists():
            return str((folder / test_path).resolve())
    if (folder / "src").exists():
        if (folder / "src").glob("*.py"):
            return detect_main_file(folder / "src")
        else:
            possible_src_files = []
            for f in (folder / "src").glob("*"):
                if not f.is_dir():
                    continue
                try:
                    main_file = detect_main_file(f)
                    if main_file:
                        possible_src_files.append(main_file)
                except FileNotFoundError:
                    pass
            if len(possible_src_files) == 1:
                return possible_src_files[0]
    raise FileNotFoundError("Could not detect main file. Please specify the file to build, e.g. programmify build my_program.py")


def build():
    # if the first argument does not start with a hyphen, try to detect file to use
    # try main.py, __main__.py, or if there is only one .py file in the current directory, use it
    if (len(sys.argv) <= 1) or sys.argv[1].startswith("-") and ("--help" not in sys.argv) and ("-h" not in sys.argv):
        file = detect_main_file()
        # insert the detected file as the first argument
        sys.argv.insert(1, file)

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="""File to build.
    If not specified, will try ...
        1. main.py in current working directory if found
        2. __main__.py
        3. the only .py file in the current working directory if only one is found (excluding __init__.py)
        4. if there is a src directory, will search in src and its subdirectories to find a single option
        5. if the above fails, will raise an error and you will need to specify the file to build.
    """)
    parser.add_argument("--name", default=default_name,
                        help="Program name. If not specified, the name of the either the file or its parent directory will be used.")
    parser.add_argument("--dst", help="Destination directory for the built program")
    parser.add_argument("--icon", default=default_icon,
                        help="Path to a 16x16 .ico file. If not specified, will try to find favicon.ico or any other .ico or .png in the current working directory.")
    parser.add_argument("--mode", default=default_mode, help="Program mode: window or widget")
    parser.add_argument("--nocleanup", action="store_false", help="Cleanup build files", dest="cleanup")
    parser.add_argument("--show_cmd", action="store_true", help="Show the command that will be run instead of running it")
    parser.add_argument("--cmd", help="Expert level: command to run instead of pyinstaller")
    parser.add_argument("--hidden_imports", nargs="*", help="Hidden imports")
    parser.add_argument("--extra-files", nargs="*", help="Extra files to include")
    parser.add_argument("--debug", action="store_false", help="Does not run in windowed mode, instead shows the terminal and stdout", dest="windowed")
    parser.add_argument("--args", nargs=argparse.REMAINDER, help="Additional arguments to pass to pyinstaller")
    parser.add_argument("--desktop", action="store_true", help="Copy the file to the desktop")
    parser.add_argument("--version", help="Adds the version string to the end of the program name. e.g. --version 1 => my_program v1")

    args = parser.parse_args()
    _build(file=args.file, name=args.name, dst=args.dst, version=args.version,
           icon=args.icon, mode=args.mode, cleanup=args.cleanup,
           hidden_imports=args.hidden_imports, extra_files=args.extra_files, windowed=args.windowed,
           cmd=args.cmd, args=args.args, desktop=args.desktop, show_cmd=args.show_cmd)


def _build(file: str = None,
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
    print(f"Building {file} as {name} with icon {icon}")
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
               f"--icon={icon}", "--add-data", f"{icon};programmify",
               "--add-data", f"{cfg_file};programmify",
               "--add-data", f"{str(Path(__file__).parent / "subprocess_program.py")};programmify",
               "--add-data", f"{__file__};.",
               "--hidden-import", "setproctitle",
               "--hidden-import", "yaml"]
        if not windowed:
            cmd.remove("--windowed")
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
        raise Exception("Build directory exists. Please remove it before building or use flag --nocleanup. Trying to avoid deleting files that you may want to keep.")

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


class Programmify:
    def __init__(self, name: str = default_name, icon: str = default_icon, **kwargs):
        if name is None:
            name = default_name
        if icon is None:
            icon = default_icon
        super().__init__(**kwargs)
        self.trayIcon = QtWidgets.QSystemTrayIcon(self)
        self.name = self.set_name(name)
        self.icon, self.trayIcon, self.icon_path = self.set_icon(icon)
        self.setupUI()

    png_to_ico = png_to_ico

    def setupUI(self):
        pass

    def set_icon(self, icon_path: str):
        if not icon_path:
            return None, None, None
        if not Path(icon_path).exists():
            raise FileNotFoundError(f"Icon file not found: {icon_path}")
        if icon_path.endswith(".png"):
            icon_path = self.png_to_ico(icon_path)
        self.icon_path = str(Path(icon_path).resolve())
        self.icon = QtGui.QIcon(self.icon_path)
        self.setWindowIcon(self.icon)
        self.trayIcon.setIcon(self.icon)
        self.trayIcon.setVisible(True)
        return self.icon, self.trayIcon, self.icon_path

    def set_name(self, title: str):
        self.name = title
        if title:
            self.setWindowTitle(title)
            if self.trayIcon:
                self.trayIcon.setToolTip(title)
            setproctitle.setproctitle(title)
        return self.name

    @classmethod
    def parse_args(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("--icon", default=default_icon, help="Icon file path")
        parser.add_argument("--name", default=default_name, help="Program name")
        args = parser.parse_args()
        kwargs = vars(args)
        return kwargs

    @classmethod
    def run(cls, **kw):
        kwargs = cls.parse_args()
        kwargs.update(kw)
        return cls._run(**kwargs)

    @classmethod
    def _run(cls, *args, **kwargs):
        print(f"Running {cls.__name__}")
        app = QtWidgets.QApplication(sys.argv)
        window = cls(*args, **kwargs)
        window.show()
        sys.exit(app.exec_())


class ProgrammifyWidget(Programmify, QtWidgets.QWidget):
    pass


class ProgrammifyMainWindow(Programmify, QMainWindow):
    def __init__(self, name: str = default_name, icon: str = default_icon, **kwargs):
        super().__init__(**kwargs)

        # Initialize your Programmify widget
        self.program_widget = ProgrammifyWidget(name=name, icon=icon)

        # Set the Programmify widget as the central widget of the QMainWindow
        self.setCentralWidget(self.program_widget)

        # Additional QMainWindow setup (like menus, toolbars, status bar, etc.) goes here
        self.setupUI()

    def setupUI(self):
        pass


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "build":
            sys.argv.pop(1)
            return build()
        elif "--build" in sys.argv:
            sys.argv.remove("--build")
            return build()
    if "--window" in sys.argv:
        sys.argv.remove("--window")
        return ProgrammifyMainWindow.run()
    elif "--widget" in sys.argv:
        sys.argv.remove("--widget")
        return ProgrammifyWidget.run()
    cls = ProgrammifyMainWindow if "--window" in sys.argv else ProgrammifyWidget
    return cls.run()


if __name__ == '__main__':
    main()
