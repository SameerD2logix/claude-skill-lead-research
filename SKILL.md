---
name: lead-research
description: Research B2B leads (schools, hospitals, clinics, businesses) from public sources, structure them into a clean CSV, de-duplicate, score by reachability, and draft a short personalised first message. Use when the user asks to find, research, clean or prioritise leads or prospects.
---

# Lead Research

## Ground rules

- Use **public business information only** (official websites, Google Maps listings, directories,
  company LinkedIn pages). No personal social profiles, no scraping behind logins.
- Never guess emails or phone numbers. Missing is better than wrong.
- Record a `source` for every lead so the user can verify it.
- Respect opt-outs: if a site says "no solicitation", mark the lead `do_not_contact`.

## Workflow

1. **Define the target** with the user: sector, city/region, size signals, and the offer.
2. **Collect** leads into CSV columns from `reference/schema.md`.
3. **Clean, merge and score:**
   ```bash
   python scripts/clean_leads.py raw.csv -o clean.csv --min-score 40
   ```
   This normalises Pakistani phones to `+92…`, websites to domains, drops invalid emails, merges
   duplicates (same phone, same domain, or ~same name in the same city) and scores 0–100.
4. **Research the top leads** (website "About", news, services) and add a one-line `hook`:
   something specific to them.
5. **Draft first messages** (≤ 80 words, one clear ask, no fake familiarity), using the hook.
6. Hand over `clean.csv` + the drafts. The user sends them; never send messages yourself.

## Score meaning

| Score | Meaning |
|---|---|
| 70–100 | Domain email + website + phone: ready for outreach |
| 40–69 | Reachable by phone or generic email |
| < 40 | Needs more research |
