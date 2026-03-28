"""
Services for content scanning, matching, and flagging logic.

This module contains the core business logic for:
1. Fetching content from sources
2. Computing match scores
3. Creating/updating flags with suppression logic
"""

import re
from datetime import datetime
from typing import List, Dict, Tuple
from django.utils import timezone
from django.db import transaction

from monitoring.models import Keyword, ContentItem, Flag


class ContentFetcher:
    """
    Handles fetching content from various sources.
    """
    
    @staticmethod
    def fetch_from_source(source: str) -> List[Dict]:
        """
        Fetch content items from the specified source.
        
        Args:
            source: 'mock' or 'newsapi'
            
        Returns:
            List of dicts with keys: title, body, source, last_updated, external_id
        """
        if source == 'mock':
            return ContentFetcher._fetch_mock_data()
        elif source == 'newsapi':
            return ContentFetcher._fetch_newsapi_data()
        else:
            raise ValueError(f"Unknown source: {source}")
    
    @staticmethod
    def _fetch_mock_data() -> List[Dict]:
        """
        Return mock content dataset.
        This is the fallback option when no external API is available.
        """
        return [
            {
                "title": "Learn Django Fast",
                "body": "Django is a powerful Python framework for building web applications quickly.",
                "source": "Blog A",
                "last_updated": "2026-03-20T10:00:00Z",
                "external_id": "blog_a_1"
            },
            {
                "title": "Cooking Tips and Recipes",
                "body": "Best recipes for beginners to start their cooking journey.",
                "source": "Blog B",
                "last_updated": "2026-03-20T10:00:00Z",
                "external_id": "blog_b_1"
            },
            {
                "title": "Python Automation Scripts",
                "body": "Learn how to automate your daily tasks using Python scripts and libraries.",
                "source": "Tech News",
                "last_updated": "2026-03-21T14:30:00Z",
                "external_id": "tech_news_1"
            },
            {
                "title": "Data Pipeline with Apache Airflow",
                "body": "Data pipeline architecture using Airflow and Python for ETL processes.",
                "source": "Data Blog",
                "last_updated": "2026-03-22T09:15:00Z",
                "external_id": "data_blog_1"
            },
            {
                "title": "Travel Guide: Paris",
                "body": "Explore the beautiful city of Paris with our comprehensive travel guide.",
                "source": "Travel Magazine",
                "last_updated": "2026-03-23T11:45:00Z",
                "external_id": "travel_mag_1"
            },
            {
                "title": "Automation in Manufacturing",
                "body": "How automation is transforming the manufacturing industry with robots and AI.",
                "source": "Industry Weekly",
                "last_updated": "2026-03-23T15:20:00Z",
                "external_id": "industry_weekly_1"
            },
        ]
    
    @staticmethod
    def _fetch_newsapi_data() -> List[Dict]:
        """
        Fetch content from NewsAPI.
        
        For this assignment, we implement a basic version.
        In production, you would:
        1. Get API key from environment
        2. Call https://newsapi.org/v2/everything or top-headlines
        3. Parse and transform the response
        
        For now, this returns mock data as a placeholder.
        """
        # Placeholder: In production, integrate real NewsAPI
        # import requests
        # api_key = os.getenv('NEWSAPI_KEY')
        # response = requests.get(
        #     'https://newsapi.org/v2/top-headlines',
        #     params={'country': 'us', 'apiKey': api_key}
        # )
        # articles = response.json()['articles']
        
        return ContentFetcher._fetch_mock_data()


class MatchingEngine:
    """
    Implements the scoring/matching logic for keywords against content.
    
    Scoring rules:
    - Exact keyword match in title (case-insensitive): 100
    - Partial keyword match in title (case-insensitive): 70
    - Keyword appears only in body: 40
    """
    
    @staticmethod
    def compute_score(keyword: str, content_item: ContentItem) -> int:
        """
        Compute match score for a keyword against a content item.
        
        Args:
            keyword: The keyword string to search for
            content_item: The ContentItem instance to search in
            
        Returns:
            Integer score from 0-100, or None if no match
        """
        keyword_lower = keyword.lower()
        title_lower = content_item.title.lower()
        body_lower = content_item.body.lower()
        
        # Check for exact match in title
        if MatchingEngine._is_exact_word_match(keyword_lower, title_lower):
            return 100
        
        # Check for partial match in title
        if keyword_lower in title_lower:
            return 70
        
        # Check if keyword is in body
        if keyword_lower in body_lower:
            return 40
        
        # No match
        return None
    
    @staticmethod
    def _is_exact_word_match(keyword: str, text: str) -> bool:
        """
        Check if keyword matches as a complete word in text.
        Uses word boundaries to avoid matching partial words.
        
        Args:
            keyword: The keyword to search for
            text: The text to search in
            
        Returns:
            True if exact word match found
        """
        pattern = r'\b' + re.escape(keyword) + r'\b'
        return bool(re.search(pattern, text))


class SupprecssionEngine:
    """
    Implements the suppression logic for previously marked irrelevant flags.
    
    Key rule: If a flag was marked as 'irrelevant', it should not reappear on
    later scans UNLESS the underlying content item has changed (last_updated).
    """
    
    @staticmethod
    def should_suppress(flag: Flag, content_item: ContentItem) -> bool:
        """
        Determine if a flag should be suppressed based on suppression rules.
        
        A flag is suppressed if:
        1. It is marked as 'irrelevant' AND
        2. The content item has NOT changed since it was marked irrelevant
        
        Args:
            flag: The existing Flag instance
            content_item: The current ContentItem
            
        Returns:
            True if the flag should be suppressed, False otherwise
        """
        # Only suppress if status is irrelevant
        if flag.status != 'irrelevant':
            return False
        
        # If we don't have a record of when content was irrelevant-marked, don't suppress
        if flag.irrelevant_at_content_version is None:
            return False
        
        # Compare: has content been updated AFTER we marked it irrelevant?
        # If content.last_updated > flag.irrelevant_at_content_version, content changed
        # In that case, don't suppress (allow re-surfacing)
        if content_item.last_updated > flag.irrelevant_at_content_version:
            return False
        
        # Content has not changed since irrelevant, so suppress
        return True


class ScanService:
    """
    Orchestrates the scanning process:
    1. Fetch content from source
    2. For each content + keyword combination, compute score
    3. Create new flags, update existing ones, apply suppression
    """
    
    @staticmethod
    @transaction.atomic
    def run_scan(source: str) -> Dict:
        """
        Execute a complete scan:
        1. Fetch content items from source
        2. For each keyword, match against all content
        3. Create or update flags
        4. Apply suppression rules
        
        Args:
            source: Content source ('mock' or 'newsapi')
            
        Returns:
            Dict with scan statistics
        """
        stats = {
            'source': source,
            'content_items_processed': 0,
            'flags_created': 0,
            'flags_updated': 0,
            'flags_suppressed': 0,
        }
        
        # Fetch content from source
        try:
            content_data = ContentFetcher.fetch_from_source(source)
        except Exception as e:
            raise ValueError(f"Failed to fetch content: {str(e)}")
        
        if not content_data:
            return stats
        
        # Upsert content items
        content_map = {}
        for item_data in content_data:
            last_updated = item_data['last_updated']
            if isinstance(last_updated, str):
                last_updated = timezone.datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            
            external_id = item_data.get('external_id')
            content_item, created = ContentItem.objects.update_or_create(
                external_id=external_id,
                defaults={
                    'title': item_data['title'],
                    'body': item_data['body'],
                    'source': item_data['source'],
                    'last_updated': last_updated,
                }
            )
            content_map[external_id] = content_item
            stats['content_items_processed'] += 1
        
        # Get all keywords
        keywords = Keyword.objects.all()
        
        # For each keyword, find matches in content
        for keyword in keywords:
            for external_id, content_item in content_map.items():
                # Compute score
                score = MatchingEngine.compute_score(keyword.name, content_item)
                
                # If no match, skip
                if score is None:
                    continue
                
                # Check for existing flag
                try:
                    flag = Flag.objects.get(keyword=keyword, content_item=content_item)
                    
                    # Flag exists - check if we should suppress it
                    if SupprecssionEngine.should_suppress(flag, content_item):
                        stats['flags_suppressed'] += 1
                        continue
                    
                    # Content changed - reset irrelevant suppression if applicable
                    if flag.status == 'irrelevant' and content_item.last_updated > flag.irrelevant_at_content_version:
                        flag.status = 'pending'
                        flag.reviewed_at = None
                        flag.irrelevant_at_content_version = None
                        flag.score = score
                        flag.save()
                        stats['flags_updated'] += 1
                    
                except Flag.DoesNotExist:
                    # Create new flag
                    Flag.objects.create(
                        keyword=keyword,
                        content_item=content_item,
                        score=score,
                        status='pending'
                    )
                    stats['flags_created'] += 1
        
        return stats
