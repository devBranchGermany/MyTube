from django.db import models
from django.contrib.auth.models import User


class Channel(models.Model):
    # Connection to the django user
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=0)
    name = models.CharField(max_length=30)


class Video(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    videoPath = models.FilePathField()
    thumbnailPath = models.FilePathField()
    likesNumber = models.IntegerField()
    dislikesNumber = models.IntegerField()
    uploadTime = models.DateTimeField()
    title = models.CharField(max_length=30)


class Comment(models.Model):
    author = models.ForeignKey(Channel, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    likesNumber = models.IntegerField()
    dislikesNumber = models.IntegerField()


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)


class VideoRate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    rating = models.BooleanField()


class CommentRate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    rating = models.BooleanField()