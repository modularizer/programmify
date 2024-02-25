import argparse
from pathlib import Path


def png_to_ico(png_path: str, ico_path: str = None, size: int = 64):
    png_path = str(Path(png_path).resolve())
    if ico_path is None:
        # replace .png with .ico
        ico_path = png_path[:-4] + ".ico"
    from PIL import Image
    img = Image.open(png_path)
    img.save(ico_path, sizes=[(size, size)])
    print(f"Wrote {size}x{size} icon to {ico_path}")
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


if __name__ == "__main__":
    png2ico()
