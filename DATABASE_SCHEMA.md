# Database Schema & Field Reference

## Models Overview

### Keyword
Storage for monitored keywords/phrases.

| Field | Type | Properties |
|-------|------|-----------|
| id | BigAutoField | Primary key, auto-increment |
| name | CharField(255) | Unique, indexed, the keyword to match |
| created_at | DateTimeField | Auto-populated on creation |
| updated_at | DateTimeField | Auto-updated on any change |

**Constraints**: `UNIQUE(name)`, `INDEX(name)`
**Use**: Quick lookup of keywords for scanning

---

### ContentItem
All content imported from external sources.

| Field | Type | Properties |
|-------|------|-----------|
| id | BigAutoField | Primary key |
| title | CharField(500) | Article/content title |
| body | TextField | Full content body |
| source | CharField(100) | Origin: "mock", "newsapi", "rss", etc. |
| last_updated | DateTimeField | ← **Suppression key**: when content was last modified |
| created_at | DateTimeField | When imported into system |
| external_id | CharField(500) | Unique, indexed |

**Constraints**: `UNIQUE(external_id)`, `INDEX(external_id)`, `INDEX(created_at)`
**Use**: Duplicate prevention, content tracking, suppression logic

---

### Flag
Match between keyword and content with review status.

| Field | Type | Properties |
|-------|------|-----------|
| id | BigAutoField | Primary key |
| keyword | ForeignKey(Keyword) | Which keyword matched |
| content_item | ForeignKey(ContentItem) | Which content matched |
| score | IntegerField | Match score (0-100) |
| status | CharField(20) | pending, relevant, or irrelevant |
| created_at | DateTimeField | When flag was created |
| reviewed_at | DateTimeField | When reviewer acted (null if pending) |
| irrelevant_at_content_version | DateTimeField | ← **Suppression field**: content's last_updated when marked irrelevant |

**Constraints**:
- `UNIQUE(keyword, content_item)` - Only one flag per keyword+content pair
- `INDEX(status, score)` - For filtering/sorting pending flags
- `INDEX(keyword, status)` - For getting keyword's flags by status

**Workflow**:
1. Flag created with `status='pending'`, `reviewed_at=NULL`
2. Reviewer updates `status` → 'relevant' or 'irrelevant'
3. `reviewed_at` automatically set to current timestamp
4. If irrelevant: `irrelevant_at_content_version` = `content_item.last_updated`
5. On next scan: if `content_item.last_updated` hasn't changed → **suppress** (don't recreate)

---

## Sample Queries

### Get pending flags for a keyword
```sql
SELECT f.* 
FROM monitoring_flag f
JOIN monitoring_keyword k ON f.keyword_id = k.id
WHERE k.name = 'python' AND f.status = 'pending'
ORDER BY f.score DESC;
```

### Find flags that are suppressed due to status=irrelevant
```sql
SELECT f.*, c.last_updated
FROM monitoring_flag f
JOIN monitoring_contentitem c ON f.content_item_id = c.id
WHERE f.status = 'irrelevant'
  AND c.last_updated <= f.irrelevant_at_content_version;
```

### Find re-surfaceable flags (content changed after marked irrelevant)
```sql
SELECT f.*, c.last_updated
FROM monitoring_flag f
JOIN monitoring_contentitem c ON f.content_item_id = c.id
WHERE f.status = 'irrelevant'
  AND c.last_updated > f.irrelevant_at_content_version;
```

### Count matches by status
```sql
SELECT f.status, COUNT(*) as count
FROM monitoring_flag f
GROUP BY f.status;
```

---

## Django ORM Equivalents

### Create keyword
```python
Keyword.objects.create(name='python')
```

### Get or create keyword
```python
keyword, created = Keyword.objects.get_or_create(name='python')
```

### Upsert content item
```python
content, created = ContentItem.objects.update_or_create(
    external_id='newsapi_123',
    defaults={
        'title': 'News Title',
        'body': 'Content...',
        'source': 'newsapi',
        'last_updated': timezone.now(),
    }
)
```

### Create flag
```python
flag = Flag.objects.create(
    keyword=keyword,
    content_item=content,
    score=100,
    status='pending'
)
```

### Update flag status
```python
flag.status = 'irrelevant'
flag.reviewed_at = timezone.now()
flag.irrelevant_at_content_version = flag.content_item.last_updated
flag.save()
```

### Query pending flags with filters
```python
flags = Flag.objects\
    .select_related('keyword', 'content_item')\
    .filter(status='pending', score__gte=70)\
    .order_by('-score', '-created_at')
```

### Get suppression status
```python
def is_suppressed(flag):
    return (
        flag.status == 'irrelevant' and
        flag.irrelevant_at_content_version and
        flag.content_item.last_updated <= flag.irrelevant_at_content_version
    )
```

---

## Admin Interface

All models are registered in Django admin at `/admin/`:

- **Keywords**: View, create, edit, delete keywords
- **Content Items**: Browse imported content
- **Flags**: Review matches with visual status indicators

Admin setup:
```bash
python manage.py createsuperuser
python manage.py runserver
# Visit http://localhost:8000/admin/
```

---

## Performance Considerations

### Indexes
- `Keyword.name` - For fast keyword lookups
- `ContentItem.external_id` - For deduplication
- `Flag(status, score)` - For common filtering
- `Flag(keyword, status)` - For keyword-specific queries

### Select Related
When fetching flags, always use:
```python
Flag.objects.select_related('keyword', 'content_item')
```
This prevents N+1 queries when accessing related names.

### Pagination
Default 20 items/page. Use query params:
```
GET /api/flags/?page=2
```

---

## Migration Notes

Initial migration creates all tables. Schema is relatively stable because:
1. Field types chosen carefully
2. Relationships are well-founded
3. Constraints match business rules

If changes needed:
```bash
python manage.py makemigrations monitoring
python manage.py migrate
```

---

## Data Cleanup

### Reset everything
```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_keywords
```

### Delete old flags
```bash
python manage.py shell
>>> from monitoring.models import Flag
>>> Flag.objects.filter(created_at__lt='2026-03-20').delete()
```

### Reset a keyword's flags
```bash
>>> from monitoring.models import Keyword, Flag
>>> keyword = Keyword.objects.get(name='python')
>>> keyword.flags.all().delete()
```
