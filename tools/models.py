from django.db import models
from django.contrib.auth.models import User

class AiTool(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ai_tools")
    url = models.URLField(unique=True)
    favicon = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    keywords = models.JSONField(default=list, blank=True)
    likes = models.ManyToManyField(User, related_name="liked_tools", blank=True)
    shares = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.CharField(default='Free',max_length=10,choices=[("Free","Free"),("Freemium","Freemium"),("Premium","Premium")])

    def total_likes(self):
        return self.likes.count()  # Efficient like count

    def total_bookmarks(self):
        return self.bookmarked_by.count()  # Efficient bookmark count

    def __str__(self):
        return self.title or self.url

    class Meta:
        ordering = ["-created_at"]


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    tool = models.ForeignKey(AiTool, on_delete=models.CASCADE, related_name="bookmarked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bookmarked {self.tool.title}"
