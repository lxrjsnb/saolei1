from django.shortcuts import render


def index(request):
    """主页视图"""
    return render(request, 'index.html')
