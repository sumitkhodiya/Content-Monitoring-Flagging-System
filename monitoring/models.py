"""
Data models for the content monitoring system.

Models:
- Keyword: Represents a keyword or phrase to monitor
- ContentItem: Represents content from an external source
- Flag: Represents a match between a keyword and content item with review status
"""

from django.db import models


class Keyword(models.Model):
    """
    Model to store keywords that the system should monitor for.
    """
    name = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ContentItem(models.Model):
    """
    Model to store content items imported from external sources.
    Tracks the last_updated timestamp to detect when content has changed.
    """
    title = models.CharField(max_length=500)
    body = models.TextField()
    source = models.CharField(max_length=100)  # e.g., 'newsapi', 'rss', 'mock'
    last_updated = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # External identifier to prevent duplicate imports  
    external_id = models.CharField(max_length=500, unique=True, db_index=True, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Flag(models.Model):
    """
    Model to represent the match between a keyword and a content item.
    
    Tracks:
    - The keyword and content item that matched
    - The match score (deterministic based on matching logic)
    - Review status (pending, relevant, irrelevant)
    - When the flag was created and reviewed
    - Last content version timestamp when irrelevant was set (for suppression)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('relevant', 'Relevant'),
        ('irrelevant', 'Irrelevant'),
    ]

    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name='flags')
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE, related_name='flags')
    score = models.IntegerField()  # 0-100
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Suppression logic: Track the content's last_updated when irrelevant was marked
    # If content changes after this timestamp, flag can resurface
    irrelevant_at_content_version = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('keyword', 'content_item')
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['status', '-score']),
            models.Index(fields=['keyword', 'status']),
        ]

    def __str__(self):
        return f"{self.keyword.name} -> {self.content_item.title} ({self.status})"
