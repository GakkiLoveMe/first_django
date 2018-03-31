from django.shortcuts import render

# Create your views here.


def cart(request):
    """购物车"""
    return render(request, 'cart.html')
