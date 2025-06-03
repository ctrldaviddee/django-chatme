# --------------------------------------------------------------------------
# Description: Database models for the chat application.
# --------------------------------------------------------------------------

from django.contrib.auth.models import User
from django.db import models


class Group(models.Model):
    """
    Represents a chat groupt or room
    """

    name = models.CharField(
        max_length=225, unique=True, help_text="Unique name for the chat group"
    )
    # TODO: more fields like 'description', 'created_by', 'members' (ManyToManyField to User)
    # For simplicity, we'll start with just the name.
    # members = models.ManyToManyField(User, related_name='chat_groups', blank=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    """
    Represents a message sent in a chat group.
    """

    group = models.ForeignKey(Group, related_name="messages", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}: {self.content[:20]} in {self.group.name}"

    class Meta:
        ordering = ["timestamp"]
