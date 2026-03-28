"""
Admin configuration for monitoring app.
"""

from django.contrib import admin
from monitoring.models import Keyword, ContentItem, Flag


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'last_updated', 'created_at')
    list_filter = ('source', 'created_at')
    search_fields = ('title', 'body')
    ordering = ('-created_at',)


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'content_item', 'score', 'status', 'created_at')
    list_filter = ('status', 'keyword', 'created_at')
    search_fields = ('keyword__name', 'content_item__title')
    ordering = ('-score', '-created_at')
    readonly_fields = ('keyword', 'content_item', 'score', 'created_at', 'reviewed_at')
    
    fieldsets = (
        ('Match Info', {
            'fields': ('keyword', 'content_item', 'score')
        }),
        ('Review Status', {
            'fields': ('status', 'reviewed_at')
        }),
        ('Suppression Info', {
            'fields': ('irrelevant_at_content_version',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
