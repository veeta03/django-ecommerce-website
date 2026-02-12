from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.conf import settings

from .models import Product, Cart, CartItem, Order, OrderItem, Payment, Category

import razorpay
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


# ------------------ HOME ------------------

def home(request):
    category_slug = request.GET.get('category')
    query = request.GET.get('q')

    products = Product.objects.all()

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if query:
        products = products.filter(name__icontains=query)

    categories = Category.objects.all()

    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories
    })



# ------------------ PRODUCT DETAIL ------------------

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'store/product_detail.html', {'product': product})


# ------------------ CART ------------------

@login_required
def cart(request):
    cart = Cart.objects.filter(user=request.user).first()

    items = []
    total = 0

    if cart:
        items = CartItem.objects.filter(cart=cart)
        total = sum(item.total_price() for item in items)

    return render(request, 'store/cart.html', {
        'items': items,
        'total': total
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')


@login_required
def update_cart(request, item_id, action):
    item = CartItem.objects.get(id=item_id)

    if action == 'increase':
        item.quantity += 1
    elif action == 'decrease':
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
            return redirect('cart')

    item.save()
    return redirect('cart')


# ------------------ CHECKOUT ------------------

@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('cart')

    items = CartItem.objects.filter(cart=cart)
    total = sum(item.total_price() for item in items)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Create Order
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            address=address,
            phone=phone,
            total_amount=total,
            status='Pending'
        )

        # Create Order Items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Initialize Razorpay
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        # Create Razorpay Order
        payment_data = {
            "amount": int(total * 100),  # in paise
            "currency": "INR",
            "receipt": f"order_{order.id}"
        }

        razorpay_order = client.order.create(payment_data)

        # Save Razorpay Order ID in Order model
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        # Create Payment record
        Payment.objects.create(
            order=order,
            payment_method="Razorpay",
            transaction_id=razorpay_order['id'],
            payment_status="Pending"
        )

        return render(request, 'store/payment.html', {
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': int(total * 100)
        })

    return render(request, 'store/checkout.html', {'total': total})


# ------------------ PAYMENT SUCCESS ------------------

@csrf_exempt
def payment_success(request):
    if request.method == "POST":

        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            # Verify signature
            client.utility.verify_payment_signature(params_dict)

            # Fetch order
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)

            # Update order
            order.status = "Paid"
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.save()

            # Update payment record
            payment = Payment.objects.get(order=order)
            payment.payment_status = "Completed"
            payment.save()

            # Clear cart after successful payment
            CartItem.objects.filter(cart__user=order.user).delete()
            return render(request, 'store/payment_success.html')



        except:
            return HttpResponseBadRequest("Payment verification failed")


# ------------------ ORDER HISTORY ------------------

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})
@login_required
def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"<b>Invoice - Order #{order.id}</b>", styles['Title']))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"Customer Name: {order.full_name}", styles['Normal']))
    elements.append(Paragraph(f"Address: {order.address}", styles['Normal']))
    elements.append(Paragraph(f"Phone: {order.phone}", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))

    data = [["Product", "Quantity", "Price"]]

    for item in order.orderitem_set.all():
        data.append([
            item.product.name,
            item.quantity,
            f"₹{item.price}"
        ])

    table = Table(data, colWidths=[3 * inch, 1 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER')
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"<b>Total Amount: ₹{order.total_amount}</b>", styles['Heading2']))

    doc.build(elements)

    return response