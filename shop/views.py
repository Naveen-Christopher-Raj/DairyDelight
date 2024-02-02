from django.http import JsonResponse
from django.shortcuts import render,redirect
from .forms import CustomUserform
from . models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
import json

def home(request):
    products = Product.objects.filter(trending=1)
    catagory = Catagory.objects.filter(status=0)
    context = {
        'catagory' : catagory,
        'products' : products,
        }
    return render(request, 'shop/index.html', context)

def favviewpage(request):
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        context = { 'fav' : fav }
        return render(request, 'shop/fav.html', context)
    else:
        return redirect('/')

def remove_fav(request, fid):
     item = Favourite.objects.get(id=fid)
     item.delete()
     return redirect('/favviewpage')

def cart_page(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        context = { 'cart' : cart }
        return render(request, 'shop/cart.html', context)
    else:
        return redirect('/')

def remove_cart(request, cid):
     cartitem = Cart.objects.get(id=cid)
     cartitem.delete()
     return redirect('/cart')

def fav_page(request):
    if request.headers.get('X-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_id= data['pid']
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status': 'Product Added to favourite'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add favourite'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)

def add_to_cart(request):
    if request.headers.get('X-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_qty= data['product_qty']
            product_id= data['pid']
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in cart'}, status=200)
                else:
                    if product_status.quantity>=product_qty:
                        Cart.objects.create(user=request.user, product_id=product_id,product_qty=product_qty)
                        return JsonResponse({'status': 'Product Added to cart'}, status=200)
                    else:
                        return JsonResponse({'status': 'Stock not available'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add cart'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out successfully..!")
    return redirect('/')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == "POST":
            name = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=name,password=password)
            if user is not None:
                login(request,user)
                messages.success(request, "Logged in successfully..!")
                return redirect('/')
            else:
                messages.error(request,"Invaild Username or Password")
                return redirect('login')
        return render(request, 'shop/login.html')

def register(request):
    form = CustomUserform()
    if request.method == "POST":
        form = CustomUserform(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration Success you can Login Now..!")
            return redirect('login')
    context = { 'form' : form }
    return render(request, 'shop/register.html', context)

def collections(request):
    catagory = Catagory.objects.filter(status=0)
    context = {'catagory' : catagory}
    return render(request, 'shop/collections.html', context)

def collectionsitem(request, name):
    if(Catagory.objects.filter(name=name, status=0)):
        products = Product.objects.filter(catagory__name=name)
        context = {
            'products' : products,
            'catagory_name' : name
            }
        return render(request, 'shop/products/products.html', context)
    else:
        messages.warning(request,"No such category found")
        return redirect('collections')
    
def product_details(request, cname, pname):
    if(Catagory.objects.filter(name=cname, status=0)):
        if (Product.objects.filter(name=pname, status=0)):
            products = Product.objects.filter(name=pname, status=0).first()
            return render(request, 'shop/products/product_details.html', {'products':products})
        else:
            messages.warning(request,"No such product found")
            return redirect('collections')
    else:
        messages.warning(request,"No such category found")
        return redirect('collections')