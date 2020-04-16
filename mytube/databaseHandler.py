from .models import *
from django.contrib.auth.models import User
from django.db.models import Q, F
import os
from datetime import datetime


def createUser(username, email, password):
    user = User.objects.filter(Q(username=username) | Q(email=email))
    if user.count() > 0:
        return False
    else:
        user = User.objects.create_user(username, email, password)
        createChannel(username, user.id)
        return user


def createChannel(name, userId):
    channel = Channel.objects.filter(name=name)
    user = User.objects.filter(id=userId)
    if channel.count() > 0 or user.count() == 0:
        return False
    user = user[0]
    channel = Channel.objects.create(name=name, user=user)
    return channel


def checkDirectory(channel):
    path = os.getcwd() + '/static/media/' + channel
    if not os.path.isdir(path):
        os.mkdir(path)
        os.mkdir(path + '/video')
        os.mkdir(path + '/thumbnail')


def getNewPath(channel, type):
    checkDirectory(channel)
    path = os.getcwd() + '/static/media/' + channel
    files = os.listdir(path + '/' + type)
    if not len(files):
        result = path + '/' + type + '/000000'
        open(result, 'a').close()
        return result
    result = path + '/' + type + '/' + str(int(max(files)) + 1).zfill(6)
    open(result, 'a').close()
    return result


def videoUploaded(videoPath, thumbnailPath, title, channelName):
    channel = Channel.objects.filter(name=channelName)
    if channel.count() == 0:
        return False
    channel = channel[0]
    Video.objects.create(videoPath=videoPath, thumbnailPath=thumbnailPath,
                         likesNumber=0, dislikesNumber=0, uploadTime=datetime.now(),
                         channel=channel, title=title)


def deleteVideo(videoId):
    video = Video.objects.filter(id=videoId)
    if video.count() == 0:
        return False
    video = video[0]
    video.delete()


def rateVideo(rate, userId, videoId):
    user = User.objects.filter(id=userId)
    video = Video.objects.filter(id=videoId)
    if user.count() == 0 or video.count() == 0:
        return False
    user = user[0]
    videoRate = VideoRate.objects.filter(user=user, video=video[0])
    if videoRate.count() > 0:
        if videoRate[0].rating:
            video.update(likesNumber=F('likesNumber')-1)
        else:
            video.update(dislikesNumber=F('dislikesNumber')-1)
        videoRate.update(rating=rate)
    else:
        VideoRate.objects.create(rating=rate, user=user, video=video[0])
    if rate == 1:
        video.update(likesNumber=F('likesNumber') + 1)
    elif rate == 0:
        video.update(dislikesNumber=F('dislikesNumber') + 1)
    return video[0].likesNumber, video[0].dislikesNumber


def createComment(videoId, text, channelId):
    video = Video.objects.filter(id=videoId)
    channel = Channel.objects.filter(id=channelId)
    if video.count() == 0 or channel.count() == 0:
        return False
    video = video[0]
    channel = channel[0]
    Comment.objects.create(text=text, author=channel, video=video, likesNumber=0,
                                     dislikesNumber=0)


def getComments(videoId, amount):
    video = Video.objects.filter(id=videoId)
    if video.count() == 0:
        return False
    video = video[0]
    comments = Comment.objects.order_by('-id').filter(video=video)[:amount]
    result = []
    for o in comments:
        result.append({'text': o.text, 'author': getChannelName(None, o.author_id)})
    return result


def rateComment(rate, userId, commentId):
    user = User.objects.filter(id=userId)
    comment = Comment.objects.filter(id=commentId)
    if user.count() == 0 or comment.count() == 0:
        return False
    user = user[0]
    commentRate = CommentRate.objects.filter(user=user, comment=comment[0])
    if commentRate.count() > 0:
        if commentRate[0].rating:
            comment.update(likesNumber=F('likesNumber') - 1)
        else:
            comment.update(dislikesNumber=F('dislikesNumber') - 1)
        commentRate.update(rating=rate)
    else:
        CommentRate.objects.create(rating=rate, user=user, comment=comment[0])
    if rate == 1:
        comment.update(likesNumber=F('likesNumber') + 1)
    elif rate == 0:
        comment.update(dislikesNumber=F('dislikesNumber') + 1)


def subscribe(userId, channelId, unsubscribe=False):
    user = User.objects.filter(id=userId)
    channel = Channel.objects.filter(id=channelId)
    if user.count() == 0 or channel.count() == 0:
        return False
    user = user[0]
    channel = channel[0]
    subscription = Subscription.objects.filter(channel=channel, user=user)
    if subscription.count() > 0:
        if unsubscribe:
            subscription[0].delete()
            return True
        else:
            return False
    Subscription.objects.create(channel=channel, user=user)


def getSubscriptions(userId):
    channels = Subscription.objects.filter(user__id=userId)
    return channels


def getVideos(channelId, subscribedById, timeRange, sortByRate, amount, title):
    videos = Video.objects.all()
    if channelId is not None:
        channel = Channel.objects.filter(id=channelId)
        if channel.count() == 0:
            return False
        channel = channel[0]
        videos = videos.filter(channel=channel)
    if subscribedById is not None:
        user = User.objects.filter(id=subscribedById)
        if user.count() == 0:
            return False
        user = user[0]
        subscriptions = Subscription.objects.filter(user=user)
        videos = videos and Video.objects.filter(channel_id__in=[o.channel_id for o in subscriptions])
    if timeRange is not None:
        videos = videos and Video.objects.filter(uploadTime__gte=timeRange[0], uploadTime__lte=timeRange[1])
    if sortByRate is not None:
        videos = videos.annotate(popularity=F('likesNumber') + F('dislikesNumber')).order_by('popularity')
    if amount is not None:
        videos = videos[:amount]
    if title is not None:
        videos = videos and Video.objects.filter(title__contains=title)
    return videos


def getChannelName(user, channelId):
    if user is not None:
        channels = Channel.objects.filter(user=user)
    elif channelId is not None:
        channels = Channel.objects.filter(id=channelId)
    if channels.count() > 0:
        return channels[0].name


def getChannelId(user):
    channels = Channel.objects.filter(user=user)
    if channels.count() > 0:
        return channels[0].id


def getVideoInfo(videoId):
    video = Video.objects.filter(id=videoId)
    if not video.count() > 0:
        return False
    video = video.first()
    videoPath = video.videoPath[len(os.getcwd()):]
    thumbnailPath = video.thumbnailPath[len(os.getcwd()):]
    result = {'id': video.id, 'videoPath': videoPath, 'thumbnailPath': thumbnailPath,
              'likesNumber': video.likesNumber, 'dislikesNumber': video.dislikesNumber,
              'uploadTime': video.uploadTime, 'channel': video.channel, 'title': video.title}
    return result
