#!/usr/bin/env python3
"""
Bootstrap builder for Wakawaka.
Produces a single standalone 'waka' binary using PyInstaller.

Usage:
    python build_waka.py

Output:
    dist/waka        (Linux/macOS)
    dist/waka.exe    (Windows)

After building, copy dist/waka (or dist/waka.exe) to a directory on
your PATH and use it directly:

    waka run hello.wk
    waka repl
    waka serve www/
"""
import os
import sys
import subprocess

DIST = os.path.join(os.path.dirname(__file__), "dist")


def check_pyinstaller():
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build():
    check_pyinstaller()

    root = os.path.dirname(os.path.abspath(__file__))
    entry = os.path.join(root, "waka.py")

    # Run PyInstaller with this interpreter, so the binary bundles the same
    # Python that runs this script (not whichever `pyinstaller` is on PATH).
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "waka",
        "--distpath", DIST,
        "--workpath", os.path.join(root, "build", "_pyinstaller"),
        "--specpath", os.path.join(root, "build"),
        # Include the src package
        "--add-data", f"{os.path.join(root, 'src')}{os.pathsep}src",
        # Include example files
        "--add-data", f"{os.path.join(root, 'examples')}{os.pathsep}examples",
        # C runtime used by `waka build` (waka.py looks for it next to itself)
        "--add-data", f"{os.path.join(root, 'runtime')}{os.pathsep}runtime",
        "--hidden-import", "src.lexer",
        "--hidden-import", "src.parser",
        "--hidden-import", "src.interpreter",
        "--hidden-import", "src.builtins",
        "--hidden-import", "src.ast_nodes",
        "--hidden-import", "src.web_server",
        "--hidden-import", "src.transpiler",
        "--hidden-import", "src.type_checker",
        "--hidden-import", "src.formatter",
        entry,
    ]

    print("Building waka binary...")
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=root)

    if result.returncode != 0:
        print("\n\033[31mBuild failed.\033[0m")
        sys.exit(1)

    binary = os.path.join(DIST, "waka.exe" if sys.platform == "win32" else "waka")
    print(f"\n\033[32mBuild successful: {binary}\033[0m")
    print("\nTo install system-wide:")
    if sys.platform == "win32":
        print(f"  copy {binary} to a directory in your PATH")
    else:
        print(f"  sudo cp {binary} /usr/local/bin/waka")
        print(f"  sudo chmod +x /usr/local/bin/waka")
    print("\nTest with:")
    print("  waka version")
    print("  waka run examples/hello.wk")


if __name__ == "__main__":
    build()
