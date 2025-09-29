from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .forms import OrderForm, RegisterForm, LoginForm, ReviewForm
from django.contrib.auth import login, authenticate, logout

# Create your views here.

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
        
    return render(request, 'store/product_list.html', {'products': products, 'categories': categories})



def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                return redirect('product_detail', pk=product.pk)
        else:
            return redirect('login')
    else:
        form = ReviewForm()
    return render(request, 'store/product_detail.html', {'product':product, "reviews":reviews, "form":form})



def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    return cart



def add_to_cart(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('cart_detail')



def cart_detail(request):
    cart = get_cart(request)
    items = CartItem.objects.filter(cart=cart)
    return render(request, 'store/cart_detail.html', {'cart': cart, 'items': items})



def checkout(request):
    cart = get_cart(request)
    items = CartItem.objects.filter(cart=cart)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )
            items.delete()
            
            return render(request, 'store/order_success.html', {'order': order})
    else:
        form = OrderForm()
    
    return render(request, 'store/checkout.html', {'form': form, 'items': items, 'cart': cart})



def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = LoginForm()
    return render(request, 'store/login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('product_list')