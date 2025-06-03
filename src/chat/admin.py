from django.contrib import admin

from .models import Group, Message


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "group",
        "content_preview",
        "timestamp",
    )
    list_filter = (
        "group",
        "author",
        "timestamp",
    )
    search_fields = (
        "content",
        "author__username",
        "group__name",
    )

    def content_preview(self, obj):
        text = obj.content or ""
        return f"{text[:50]}..." if len(text) > 50 else text

    content_preview.short_description = "Content"
