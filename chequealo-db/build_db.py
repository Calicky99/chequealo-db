#!/usr/bin/env python3
"""Genera la base local de Chequealo a partir de MalwareBazaar y URLhaus (abuse.ch).

Uso:
  ABUSECH_AUTH_KEY=... python3 build_db.py          # descarga y genera data/
  python3 build_db.py --seed                         # solo la semilla de prueba (EICAR), sin red

Salida en data/:
  hashes.bin  huellas SHA-256 recortadas a 16 bytes, ordenadas y sin repetir
  urls.txt    enlaces peligrosos en línea, normalizados (minúsculas, sin esquema)
  hosts.txt   dominios peligrosos
  meta.json   versión y conteos
"""
import json, os, sys, time, urllib.request
from pathlib import Path

OUT = Path(__file__).parent / "data"
EICAR_SHA256 = "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"

SOURCES = {
    "hashes": "https://bazaar.abuse.ch/export/txt/sha256/recent/",
    "urls": "https://urlhaus.abuse.ch/downloads/text_online/",
    "hosts": "https://urlhaus.abuse.ch/downloads/hostfile/",
}
MAX_HASHES = 400_000
MAX_URLS = 200_000


def fetch(url, key):
    req = urllib.request.Request(url, headers={"Auth-Key": key, "User-Agent": "chequealo-db/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", "replace").splitlines()


def clean(lines):
    for l in lines:
        l = l.strip()
        if l and not l.startswith("#"):
            yield l


def norm_url(u):
    u = u.strip().lower().split("#")[0]
    for p in ("https://", "http://"):
        if u.startswith(p):
            u = u[len(p):]
    return u.rstrip("/")


def write(hashes, urls, hosts):
    OUT.mkdir(exist_ok=True)
    recs = sorted({bytes.fromhex(h)[:16] for h in hashes if len(h) == 64})
    (OUT / "hashes.bin").write_bytes(b"".join(recs))
    (OUT / "urls.txt").write_text("\n".join(sorted(urls)) + ("\n" if urls else ""))
    (OUT / "hosts.txt").write_text("\n".join(sorted(hosts)) + ("\n" if hosts else ""))
    meta = {"version": time.strftime("%Y%m%d%H%M", time.gmtime()), "hashes": len(recs), "urls": len(urls), "hosts": len(hosts)}
    (OUT / "meta.json").write_text(json.dumps(meta))
    print(meta)


def main():
    if "--seed" in sys.argv:
        write([EICAR_SHA256], set(), set())
        return
    key = os.environ.get("ABUSECH_AUTH_KEY", "").strip()
    if not key:
        sys.exit("Falta la variable ABUSECH_AUTH_KEY.")
    hashes = [h.lower() for h in clean(fetch(SOURCES["hashes"], key))][:MAX_HASHES]
    urls = {norm_url(u) for u in clean(fetch(SOURCES["urls"], key))}
    urls = set(list(urls)[:MAX_URLS])
    hosts = set()
    for l in clean(fetch(SOURCES["hosts"], key)):
        parts = l.split()
        host = parts[-1].lower()  # formato "127.0.0.1 dominio"
        if "." in host:
            hosts.add(host)
    hashes.append(EICAR_SHA256)  # para poder probar la app con el archivo EICAR
    if len(hashes) < 100:
        sys.exit("Descarga sospechosamente pequeña; no se actualiza.")
    write(hashes, urls, hosts)


if __name__ == "__main__":
    main()
