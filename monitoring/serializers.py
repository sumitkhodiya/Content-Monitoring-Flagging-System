"""
Serializers for API endpoints.
"""

from rest_framework import serializers
from monitoring.models import Keyword, ContentItem, Flag


class KeywordSerializer(serializers.ModelSerializer):
    """Serializer for Keyword model."""
    
    class Meta:
        model = Keyword
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContentItemSerializer(serializers.ModelSerializer):
    """Serializer for ContentItem model."""
    
    class Meta:
        model = ContentItem
        fields = ['id', 'title', 'body', 'source', 'last_updated', 'created_at', 'external_id']
        read_only_fields = ['id', 'created_at', 'external_id']


class FlagSerializer(serializers.ModelSerializer):
    """Serializer for Flag model."""
    keyword_name = serializers.CharField(source='keyword.name', read_only=True)
    content_item_title = serializers.CharField(source='content_item.title', read_only=True)
    
    class Meta:
        model = Flag
        fields = [
            'id', 
            'keyword', 
            'keyword_name',
            'content_item', 
            'content_item_title',
            'score', 
            'status', 
            'created_at',
            'reviewed_at'
        ]
        read_only_fields = ['id', 'score', 'created_at', 'reviewed_at', 'keyword_name', 'content_item_title']


class FlagUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating flag status."""
    
    class Meta:
        model = Flag
        fields = ['status']
    
    def update(self, instance, validated_data):
        """Override update to track review timestamp."""
        from django.utils import timezone
        instance.status = validated_data.get('status', instance.status)
        instance.reviewed_at = timezone.now()
        
        # If marking as irrelevant, save the content item's current last_updated timestamp
        # This is used for suppression logic
        if validated_data.get('status') == 'irrelevant':
            instance.irrelevant_at_content_version = instance.content_item.last_updated
        else:
            instance.irrelevant_at_content_version = None
        
        instance.save()
        return instance


class ScanRequestSerializer(serializers.Serializer):
    """Serializer for scan request."""
    source = serializers.ChoiceField(
        choices=['mock', 'newsapi'],
        help_text="Data source: 'mock' for local dataset, 'newsapi' for real API"
    )
