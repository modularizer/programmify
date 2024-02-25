from pathlib import Path


programmify_icon = Path(__file__).parent / "favicon.ico"


def detect_icon(folder=Path.cwd(), default_icon=programmify_icon) -> str:
    """Detect the default icon for the folder (uses current working directory by default)."""
    folder = Path(folder).expanduser()
    # if there is a favicon.ico file in the current directory, use it
    if (folder / "favicon.ico").exists():
        icon = str((folder / "favicon.ico").resolve())
    else:
        # if there is exactly one .ico file in the current directory, use it
        ico_files = list(folder.glob("*.ico"))
        if len(ico_files) == 1:
            icon = str(ico_files[0].resolve())
        else:
            # if there is only one .png file in the current directory, convert it to .ico and use it
            png_files = list(folder.glob("*.png"))
            if len(png_files) == 1:
                try:
                    from programmify.png2ico import png_to_ico
                    icon = png_to_ico(png_files[0])
                except Exception as e:
                    print(f"Failed to convert {png_files[0]} to .ico: {e}")
            else:
                # if there is no .ico file in the current directory, use the default icon
                icon = None
    return icon or str(Path(default_icon).resolve())


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


if __name__ == "__main__":
    print(detect_main_file())