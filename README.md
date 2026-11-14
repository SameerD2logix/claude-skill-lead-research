# Lead Research: a Claude Agent Skill

> Turn *"find private schools in Lahore for our software"* into a **clean, de-duplicated, scored lead list** plus personalised first messages, using public information only.

![skill](https://img.shields.io/badge/Claude-Agent%20Skill-D97757) ![python](https://img.shields.io/badge/python-3.10%2B-3776AB) ![license](https://img.shields.io/badge/license-MIT-green)

## Features

- **Research workflow** for Claude: target definition → collection → cleaning → research hooks → message drafts
- **`clean_leads.py`** (stdlib only):
  - Pakistani phone numbers → E.164 `+92…` (mobiles and landlines)
  - websites → bare domains; invalid emails dropped
  - duplicate merging by phone, domain or fuzzy name in the same city (keeps all sources)
  - **reachability score 0–100**
- Ethics built in: public business data only, no guessed contact details, opt-outs respected, user sends messages

## Example

```bash
$ python scripts/clean_leads.py examples/raw-leads.csv
5 rows in → 3 leads out
```
| name | phone | email | website | score |
|---|---|---|---|---|
| Bright Future School System | +923001234567 | info@brightfutureexample.pk | brightfutureexample.pk | 100 |
| Green Valley Hospital | +922135550000 | admin@gmail.com | greenvalleyexample.com | 70 |
| Sunrise Clinic | | | | 0 |

*(Example data is fictional.)*

## Install

```bash
git clone https://github.com/SameerD2logix/claude-skill-lead-research ~/.claude/skills/lead-research
```

## Tests

```bash
pip install pytest && pytest -q
```

## Author

**Sameer Hussain** · [LinkedIn](https://www.linkedin.com/in/sameer-hussain-87368a164) · [D2Logix](https://d2logix.com). AI-assisted lead generation for education and healthcare.
