"""Read-only PE inspection of selected reflected functions; no execution or patching."""
from pathlib import Path
import bisect
import json
import re
import struct

import capstone
import pefile

ROOT = Path(__file__).resolve().parents[1] / "artifacts/wandering-sword-local-study"
EXE = Path(r"D:\Y 逸jian风yun决 v1.23.26 全DLC xg器\WanderingSword\Wandering_Sword\Binaries\Win64\JH-Win64-Shipping.exe")
binary = EXE.read_bytes()
pe = pefile.PE(data=binary, fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
text = next(s for s in pe.sections if s.Name.startswith(b".text"))
code_start = base + text.VirtualAddress
code_end = code_start + text.Misc_VirtualSize
data = next(s for s in pe.sections if s.Name.startswith(b".rdata"))
pdata = next(s for s in pe.sections if s.Name.startswith(b".pdata"))
functions = [struct.unpack_from("<III", binary, o) for o in range(pdata.PointerToRawData, pdata.PointerToRawData + pdata.SizeOfRawData - 11, 12)]
functions = sorted(t for t in functions if t[0] and t[1] > t[0])
starts = [f[0] for f in functions]
decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)


def function(va):
    index = bisect.bisect_right(starts, va - base) - 1
    if index < 0:
        return None
    a, b, unwind = functions[index]
    return (base + a, base + b) if a <= va - base < b else None


def disassemble(va):
    bounds = function(va) or (va, va + 128)
    start, end = bounds
    offset = pe.get_offset_from_rva(start - base)
    return [(i.address, i.mnemonic, i.op_str) for i in decoder.disasm(binary[offset:offset + end - start], start)]


def reflected(name):
    needle = name.encode() + b"\0"
    result = []
    for m in re.finditer(re.escape(needle), binary):
        if m.start() and binary[m.start() - 1] not in [0]:
            continue
        address = base + pe.get_rva_from_offset(m.start())
        for x in re.finditer(re.escape(struct.pack("<Q", address)), binary):
            following = struct.unpack_from("<Q", binary, x.start() + 8)[0]
            if code_start <= following < code_end:
                result.append({"name": name, "table_offset": x.start(), "function_va": following,
                               "instructions": disassemble(following)})
    return result


if __name__ == "__main__":
    result = []
    for name in ["LockX", "LockY", "LockZ", "UnLockX", "UnLockY", "UnLockZ", "MoveCameraboom"]:
        items = reflected(name)
        result.extend(items)
        print(name, [(hex(i["function_va"]), len(i["instructions"])) for i in items])
    (ROOT / "native-reflected-camera-functions.json").write_text(json.dumps(result, indent=2), encoding="utf8")
