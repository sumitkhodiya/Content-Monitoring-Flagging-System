# Troubleshooting & FAQ

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: "django.db.utils.OperationalError: no such table"

**Solution**:
```bash
python manage.py migrate
python manage.py migrate monitoring
```

### Issue: "Port 8000 already in use"

**Solution**:
```bash
python manage.py runserver 0.0.0.0:8001
# Or kill existing process
# On Windows: taskkill /F /IM python.exe
```

### Issue: Flags keep duplicating on every scan

**Cause**: Unique constraint not working
**Check**:
```python
# In Django shell
python manage.py shell
>>> from monitoring.models import Flag
>>> Flag.objects.raw('SELECT * FROM monitoring_flag')  # Should show unique (keyword, content_item)
```

### Issue: Suppression not working (irrelevant flags are being recreated)

**Diagnosis**:
```bash
# Check flag with ID 1
curl http://localhost:8000/api/flags/1/

# Look for these fields:
# - status: should be "irrelevant"
# - reviewed_at: should not be null
# - (also check irrelevant_at_content_version via Django shell)
```

**Possible causes**:
1. `irrelevant_at_content_version` is NULL - content's `last_updated` wasn't saved
2. Content's `last_updated` was updated - this SHOULD cause re-surfacing (expected behavior)
3. New keyword matches - creates new flag, doesn't suppress old one

---

## FAQ

### Q: Why does the score go 100 → 70 → 40 with no in-between?
**A**: Scoring is deterministic and multi-level:
- First check title for exact word match → 100 (stops checking)
- Then check title for partial match → 70 (stops checking)
- Finally check body → 40

This prevents lower-scored matches from being repeated. You can modify `MatchingEngine.compute_score()` for different logic.

### Q: Can I have multiple keywords matching same content?
**A**: Yes! Each keyword creates its own flag. So if "python" AND "django" both match content, you get 2 separate flags with different scores.

### Q: What happens if I mark a flag as "relevant"?
**A**: 
- Status changes to "relevant"
- `reviewed_at` is set to current time
- `irrelevant_at_content_version` is cleared (set to NULL)
- On next scan: flag will NOT be recreated (because it already exists with unique constraint)

### Q: Can I delete a flag?
**A**: Yes, via API:
```bash
curl -X DELETE http://localhost:8000/api/flags/1/
```

But this is not recommended in normal workflow - use status updates instead.

### Q: How do I see ALL flags, not just pending?
**A**: Use filter param:
```bash
curl "http://localhost:8000/api/flags/?status=relevant"
curl "http://localhost:8000/api/flags/?status=irrelevant"
# Or no filter = all
curl http://localhost:8000/api/flags/
```

### Q: Can keywords have spaces?
**A**: Yes!
```bash
curl -X POST http://localhost:8000/api/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"name":"data pipeline"}'
```

Matching is case-insensitive and respects word boundaries.

### Q: What if two content items are identical?
**A**: Set different `external_id` and they'll be imported separately. If you want deduplication, compute a hash of (title+body) and use that as `external_id`.

### Q: How do I reset everything?
**A**:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_keywords
```

This wipes database and resets to initial state.

### Q: How do I change the matching logic?
**A**: Edit `monitoring/services.py` → `MatchingEngine.compute_score()`

Example: to add substring matching in title with score 80:
```python
if keyword_lower in title_lower:
    # Check if it's exact word match
    if MatchingEngine._is_exact_word_match(keyword_lower, title_lower):
        return 100
    # Otherwise partial match
    else:
        return 80  # Changed from 70
```

### Q: How do I change the scoring scale?
**A**: The is flexible. Currently:
- 100 = high confidence
- 70 = medium confidence  
- 40 = low confidence
- None = no match

You can use any scale you want. Adjust in `MatchingEngine`.

### Q: Can I integrate with real NewsAPI?
**A**: Yes, the placeholder exists in `services.py`:

```python
def _fetch_newsapi_data(self):
    import requests
    import os
    
    api_key = os.getenv('NEWSAPI_KEY')
    response = requests.get(
        'https://newsapi.org/v2/everything',
        params={
            'q': 'technology',
            'apiKey': api_key,
            'sortBy': 'publishedAt',
            'pageSize': 100,
        }
    )
    articles = response.json()['articles']
    
    # Transform to standard format
    results = []
    for article in articles:
        results.append({
            'title': article['title'],
            'body': article['description'] + ' ' + article['content'],
            'source': 'newsapi',
            'last_updated': article['publishedAt'],
            'external_id': article['url'],  # URL is unique
        })
    return results
```

Then install `requests`:
```bash
pip install requests
```

And scan with:
```bash
curl -X POST http://localhost:8000/api/scan/ \
  -H "Content-Type: application/json" \
  -d '{"source":"newsapi"}'
```

### Q: How do I prevent duplicate flags?
**A**: The database handles this automatically via `UNIQUE(keyword, content_item)` constraint. You can't create two flags for same keyword+content pair.

To avoid duplicate content items, use consistent `external_id` values.

### Q: What's the difference between `reviewed_at` and `created_at`?
**A**:
- `created_at`: When flag was auto-generated by scan
- `reviewed_at`: When a human marked it as relevant/irrelevant (null if still pending)

### Q: How do I export flags to CSV?
**A**: Use Django shell:
```bash
python manage.py shell
```

Then:
```python
import csv
from monitoring.models import Flag

with open('flags.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Keyword', 'Content', 'Score', 'Status'])
    
    for flag in Flag.objects.select_related('keyword', 'content_item'):
        writer.writerow([
            flag.id,
            flag.keyword.name,
            flag.content_item.title,
            flag.score,
            flag.status,
        ])
```

### Q: Can I run this in Docker?
**A**: Yes! Create `Dockerfile`:

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

Then:
```bash
docker build -t content-monitor .
docker run -p 8000:8000 content-monitor
```

### Q: How do I add authentication?
**A**: Use Django REST Framework's authentication classes in settings:

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```

Then:
```bash
python manage.py drf_create_token <username>
```

### Q: How do I add pagination?
**A**: Already configured! Default 20 items per page:

```bash
curl "http://localhost:8000/api/flags/?page=2&page_size=50"
```

To change default, edit `settings.py`:
```python
REST_FRAMEWORK = {
    'PAGE_SIZE': 50  # Changed from 20
}
```

### Q: Performance: what if I have millions of flags?
**A**: 
1. Add database indices (see DATABASE_SCHEMA.md)
2. Use pagination (already default)
3. Consider async scanning with Celery
4. Archive old flags to separate table
5. Use PostgreSQL instead of SQLite

---

## Debugging & Testing

### Enable Django Debug Toolbar
```bash
pip install django-debug-toolbar
# Add to INSTALLED_APPS in settings.py
# Visit http://localhost:8000/__debug__/
```

### Access Django Shell
```bash
python manage.py shell

# Test matching
from monitoring.services import MatchingEngine
from monitoring.models import ContentItem

content = ContentItem.objects.first()
score = MatchingEngine.compute_score('python', content)
print(f"Score: {score}")
```

### Raw SQL Queries
```bash
python manage.py shell

from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as queries:
    from monitoring.models import Flag
    Flag.objects.select_related('keyword', 'content_item').filter(status='pending')[:10]

for q in queries:
    print(q['sql'])
    print(f"Time: {q['time']}")
```

### Test Flag Creation Speed
```bash
from django.utils import timezone
from monitoring.models import Keyword, ContentItem, Flag
import time

keywords = Keyword.objects.all()[:10]
contents = ContentItem.objects.all()[:100]

start = time.time()
flags = [
    Flag(keyword=k, content_item=c, score=100, status='pending')
    for k in keywords for c in contents
]
Flag.objects.bulk_create(flags, ignore_conflicts=True)
elapsed = time.time() - start

print(f"Created {len(flags)} flags in {elapsed:.2f}s")
```

---

## Support Resources

- Django docs: https://docs.djangoproject.com/
- DRF docs: https://www.django-rest-framework.org/
- Python regex: https://docs.python.org/3/library/re.html
- SQLite docs: https://www.sqlite.org/docs.html

---

## Reporting Issues

When reporting issues, include:
1. Django version: `python -m django --version`
2. Python version: `python --version`
3. Error traceback (full output)
4. Steps to reproduce
5. What you expected vs. what happened

Example:
```bash
python manage.py runserver 2>&1 | tee error.log
# Share the error.log
```
