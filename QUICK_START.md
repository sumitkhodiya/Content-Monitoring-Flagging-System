# QUICK START - Setup & Run in 5 Minutes

## One-Time Setup

```bash
# 1. Navigate to project
cd content_monitor

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Create database and tables
python manage.py migrate

# 4. Seed default keywords
python manage.py seed_keywords
```

**Done!** You now have a working system with:
- ✅ 6 keywords: python, django, automation, data pipeline, machine learning, web development
- ✅ Empty flags table
- ✅ SQLite database

---

## Run the Server

```bash
python manage.py runserver
```

Server is now live at: **http://localhost:8000/api/**

---

## Test It (In Another Terminal)

### 1. Check keywords were created
```bash
curl http://localhost:8000/api/keywords/
```

### 2. Run a scan (creates flags)
```bash
curl -X POST http://localhost:8000/api/scan/ \
  -H "Content-Type: application/json" \
  -d '{"source":"mock"}'
```

Expected response:
```json
{
  "success": true,
  "stats": {
    "content_items_processed": 6,
    "flags_created": 7,
    "flags_suppressed": 0
  }
}
```

### 3. View pending flags
```bash
curl http://localhost:8000/api/flags/?status=pending
```

### 4. Mark one as irrelevant
```bash
curl -X PATCH http://localhost:8000/api/flags/1/ \
  -H "Content-Type: application/json" \
  -d '{"status":"irrelevant"}'
```

### 5. Scan again (verify suppression works)
```bash
curl -X POST http://localhost:8000/api/scan/ \
  -H "Content-Type: application/json" \
  -d '{"source":"mock"}'
```

Notice: `"flags_suppressed": 1` means the irrelevant flag wasn't recreated ✅

---

## Next Steps

Read these docs in order:
1. **README.md** - Full API documentation
2. **SAMPLE_REQUESTS.md** - Copy-paste curl commands
3. **DATABASE_SCHEMA.md** - Model structure
4. **TROUBLESHOOTING.md** - Common issues & FAQ
5. **IMPLEMENTATION_SUMMARY.md** - Architecture overview

---

## File Structure

```
content_monitor/
├── manage.py              # Django CLI
├── db.sqlite3             # Database (auto-created)
├── README.md              # Main documentation
├── QUICK_START.md         # This file
├── SAMPLE_REQUESTS.md     # API examples
├── DATABASE_SCHEMA.md     # Model reference
├── IMPLEMENTATION_SUMMARY.md # Architecture
├── TROUBLESHOOTING.md     # FAQ & issues
├── requirements.txt       # Dependencies
│
├── config/                # Django settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── monitoring/            # Main app
    ├── models.py          # Keyword, ContentItem, Flag
    ├── views.py           # API endpoints
    ├── serializers.py     # Data formatting
    ├── services.py        # Business logic ⭐
    ├── urls.py
    ├── admin.py
    ├── management/
    │   └── commands/
    │       ├── seed_keywords.py
    │       └── run_scan.py
    └── migrations/
```

---

## Common Commands

```bash
# Database
python manage.py migrate              # Apply migrations
python manage.py makemigrations       # Create migrations

# Management
python manage.py seed_keywords        # Add default keywords
python manage.py run_scan --source mock  # Scan via CLI

# Admin
python manage.py createsuperuser      # Create admin user
python manage.py runserver            # Start dev server

# Utility
python manage.py shell                # Django Python shell
python manage.py flush                # Delete all data (careful!)
```

---

## API Endpoints Cheat Sheet

```bash
# Keywords
POST   /api/keywords/               # Create
GET    /api/keywords/               # List

# Scanning
POST   /api/scan/                   # Trigger scan

# Flags
GET    /api/flags/                  # List (all)
GET    /api/flags/pending/          # List pending only
GET    /api/flags/stats/            # Statistics
PATCH  /api/flags/{id}/             # Update status
```

---

## Reset/Clean Restart

If something goes wrong:

```bash
# Delete database
rm db.sqlite3

# Recreate everything
python manage.py migrate
python manage.py seed_keywords

# Run server
python manage.py runserver
```

---

## What's Actually Happening

### Behind the Scenes of `/api/scan/`

```
1. Fetch content from source
   └─> Mock data: 6 articles

2. Get all keywords  
   └─> 6 keywords in DB

3. For each keyword + content pair:
   └─> Compute match score (100/70/40/None)
   └─> Create flag if score > 0

4. Apply suppression logic:
   └─> If flag.status == 'irrelevant':
       └─> If content unchanged → suppress (don't recreate)
       └─> If content changed → resurface (reset to pending)

5. Return statistics
```

### Key Field: `irrelevant_at_content_version`

When you mark a flag as irrelevant:
```python
flag.status = 'irrelevant'
flag.irrelevant_at_content_version = flag.content_item.last_updated
flag.reviewed_at = timezone.now()
flag.save()
```

On next scan, the suppression engine checks:
```python
if (flag.status == 'irrelevant' and 
    content_item.last_updated == flag.irrelevant_at_content_version):
    # Don't recreate the flag
    skip()
```

---

## Performance Tips

- First scan might take a moment (creates entries)
- Second scan is faster (updates only)
- Suppression reduces duplicate flags
- Queries are optimized with select_related()

---

## Next Integration Points

Once everything works locally:

1. **Real content source**: Edit `ContentFetcher._fetch_newsapi_data()`
2. **Async scans**: Add Celery task
3. **Web UI**: Add React/Vue frontend
4. **Authentication**: Add DRF TokenAuthentication
5. **Production**: Deploy to Heroku/AWS/etc

---

**You're ready to go!** 🚀

For questions, see TROUBLESHOOTING.md or check the full README.md
