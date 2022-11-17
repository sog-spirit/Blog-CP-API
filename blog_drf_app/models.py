from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    POST_STATUS = [
        ("DRAFT", "Draft"),
        ("PUBLISH", "Publish")
    ]

    title = models.CharField(max_length=256)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=7, choices=POST_STATUS, default="DRAFT")

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f'Post by {self.author.username}, with id: {self.id}'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    is_delete = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f'Comment by {self.user.username}, content: {self.content}'