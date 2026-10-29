# -*- coding: utf-8 -*-
"""HTML → PNG 长图（Chrome headless + PIL 自动裁底）"""
import os, subprocess, tempfile
from pathlib import Path
from PIL import Image
import numpy as np

BASE = Path(__file__).resolve().parent
HTML = BASE / "10月28号-全天-韭菜指数.html"
PNG = BASE / "10月28号-全天-韭菜指数-长图.png"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SCALE = 1.5
WIDTH = 1200
HEIGHT = 16000

raw = Path(tempfile.gettempdir()) / "jiucai_render_raw.png"
if raw.exists():
    raw.unlink()

cmd = [
    CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
    f"--force-device-scale-factor={SCALE}", f"--window-size={WIDTH},{HEIGHT}",
    f"--screenshot={raw}", HTML.as_uri(),
]
subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=180)

im = Image.open(raw).convert("RGB")
a = np.array(im)
bg = np.array([247, 244, 236])
mask = np.any(np.abs(a.astype(int) - bg) > 3, axis=2)
rows = np.where(mask.any(axis=1))[0]
bottom = min(im.height, int(rows.max()) + 25)
im.crop((0, 0, im.width, bottom)).save(PNG, optimize=True)
print(f"saved: {PNG}")
print(f"size: {im.width}x{bottom}px ({bottom/SCALE:.0f} CSS px)")
