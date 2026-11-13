"""Author a seamless wave-slope texture (image only; no scene geometry)."""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'assets/water'
out.mkdir(exist_ok=True)
size = 512
rng = np.random.default_rng(4281)
freq = np.fft.fftfreq(size) * size
kx, ky = np.meshgrid(freq, freq)
radius = np.sqrt(kx*kx + ky*ky)
# A continuous, broad spectrum avoids parallel bands and repeated wave crests.
envelope = np.exp(-0.5 * ((radius - 12.0) / 6.0)**2)
envelope *= 0.7 + 0.3 * np.abs(kx) / np.maximum(radius, 1)
envelope[radius < 3] = 0
spectrum = np.fft.fft2(rng.normal(size=(size, size))) * envelope
dx = np.fft.ifft2(spectrum * (1j*kx)).real
dy = np.fft.ifft2(spectrum * (1j*ky)).real
scale = max(dx.std(), dy.std()) * 3.7
encoded = np.stack([dx/scale, dy/scale, np.ones_like(dx)], axis=-1)
encoded = np.clip(encoded * 0.5 + 0.5, 0, 1)
Image.fromarray(np.round(encoded*255).astype('uint8')).save(out/'coastal_wave_slopes.png')
print('Saved original seamless coastal wave slope texture')
