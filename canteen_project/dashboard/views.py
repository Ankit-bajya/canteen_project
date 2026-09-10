# dashboard/views.py
from .models import Notification
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Brand, Item ,Order ,OrderItem
from django.contrib.admin.views.decorators import staff_member_required


@login_required(login_url='login')
def dashboard_home(request):
    # Base QuerySets
    categories = Category.objects.all()
    items = Item.objects.all()

    # URL Parameters extract kar rahe hain
    search_query = request.GET.get('search', '')
    selected_category_id = request.GET.get('category', '')
    selected_brand_id = request.GET.get('brand', '')

    # 1. Search Bar Logic (Item name search karne par)
    if search_query:
        items = items.filter(name__icontains=search_query)

    # 2. Category Filter Logic (Category par click karne par)
    if selected_category_id:
        items = items.filter(category_id=selected_category_id)

    # 3. Brand Filter Logic (Agar category ke andar specific brand choose kare)
    if selected_brand_id:
        items = items.filter(brand_id=selected_brand_id)

    # Category choose hone par uske related Brands fetch karo
    brands = None
    if selected_category_id:
        brands = Brand.objects.filter(category_id=selected_category_id)

    context = {
        'categories': categories,
        'brands': brands,
        'items': items,
        'search_query': search_query,
        'selected_category_id': selected_category_id,
        'selected_brand_id': selected_brand_id,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required(login_url='login')
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    if not item.is_available:
        messages.error(request, "Ye item abhi available nahi hai.")
        return redirect('dashboard_home')

    cart = request.session.get('cart', {})
    item_id_str = str(item_id)

    if item_id_str in cart:
        cart[item_id_str]['quantity'] += 1
    else:
        cart[item_id_str] = {
            'name': item.name,
            'price': float(item.price),
            'quantity': 1,
            'image': item.image.url if item.image else ''
        }

    request.session['cart'] = cart
    messages.success(request, f"{item.name} cart me add ho gaya!")
    return redirect('dashboard_home')


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    item_id_str = str(item_id)

    if item_id_str in cart:
        del cart[item_id_str]
        request.session['cart'] = cart
        messages.info(request, "Item cart se hata diya gaya.")

    return redirect('view_cart')


# dashboard/views.py me view_cart update karein

@login_required(login_url='login')
def view_cart(request):
    cart = request.session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())

    if request.method == 'POST':
        if not cart:
            messages.error(request, "Aapka cart khali hai!")
            return redirect('dashboard_home')

        delivery_location = request.POST.get('delivery_location')
        specific_spot = request.POST.get('specific_spot', '')
        payment_method = request.POST.get('payment_method', 'COD')

        # 1. Main Order Create karo Database me
        order = Order.objects.create(
            user=request.user,
            total_amount=total_price,
            payment_method=payment_method,
            delivery_location=delivery_location,
            specific_spot=specific_spot
        )

        # 2. Cart ke sare items ko OrderItems table me save karo
        for item_id, item_data in cart.items():
            item_obj = Item.objects.get(id=int(item_id))
            OrderItem.objects.create(
                order=order,
                item=item_obj,
                quantity=item_data['quantity'],
                price=item_data['price']
            )

        # 3. Order save hone ke baad Session Cart Clear (Khali) kar do
        request.session['cart'] = {}

        messages.success(request, f"Order #{order.id} Place Ho Gaya Hai! Delivered within 25 Mins.")
        return redirect('order_success', order_id=order.id)

    context = {
        'cart': cart,
        'total_price': total_price,
        'locations': Order.LOCATION_CHOICES,
    }
    return render(request, 'dashboard/cart.html', context)
@login_required(login_url='login')
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'dashboard/order_success.html', {'order': order})

@login_required(login_url='login')
def my_orders(request):
    # User ke sare orders newest first fetch karo
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/my_orders.html', {'orders': user_orders})

@staff_member_required
def kitchen_dashboard(request):
    # Sare pending aur active orders
    active_orders = Order.objects.exclude(status='DELIVERED').order_by('-created_at')
    completed_orders = Order.objects.filter(status='DELIVERED').order_by('-created_at')[:10]
    items = Item.objects.all()

    context = {
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'items': items,
    }
    return render(request, 'dashboard/kitchen.html', context)


@staff_member_required
def update_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)
    order.status = status
    order.save()

    # Dynamic Location Name Nikalo (Custom Spot ya Dropdown Location)
    location_display = order.get_delivery_location_display()
    if order.specific_spot:
        location_display += f" ({order.specific_spot})"

    # Automatic Notification Messages Logic
    if status == 'OUT_FOR_DELIVERY':
        title = "🚀 Order Out for Delivery!"
        msg = f"Hi {order.user.username}, aapka Order #{order.id} canteen se nikal chuka hai! Delivery location: {location_display} par pahuchein."
        Notification.objects.create(user=order.user, title=title, message=msg)

    elif status == 'DELIVERED':
        title = "✅ Order Delivered!"
        msg = f"Order #{order.id} deliver kar diya gaya hai. Enjoy your meal!"
        Notification.objects.create(user=order.user, title=title, message=msg)

    elif status == 'CANCELLED':
        title = "❌ Order Cancelled"
        msg = f"Aapka Order #{order.id} cancel kar diya gaya hai."
        Notification.objects.create(user=order.user, title=title, message=msg)

    messages.success(request, f"Order #{order.id} status updated to {status}!")
    return redirect('kitchen_dashboard')

@staff_member_required
def toggle_item_availability(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.is_available = not item.is_available
    item.save()
    messages.info(request, f"{item.name} status updated!")
    return redirect('kitchen_dashboard')


@login_required(login_url='login')
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'PENDING':
        order.status = 'CANCELLED'
        order.save()
        messages.success(request, f"Order #{order.id} cancel kar diya gaya hai.")
    else:
        messages.error(request, "Ye order ab cancel nahi ho sakta kyunki process ho chuka hai.")
    return redirect('my_orders')



@login_required(login_url='login')
def notifications_view(request):
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Unread notifications ko read mark kar do page open hote hi
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'dashboard/notifications.html', {'notifications': user_notifications})

