from django.contrib.auth.models import User
from django.db import models


class ChatGroup(models.Model):
    # Store all our chat rooms
    group_name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.group_name

    class Meta:
        verbose_name_plural = "Chat Groups"


class GroupMessages(models.Model):
    # Store group messages
    group = models.ForeignKey(
        ChatGroup, related_name="chat_messages_rel", on_delete=models.CASCADE
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} : {self.content[:20]} : Room-{self.group.group_name}"

    class Meta:
        verbose_name_plural = "Group Messages"
        ordering = ["-timestamp"]
