#!/usr/bin/env python3
"""
Organizador de imágenes de Kai.

Flujo:
  1) Tirá TODAS las imágenes bajadas de Flow en  inbox/  (cualquier nombre).
  2) python tools/organize_images.py love-bombing
        -> arma inbox/order.txt (propuesta de orden) y out/contact_sheet_XX.jpg (número + línea de voz de cada imagen)
        -> te avisa si faltan/sobran imágenes, si hay duplicadas o si alguna no es vertical 9:16
  3) Mirá las hojas. Si alguna está fuera de lugar, editá inbox/order.txt (mové las líneas) y repetí el paso 2.
  4) python tools/organize_images.py love-bombing --apply
        -> copia (sin borrar originales) a public/episodes/love-bombing/images/kai-p1-01.png ... y guarda mapping.json

Otros:
  python tools/organize_images.py love-bombing --check     # revisa la carpeta final: qué números faltan
  --by name|mtime      orden inicial (por defecto mtime = orden en que las bajaste)
  --missing-ok         permite aplicar aunque falten imágenes (las que faltan quedan vacías)
Requiere: pip install pillow
"""
import argparse, hashlib, json, re, shutil, sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def natural_key(p: Path):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def load_expected(slug: str):
    for lang in ("en", "es"):
        path = ROOT / "episodes" / slug / lang / "script.json"
        if path.exists():
            script = json.loads(path.read_text(encoding="utf-8"))
            break
    else:
        raise FileNotFoundError(f"No encontré script.json (ni en/ ni es/) para {slug} en {ROOT / 'episodes' / slug}")
    per_image = {}  # n -> (line id, text)
    for line in script["lines"]:
        for im in line["images"]:
            per_image[im["n"]] = (line["id"], line["text"])
    return script, per_image


def ahash(img: Image.Image) -> int:
    g = img.convert("L").resize((8, 8))
    px = list(g.tobytes())
    avg = sum(px) / 64
    return sum(1 << i for i, v in enumerate(px) if v > avg)


def ham(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def font(size):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            pass
    return ImageFont.load_default()


def contact_sheets(order, per_image, out_dir: Path, per_page=12, cols=4):
    out_dir.mkdir(parents=True, exist_ok=True)
    cw, ch = 270, 480
    cap = 70
    for old in out_dir.glob("contact_sheet_*.jpg"):
        old.unlink()
    pages = []
    for p0 in range(0, len(order), per_page):
        chunk = order[p0:p0 + per_page]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cw * cols, (ch + cap) * rows), (20, 20, 28))
        d = ImageDraw.Draw(sheet)
        for k, path in enumerate(chunk):
            n = p0 + k + 1
            x, y = (k % cols) * cw, (k // cols) * (ch + cap)
            try:
                im = Image.open(path).convert("RGB")
                im.thumbnail((cw - 6, ch - 6))
                sheet.paste(im, (x + 3, y + 3))
            except Exception:
                d.text((x + 10, y + 10), "no se pudo abrir", fill=(255, 80, 80), font=font(18))
            d.rectangle([x + 3, y + 3, x + 64, y + 40], fill=(0, 0, 0))
            d.text((x + 10, y + 8), f"{n:02d}", fill=(255, 210, 60), font=font(26))
            lid, text = per_image.get(n, (0, "(imagen de más: no hay línea para este número)"))
            wrapped = textwrap.wrap(f"L{lid}: {text}", 33)
            if len(wrapped) > 3:
                wrapped = wrapped[:3]
                wrapped[-1] = wrapped[-1][:30] + "…"
            for li, row in enumerate(wrapped):
                d.text((x + 6, y + ch + 3 + li * 16), row, fill=(235, 235, 235), font=font(13))
        name = out_dir / f"contact_sheet_{p0 // per_page + 1:02d}.jpg"
        sheet.save(name, quality=82)
        pages.append(name)
    return pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--inbox", default=str(ROOT / "inbox"))
    ap.add_argument("--by", choices=["mtime", "name"], default="mtime")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--missing-ok", action="store_true")
    ap.add_argument("--force", action="store_true", help="pisar imágenes ya existentes en public/")
    a = ap.parse_args()

    script, per_image = load_expected(a.slug)
    expected = script["imageCount"]
    prefix = script["imagePrefix"]
    final_dir = ROOT / "public" / "episodes" / a.slug / "images"
    final_dir.mkdir(parents=True, exist_ok=True)

    if a.check:
        have = {int(m.group(1)) for p in final_dir.glob(f"{prefix}*.png") if (m := re.match(rf"{re.escape(prefix)}(\d+)\.png$", p.name))}
        missing = [n for n in range(1, expected + 1) if n not in have]
        extra = sorted(n for n in have if n > expected)
        print(f"{len(have)} de {expected} imágenes en {final_dir}")
        for n in missing:
            print(f"  FALTA {prefix}{n:02d}.png   (línea {per_image[n][0]}: {per_image[n][1][:60]})")
        for n in extra:
            print(f"  SOBRA {prefix}{n:02d}.png")
        sys.exit(1 if missing else 0)

    inbox = Path(a.inbox)
    inbox.mkdir(exist_ok=True)
    files = [p for p in inbox.iterdir() if p.suffix.lower() in EXTS]
    if not files:
        print(f"No hay imágenes en {inbox}. Copiá ahí las de Flow y volvé a correr.")
        sys.exit(1)

    order_file = inbox / "order.txt"
    if order_file.exists():
        names = [l.split("#")[0].strip() for l in order_file.read_text(encoding="utf-8").splitlines()]
        names = [n for n in names if n]
        by_name = {p.name: p for p in files}
        order = [by_name[n] for n in names if n in by_name]
        unknown = [n for n in names if n not in by_name]
        new = [p for p in files if p.name not in set(names)]
        if unknown:
            print("Estos nombres de order.txt no existen en inbox/ (se ignoran):", ", ".join(unknown))
        if new:
            print("Imágenes nuevas en inbox/ que no estaban en order.txt (van al final):", ", ".join(p.name for p in new))
            order += sorted(new, key=natural_key)
        print(f"Usando el orden de {order_file.name} ({len(order)} imágenes)")
    else:
        order = sorted(files, key=(lambda p: p.stat().st_mtime) if a.by == "mtime" else natural_key)
        print(f"Orden inicial por {a.by} ({len(order)} imágenes)")

    # ---- checks ----
    problems = 0
    hashes = {}
    ahs = []
    for i, p in enumerate(order, 1):
        h = hashlib.sha1(p.read_bytes()).hexdigest()
        if h in hashes:
            print(f"  DUPLICADA exacta: {p.name} = {hashes[h]}  (posiciones {order.index(Path(inbox / hashes[h])) + 1} y {i})")
            problems += 1
        hashes[h] = p.name
        try:
            with Image.open(p) as im:
                w, hgt = im.size
                ahs.append((i, p.name, ahash(im)))
                if abs(w / hgt - 9 / 16) > 0.03:
                    print(f"  NO ES 9:16: {p.name} ({w}x{hgt})")
                    problems += 1
                elif w < 720:
                    print(f"  BAJA RESOLUCIÓN: {p.name} ({w}x{hgt})")
        except Exception as e:
            print(f"  NO SE PUEDE ABRIR: {p.name} ({e})")
            problems += 1
    for x in range(len(ahs)):
        for y in range(x + 1, len(ahs)):
            if ham(ahs[x][2], ahs[y][2]) <= 2 and hashlib.sha1(order[x].read_bytes()).hexdigest() != hashlib.sha1(order[y].read_bytes()).hexdigest():
                print(f"  MUY PARECIDAS: #{ahs[x][0]} {ahs[x][1]}  ~  #{ahs[y][0]} {ahs[y][1]}  (¿versión repetida?)")

    n = len(order)
    if n < expected:
        print(f"\nFALTAN {expected - n} imagen(es): hay {n} y el guion pide {expected}.")
        print("  No puedo saber cuáles faltan en el medio: mirá las hojas de contacto y fijate desde qué número")
        print("  la imagen deja de coincidir con su línea; ahí falta una. Las últimas líneas sin imagen serían:")
        for k in range(n + 1, expected + 1):
            print(f"    {k:02d}  (línea {per_image[k][0]}: {per_image[k][1][:60]})")
        problems += 1
    elif n > expected:
        print(f"\nSOBRAN {n - expected} imagen(es): hay {n} y el guion pide {expected}.")
        problems += 1
    else:
        print(f"\nCantidad correcta: {n} imágenes.")

    # ---- proposal + sheets ----
    lines = [f"{p.name}   # {i:02d}  L{per_image.get(i, (0, ''))[0]}: {per_image.get(i, (0, ''))[1][:50]}" for i, p in enumerate(order, 1)]
    order_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sheets = contact_sheets(order, per_image, ROOT / "out")
    print(f"Orden guardado en {order_file}")
    print("Hojas de contacto: " + ", ".join(str(s.relative_to(ROOT)) for s in sheets))

    if not a.apply:
        print("\nRevisá las hojas. Si está todo bien:  python tools/organize_images.py " + a.slug + " --apply")
        return

    if n != expected and not a.missing_ok:
        print("\nNo aplico: la cantidad no coincide. (Usá --missing-ok si querés aplicar igual.)")
        sys.exit(1)
    mapping = {}
    for i, p in enumerate(order[:expected], 1):
        dest = final_dir / f"{prefix}{i:02d}.png"
        if dest.exists() and not a.force:
            print(f"  ya existe {dest.name} (usá --force para pisarla)")
            continue
        with Image.open(p) as im:
            im.convert("RGB").save(dest, "PNG")
        mapping[f"{prefix}{i:02d}.png"] = p.name
    (final_dir / "mapping.json").write_text(json.dumps(mapping, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nListo: {len(mapping)} imágenes copiadas a {final_dir}")
    print("Verificá con:  python tools/organize_images.py " + a.slug + " --check")


if __name__ == "__main__":
    main()
