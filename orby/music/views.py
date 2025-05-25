from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def music_home(request):
    
    return render(request, 'music/music_home.html')
