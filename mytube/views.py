from django.shortcuts import render, HttpResponse, redirect
from .databaseHandler import *
from django.contrib.auth import authenticate, login, logout as abmelden
from .forms import UploadVideo
import json


def start(request):
    context = {'banner': False, 'content': True, 'profile': True}
    videos = []
    if request.POST.get('login') and request.POST.get('username') \
            and request.POST.get('password'):
        user = authenticate(request, username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None:
            login(request, user)
        else:
            context['loginError'] = True
            context['loginErrorText'] = 'Login Daten sind nicht korrekt. Versuchen Sie es erneut'
    if request.POST.get('search'):
        v = getVideos(None, None, None, None, 10, request.POST.get('text'))
    else:
        v = getVideos(None, None, None, None, 10, None)
    for o in v:
        o.thumbnailPath = o.thumbnailPath[len(os.getcwd()):]
        videos.append(o)
    context['videos'] = videos
    return render(request, 'standard.html', context)


def register(request):
    context = {'banner': False, 'content': False, 'register': True, 'profile': False}
    if request.user.is_authenticated:
        return redirect('/')
    if request.POST.get('register') and request.POST.get('username') \
            and request.POST.get('email') and request.POST.get('password'):
        user = createUser(request.POST.get('username'), request.POST.get('email'), request.POST.get('password'))
        if not user:
            context['message'] = 'E-Mail oder Kanalname/Benutzername bereits vergeben.'
        else:
            return redirect('/')
    return render(request, 'standard.html', context)


def upload(request):
    context = {'banner': False, 'content': False, 'register': False, 'profile': True, 'upload': True}
    if not request.user.is_authenticated:
        return redirect('/')
    form = UploadVideo()
    context['form'] = form
    if request.method == 'POST':
        form = UploadVideo(request.POST, request.FILES)
        if form.is_valid():
            videoPath = saveVideo(form.cleaned_data.get('video'), getChannelName(request.user, None))
            thumbnailPath = saveThumbnail(form.cleaned_data.get('thumbnail'), getChannelName(request.user, None))
            videoUploaded(videoPath, thumbnailPath, form.cleaned_data['title'], getChannelName(request.user, None))
        else:
            context['form'] = form

    return render(request, 'standard.html', context)


def saveVideo(file, channel):
    path = getNewPath(channel, 'video')
    with open(path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return path


def saveThumbnail(file, channel):
    path = getNewPath(channel, 'thumbnail')
    with open(path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return path


def channel(request):
    context = {'banner': True, 'content': True, 'register': False, 'profile': True, 'upload': False}
    videos = []
    if not request.user.is_authenticated:
        return redirect('/')
    if request.POST.get('subscribe'):
        subscribe(request.user.id, request.GET.get('channel'))
    if request.POST.get('unsubscribe'):
        subscribe(request.user.id, request.GET.get('channel'), True)
    if request.GET.get('channel'):
        context['ownChannel'] = False
        context['channelId'] = request.GET.get('channel')
        subscribtions = getSubscriptions(request.user.id)
        subscribedTo = []
        for o in subscribtions:
            subscribedTo.append(o.channel.id)
        if int(context['channelId']) in subscribedTo:
            context['subscribed'] = True
        v = getVideos(request.GET.get('channel'), None, None, None, 10, None)
        for o in v:
            o.thumbnailPath = o.thumbnailPath[len(os.getcwd()):]
            videos.append(o)
        context['videos'] = videos
        context['channelName'] = getChannelName(None, request.GET.get('channel'))
    else:
        v = getVideos(getChannelId(request.user), None, None, None, 10, None)
        for o in v:
            o.thumbnailPath = o.thumbnailPath[len(os.getcwd()):]
            videos.append(o)
        context['ownChannel'] = True
        context['videos'] = videos
        context['channelName'] = getChannelName(request.user, None)
    return render(request, 'standard.html', context)


def video(request):
    context = {'register': False, 'profile': True}
    if request.POST.get('login') and request.POST.get('username') \
            and request.POST.get('password'):
        user = authenticate(request, username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None:
            login(request, user)
        else:
            context['loginError'] = True
            context['loginErrorText'] = 'Login Daten sind nicht korrekt. Versuchen Sie es erneut'
    if not request.GET.get('video'):
        return redirect('/')
    videoInfo = getVideoInfo(request.GET.get('video'))
    if request.POST.get('comment'):
        createComment(videoInfo['id'], request.POST.get('commentText'), getChannelId(request.user))
    comments = getComments(videoInfo['id'], 20)
    context.update(videoInfo)
    context['comments'] = comments
    return render(request, 'video.html', context)


def rating(request):
    if request.method == 'POST':
        numbers = rateVideo(int(request.POST.get('like')), request.user.id, request.POST.get('videoId'))
        return HttpResponse(
            json.dumps({'likes': numbers[0], 'dislikes': numbers[1]}),
            content_type="application/json"
        )


def logout(request):
    abmelden(request)
    return redirect('/')
