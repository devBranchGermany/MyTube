from django import forms


class UploadVideo(forms.Form):
    video = forms.FileField()
    thumbnail = forms.FileField()
    title = forms.CharField(max_length=30)

    def clean(self):
        video = self.cleaned_data.get('video')
        thumbnail = self.cleaned_data.get('thumbnail')
        print()
        if not (video.content_type == 'video/mp4' or video.content_type == 'video/webm' or
                video.content_type == 'video/ogg'):
            raise forms.ValidationError("Das Video muss im MP4, WEBM oder OGG Format sein.")

        if not (thumbnail.content_type == 'image/png' or thumbnail.content_type == 'image/jpeg'):

            raise forms.ValidationError("Das Bild muss im PNG oder JPEG Format sein.")