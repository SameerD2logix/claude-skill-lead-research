import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from clean_leads import clean, normalize_domain, normalize_email, normalize_phone  # noqa: E402

RAW = Path(__file__).resolve().parents[1] / "examples" / "raw-leads.csv"


def test_phone_normalisation():
    assert normalize_phone("0300-1234567") == "+923001234567"
    assert normalize_phone("+92 300 1234567") == "+923001234567"
    assert normalize_phone("0092 21 35550000") == "+922135550000"
    assert normalize_phone("021-35550000") == "+922135550000"
    assert normalize_phone("12345") == ""


def test_domain_and_email():
    assert normalize_domain("https://www.Example.pk/contact?x=1") == "example.pk"
    assert normalize_domain("not a site") == ""
    assert normalize_email(" Info@Example.PK ") == "info@example.pk"
    assert normalize_email("not-an-email") == ""


def test_example_file_merges_duplicates_and_scores():
    rows = list(csv.DictReader(RAW.open(encoding="utf-8")))
    leads = clean(rows)
    names = [l["name"] for l in leads]
    assert len(leads) == 3, names  # 5 rows: 2 school duplicates + 2 hospital duplicates
    school = next(l for l in leads if "Bright" in l["name"])
    assert school["source"] == "maps; website"
    assert school["score"] == 100  # domain email matching website + website + mobile + address
    clinic = next(l for l in leads if "Sunrise" in l["name"])
    assert clinic["score"] == 0
