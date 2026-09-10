import importlib.util, re, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path

V = "0.7.3"

def run(c):
    print("+", " ".join(c))
    subprocess.run(c, check=True)

run([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", "setuptools", "wheel"])
if importlib.util.find_spec("numpy") is None:
    run([sys.executable, "-m", "pip", "install", "numpy==1.26.4"])

tmp = Path(tempfile.mkdtemp())
try:
    run([sys.executable, "-m", "pip", "download", f"insightface=={V}",
         "--no-deps", "--no-binary", "insightface", "-d", str(tmp)])
    tgz = next(tmp.glob("*.tar.gz"))
    with tarfile.open(tgz) as tf:
        tf.extractall(tmp)
    root = next(p for p in tmp.iterdir() if p.is_dir() and p.name.startswith("insightface-"))

    sp = root / "setup.py"
    src = sp.read_text()
    src = src.replace("from distutils.core import Extension", "")
    src = src.replace("from Cython.Distutils import build_ext", "")
    src = src.replace("from Cython.Build import cythonize", "")
    src = re.sub(r"extensions\s*=\s*\[.*?\n\s*\]", "extensions = []", src, flags=re.S)
    src = re.sub(r"ext_modules\s*=\s*cythonize\(extensions\)", "ext_modules = []", src)
    src = re.sub(r"\n\s*headers\s*=.*?,", "\n", src)
    sp.write_text(src)

    (root / "insightface" / "app" / "__init__.py").write_text(
        "from .face_analysis import *\n")

    run([sys.executable, "-m", "pip", "install", "--no-deps",
         "--no-build-isolation", str(root)])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

run([sys.executable, "-c", "import insightface; print('insightface', insightface.__version__, 'OK')"])
print("DONE")