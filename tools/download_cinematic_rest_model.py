"""Download and verify the specific Ref2VA Q4 model authorized for this shot."""
from pathlib import Path
import sys

RUNTIME = Path('D:/AI/minimax-h3-minimal')
sys.path.insert(0, str(RUNTIME))
from download_parallel import fetch_file

MODEL = {
    'target': 'ComfyUI_windows_portable/ComfyUI/models/unet/minimax_h3_ref2va_turbo_Q4_K_M.gguf',
    'url': 'https://huggingface.co/ChrisColeTech/minimax-h3-turbo-GGUF/resolve/490f6dca88bd4ee9aac76a0055e5ee5793a18237/split/diffusion_models/minimax_h3_ref2va_turbo_Q4_K_M.gguf',
    'bytes': 11388228576,
    'sha256': '587884205aa40732fe3c39fff93eaa0f2df82fd96d7304e98360b3dffa7af697',
}

if __name__ == '__main__':
    fetch_file(MODEL, workers=16)
