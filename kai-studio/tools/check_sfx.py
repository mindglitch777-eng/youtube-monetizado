#!/usr/bin/env python3
"""
Revisa public/sfx y escribe public/sfx/manifest.json (qué sonidos existen).
Sonidos esperados (mp3): whoosh, impact, thud, riser, notification, music.
Además exige sfx/LICENCIAS.md con fuente y licencia de cada uno.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SFX = ROOT / "public" / "sfx"
EXPECTED = ["whoosh", "impact", "thud", "riser", "notification", "music"]

SFX.mkdir(parents=True, exist_ok=True)
found = sorted(p.name for p in SFX.iterdir() if p.suffix.lower() in (".mp3",))
names = {Path(f).stem for f in found}
(SFX / "manifest.json").write_text(json.dumps({"files": found}, indent=1), encoding="utf-8")

for n in EXPECTED:
    print(("OK      " if n in names else "FALTA   ") + f"{n}.mp3")
extra = sorted(names - set(EXPECTED))
if extra:
    print("extra (no se usan solos):", ", ".join(extra))
lic = SFX / "LICENCIAS.md"
if not lic.exists():
    print("\nFALTA public/sfx/LICENCIAS.md  ->  anotá fuente y licencia de cada sonido (solo uso comercial libre).")
sys.exit(0)
