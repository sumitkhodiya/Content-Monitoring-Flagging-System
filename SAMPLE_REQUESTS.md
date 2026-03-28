# Content Monitoring System - Sample API Requests

This file contains copy-paste ready curl commands to test the API.

## Prerequisites

- Server running: `python manage.py runserver`
- Keywords seeded: `python manage.py seed_keywords`
- Base URL: http://localhost:8000/api/

## 1. Create Additional Keywords

```bash
curl -X POST http://localhost:8000/api/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"name": "kubernetes"}'

curl -X POST http://localhost:8000/api/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"name": "cloud computing"}'

curl -X POST http://localhost:8000/api/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"name": "react"}'
```

## 2. List All Keywords

```bash
curl http://localhost:8000/api/keywords/
```

## 3. Search Keywords by Name

```bash
curl "http://localhost:8000/api/keywords/?name=python"
```

## 4. Trigger a Content Scan

```bash
# Scan with mock data
curl -X POST http://localhost:8000/api/scan/ \
  -H "Content-Type: application/json" \
  -d '{"source": "mock"}'
```

## 5. List All Flags

```bash
curl http://localhost:8000/api/flags/
```

## 6. List Flags with Filters

```bash
# Only pending flags
curl "http://localhost:8000/api/flags/?status=pending"

# Only relevant flags
curl "http://localhost:8000/api/flags/?status=relevant"

# Only irrelevant flags
curl "http://localhost:8000/api/flags/?status=irrelevant"

# Flags with score >= 70
curl "http://localhost:8000/api/flags/?min_score=70"

# Flags for keyword_id=1 (python)
curl "http://localhost:8000/api/flags/?keyword_id=1"

# Combine filters
curl "http://localhost:8000/api/flags/?status=pending&min_score=70"
```

## 7. Get Pending Flags (Convenience Endpoint)

```bash
curl http://localhost:8000/api/flags/pending/
```

## 8. Get Flag Statistics

```bash
curl http://localhost:8000/api/flags/stats/
```

## 9. Review: Mark Flag as Relevant

Replace `{id}` with actual flag ID (e.g., 1)

```bash
curl -X PATCH http://localhost:8000/api/flags/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "relevant"}'
```

## 10. Review: Mark Flag as Irrelevant

```bash
curl -X PATCH http://localhost:8000/api/flags/2/ \
  -H "Content-Type: application/json" \
  -d '{"status": "irrelevant"}'
```

## 11. Get Specific Flag Details

```bash
curl http://localhost:8000/api/flags/1/
```

## Workflow Example

### Step 1: Start fresh
```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_keywords
python manage.py runserver
```

### Step 2: In another terminal, run scan
```bash
curl -X POST http://localhost:8000/api/scan/ \
  -H "Content-Type: application/json" \
  -d '{"source": "mock"}'
```

Expected output:
```json
{
  "success": true,
  "message": "Scan completed for source: mock",
  "stats": {
    "source": "mock",
    "content_items_processed": 6,
    "flags_created": 12,
    "flags_updated": 0,
    "flags_suppressed": 0
  }
}
```

### Step 3: View pending flags
```bash
curl http://localhost:8000/api/flags/?status=pending | python -m json.tool
```

### Step 4: Mark some as irrelevant
```bash
# Mark flag 1 as irrelevant
curl -X PATCH http://localhost:8000/api/flags/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "irrelevant"}'

# Mark flag 2 as relevant
curl -X PATCH http://localhost:8000/api/flags/2/ \
  -H "Content-Type: application/json" \
  -d '{"status": "relevant"}'
```

### Step 5: Run scan again (test suppression)
```bash
curl -X POST http://localhost:8000/api/scan/ \
  -H "Content-Type: application/json" \
  -d '{"source": "mock"}'
```

Expected:
- Flag 1 should be suppressed (not re-created since content unchanged)
- Stats should show `"flags_suppressed": 1` (or more)
- No new duplicate flags

### Step 6: Check flag statistics
```bash
curl http://localhost:8000/api/flags/stats/
```

Example:
```json
{
  "total_flags": 12,
  "by_status": {
    "pending": 9,
    "relevant": 1,
    "irrelevant": 2
  }
}
```

## Using Python/Requests (Alternative to curl)

If you prefer Python requests:

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# 1. Create a keyword
response = requests.post(
    f"{BASE_URL}/keywords/",
    json={"name": "fastapi"}
)
print(response.json())

# 2. Run a scan
response = requests.post(
    f"{BASE_URL}/scan/",
    json={"source": "mock"}
)
print(json.dumps(response.json(), indent=2))

# 3. Get pending flags
response = requests.get(f"{BASE_URL}/flags/?status=pending")
flags = response.json()
print(f"Found {len(flags)} pending flags")

# 4. Mark first flag as relevant
if flags:
    flag_id = flags[0]['id']
    response = requests.patch(
        f"{BASE_URL}/flags/{flag_id}/",
        json={"status": "relevant"}
    )
    print(f"Updated flag {flag_id}: {response.json()['status']}")
```

## Notes

- Replace `localhost:8000` with your server address if deployed
- Use `python -m json.tool` to pretty-print JSON: `curl ... | python -m json.tool`
- Flag IDs start at 1 and increment per flag created
- Keyword IDs depend on seed order; use `/api/keywords/` to see all IDs
- All times are returned in ISO 8601 format (UTC)
