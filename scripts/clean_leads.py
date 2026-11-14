#!/usr/bin/env python3
"""Clean, de-duplicate and score a B2B lead list (CSV in, CSV out).

- Normalises Pakistani phone numbers to E.164 (+92...), websites to bare domains, emails to lowercase.
- Merges duplicates that share a phone, a domain, or a very similar name in the same city.
- Scores each lead 0-100 by how reachable it is (verified email > website > phone > address).

Usage:
    python clean_leads.py leads.csv -o clean.csv [--min-score 40]

Expected columns (others are kept): name, city, phone, email, website, address, source
Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from difflib import SequenceMatcher

EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
FREE_MAIL = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "live.com"}
NAME_NOISE = re.compile(r"\b(the|pvt|private|ltd|limited|school|system|hospital|clinic|campus|branch)\b|[^\w\s]")


def normalize_phone(raw: str) -> str:
    """Pakistani numbers → +92XXXXXXXXXX. Returns '' when it can't be a valid number."""
    digits = re.sub(r"\D", "", raw or "")
    if digits.startswith("0092"):
        digits = digits[4:]
    elif digits.startswith("92"):
        digits = digits[2:]
    elif digits.startswith("0"):
        digits = digits[1:]
    # mobiles: 3XXXXXXXXX (10 digits); landlines: area code + number (9-10 digits)
    if len(digits) == 10 and digits.startswith("3") or 9 <= len(digits) <= 10 and not digits.startswith("3"):
        return "+92" + digits
    return ""


def normalize_domain(raw: str) -> str:
    d = (raw or "").strip().lower()
    d = re.sub(r"^https?://", "", d)
    d = d.split("/")[0].split("?")[0]
    d = re.sub(r"^www\.", "", d)
    return d if "." in d and " " not in d else ""


def normalize_email(raw: str) -> str:
    e = (raw or "").strip().lower()
    return e if EMAIL.match(e) else ""


def name_key(name: str) -> str:
    return " ".join(NAME_NOISE.sub(" ", (name or "").lower()).split())


def score(lead: dict) -> int:
    s = 0
    if lead["email"]:
        domain = lead["email"].split("@")[1]
        s += 40 if domain not in FREE_MAIL else 25
        if lead["website"] and domain == lead["website"]:
            s += 10  # email matches the organisation's own domain
    if lead["website"]:
        s += 20
    if lead["phone"]:
        s += 20 if lead["phone"].startswith("+923") else 15  # mobiles reach decision makers faster
    if lead.get("address"):
        s += 10
    return min(s, 100)


def is_duplicate(a: dict, b: dict) -> bool:
    if a["phone"] and a["phone"] == b["phone"]:
        return True
    if a["website"] and a["website"] == b["website"]:
        return True
    same_city = (a.get("city") or "").strip().lower() == (b.get("city") or "").strip().lower()
    ka, kb = name_key(a.get("name", "")), name_key(b.get("name", ""))
    return bool(same_city and ka and kb and SequenceMatcher(None, ka, kb).ratio() >= 0.9)


def merge(a: dict, b: dict) -> dict:
    """Keep a's values, fill blanks from b, remember both sources."""
    out = dict(a)
    for k, v in b.items():
        if not out.get(k) and v:
            out[k] = v
    sources = {s for s in (a.get("source", ""), b.get("source", "")) if s}
    out["source"] = "; ".join(sorted(sources))
    return out


def clean(rows: list[dict]) -> list[dict]:
    leads: list[dict] = []
    for r in rows:
        lead = dict(r)
        lead["name"] = " ".join((r.get("name") or "").split())
        lead["phone"] = normalize_phone(r.get("phone", ""))
        lead["email"] = normalize_email(r.get("email", ""))
        lead["website"] = normalize_domain(r.get("website", ""))
        if not lead["name"]:
            continue
        for i, existing in enumerate(leads):
            if is_duplicate(existing, lead):
                leads[i] = merge(existing, lead)
                break
        else:
            leads.append(lead)
    for lead in leads:
        lead["score"] = score(lead)
    return sorted(leads, key=lambda l: -l["score"])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="-")
    ap.add_argument("--min-score", type=int, default=0)
    args = ap.parse_args(argv)
    with open(args.input, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    leads = [l for l in clean(rows) if l["score"] >= args.min_score]
    fields = list(dict.fromkeys([*(rows[0].keys() if rows else []), "score"]))
    out = sys.stdout if args.output == "-" else open(args.output, "w", newline="", encoding="utf-8")
    w = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(leads)
    if out is not sys.stdout:
        out.close()
    print(f"{len(rows)} rows in → {len(leads)} leads out", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
