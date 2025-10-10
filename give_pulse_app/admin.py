from django.contrib import admin
from .models import SuccessStory

@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'donor_name', 'is_published', 'display_order', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'donor_name', 'story_text']
    list_editable = ['is_published', 'display_order']
    ordering = ['display_order', '-created_at']

    fieldsets = (
        ('Story Information', {
            'fields': ('title', 'donor_name', 'story_text')
        }),
        ('Display Settings', {
            'fields': ('is_published', 'display_order', 'image_url')
        }),
    )
