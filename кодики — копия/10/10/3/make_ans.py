import math
from pathlib import Path

folder = Path(__file__).resolve().parent
lines = (folder / "task3.txt").read_text(encoding="utf-8").splitlines()

out = []
for line in lines:
    if not line.strip():
        continue
    a, b, c = map(int, line.split())
    value = a * math.sqrt(a) * c + c * c
    out.append(f"{value:.5f}".replace(".", ","))

(folder / "ans3.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))