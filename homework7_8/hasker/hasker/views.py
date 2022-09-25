from django.shortcuts import render

def index(request):
    context = {
        'title': 'Home page'
    }
    return render(request, 'home.html', context)
