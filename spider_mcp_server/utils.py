import os
from typing import Callable

def save(path: str, name: str, s: str | bytes | bytearray | None, call: Callable[[str], None]):
    print(f"save: {path}, {name}, {type(s).__name__}")

    if s is None:
        return

    file: str = os.path.join(path, name)
    if isinstance(s, str):
        with open(file, 'w', encoding='utf-8') as f:
            _ = f.write(s)
    else:
        with open(file, 'wb') as f:
            _ = f.write(s)
            
    call(file) 