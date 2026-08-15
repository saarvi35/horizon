from django.shortcuts import render,redirect ,get_object_or_404
from django.http import HttpResponse
from .models import Register , BillingAddress , Order , OrderItem
from products.models import CartItem , AllProducts
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import string,random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
import stripe 
stripe.api_key = settings.STRIPE_SECRET_KEY

def register(request):                    # register page
    if request.method=="POST":
        name_var = request.POST.get('name')
        contact_var = request.POST.get('phone_no')
        email_var = request.POST.get('email')
        
        password_var = request.POST.get('password')
        confirm_password_var = request.POST.get('confirm')

        if confirm_password_var != password_var:
            messages.error(request, 'Passwords donot match.')
            return redirect('register')

        hashed_password = make_password(password_var)
        data1 = Register(
            name=name_var,
           phone_no = contact_var,
           
            email=email_var,
            password=hashed_password
            
        )

        data1.save()
        messages.success(request, "Registration successful!")
        return redirect('login')

    return render(request, 'accounts/register.html')

def user_login(request):  
    if request.method =='POST':
        email_var = request.POST.get('email_login')  # we store email which is entered by user in email_var
        password_var = request.POST.get('password_login')

        try:
            form_data = Register.objects.filter(email = email_var).first() # in form model give rows which match the user entered email [email is register email]
            if form_data is None:
                messages.error(request, "User does not exist")
                return render(request, 'accounts/login.html')
            
            if check_password(password_var , form_data.password):
                request.session['register_id'] = form_data.id   
                request.session['user_email'] = form_data.email  
                messages.success(request,"Login Successful!")
                return redirect('home')
            else:
                messages.error(request,"Incorrect Password!")
                return render(request , 'accounts/login.html')
        except Register.DoesNotExist:
            messages.error("User does not exist") 
            return render (request,'accounts/login.html')

    return render(request , 'accounts/login.html')
   

def logout(request):
    request.session.flush()
    messages.error(request,"Logout Successfull")
    return redirect('login')




def address(request):
    register_id = request.session.get('register_id')
    if not register_id:
        return redirect('login') 
    user = Register.objects.get(id = register_id)
    saved_address = BillingAddress.objects.filter(user_id = register_id)

    if request.method == 'POST':
        selected_address = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method')
        email_shipping = None
        if selected_address:
            try:
                address = BillingAddress.objects.get(id = selected_address)
                email_shipping = address.email_shipping
            except BillingAddress.DoesNotExist:
                pass 
        else:
            full_name = request.POST.get('full_name')
            email_shipping = request.POST.get('email_shipping')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            country = request.POST.get('country')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zip_code = request.POST.get('zip_code')
            order_notes = request.POST.get('order_notes')

            address = BillingAddress.objects.create(
                user = user ,
                full_name = full_name,
                email_shipping = email_shipping,
                phone = phone , 
                address = address,
                country = country , 
                city = city ,
                state = state , 
                zip_code = zip_code,
                order_notes = order_notes
            )
        buy_now = request.session.get('buy_now')
        grand_total = 0
        items = []
        if buy_now:
            product = get_object_or_404(AllProducts , id=buy_now['id'])
            quantity = buy_now.get('quantity' , 1)
            price = product.discount_price * quantity
            grand_total += price
            items.append({
                'product' : product ,
                'quantity' : quantity , 
                'price' : price
            })
        else:
            cart = CartItem.objects.filter(user_id = register_id)
            if not cart.exists():
                return redirect('cart')
            
            grand_total = 0
            for item in cart:
                grand_total += item.total_price()
                items.append({
                    'product' : item.product ,
                    'quantity' : item.quantity ,
                    'price' : item.total_price()
                })

        # shipping charges
        if grand_total < 1499:
            grand_total += 99 
        
        full_address = f"{address.address}, {address.city}, {address.state}, {address.country} - {address.zip_code}"

        if payment_method == 'COD':
            order = Order.objects.create(
                user = user,
                payment_method = "COD" ,
                status = "Pending" , 
                total_price = grand_total , 
                billing_address = full_address
            )
            for item in cart:
                OrderItem.objects.create(
                    order = order ,
                    product = item.product , 
                    quantity = item.quantity ,
                    price = item.total_price()
                )
            cart.delete()
            return redirect('payment_success' , order_id = order.id)
        else:
            request.session['order_data'] = {
                'email' : email_shipping ,
                'address' : address.id ,
                'grand_total' : str(grand_total) ,
            }
            session = stripe.checkout.Session.create(
                payment_method_types= ['card'],
                line_items= [{
                    'price_data' : {
                        'currency':'inr' ,
                        'product_data' : {'name': 'Order from Beleva'},
                        'unit_amount' : int(grand_total * 100) ,
                    },
                    'quantity' : 1,
                }],
                mode= 'payment',
                success_url= 'http://127.0.0.1:8000/accounts/payment_success/' , 
                cancel_url= 'http://127.0.0.1:8000/accounts/payment_cancel' ,
                customer_email= email_shipping ,
            )

        return redirect(session.url , code=303)
    buy_now = request.session.get('buy_now')
    if buy_now:
        product = get_object_or_404(AllProducts , id=buy_now['id'])
        quantity = buy_now.get('quantity' , 1)
        total = product.discount_price * quantity
        grand_total += price
        items.append({
            'product' : product ,
            'quantity' : quantity , 
            'price' : total
            })
    else:
        cart = CartItem.objects.filter(user_id = register_id)
        total = 0
        for item in cart:
            total += item.total_price()
        items = cart
    return render(request , 'accounts/billing.html' , {'saved_address' : saved_address , 'items' : items , 'total' : total})


def billing(request):
    register_id = request.session.get('register_id')
    if not register_id:
        return redirect('login') 
    user = Register.objects.get(id = register_id)
    addresses = BillingAddress.objects.filter(user_id = register_id)
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email_shipping')
        phone_no = request.POST.get('phone')
        address = request.POST.get('address')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip_code')


        BillingAddress.objects.create(
            user = user ,
            full_name = full_name,
            email_shipping =    email , 
            phone = phone_no , 
            address = address,
            country = country ,
            state = state ,
            city = city ,
            zip_code = zip_code
        )
        return redirect('add_address')

    return render(request , 'accounts/address.html' , {'addresses' : addresses})

def delete_address(request , address):
    address = get_object_or_404(BillingAddress, id=address)
    address.delete()
    return redirect('add_address') 

def payment_success(request, order_id=None):
    if order_id:
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'accounts/success.html', {'order': order})

    register_id = request.session.get('register_id')
    if not register_id:
        return redirect('login')

    order_data = request.session.get('order_data')
    if not order_data:
        return redirect('login')

    user = Register.objects.get(id=register_id)
    email_shipping = order_data.get('email')
    address = order_data.get('address')
    grand_total = order_data.get('grand_total')

    try:
        billing = BillingAddress.objects.get(id=address)
    except BillingAddress.DoesNotExist:
        messages.error(request, "Billing address not found.")
        return redirect('cart')

    full_address = f"{billing.address}, {billing.city}, {billing.state}, {billing.country} - {billing.zip_code}"

    order = Order.objects.create(
        user=user,
        payment_method="Online Payment",
        status="Paid",
        total_price=grand_total,
        billing_address=full_address
    )

    cart_items = CartItem.objects.filter(user_id=register_id)
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.total_price()
        )

    cart_items.delete()
    del request.session['order_data']

    messages.success(request, "Payment successful! Your order has been placed.")
    return render(request, 'accounts/success.html', {'order': order})


def payment_cancel(request):
    return render(request , 'accounts/cancel.html')


@login_required
def google_login_success(request):
    social_user = request.user
    if not social_user.is_authenticated:
        messages.error(request, "Google login failed. Please try again.")
        return redirect('login')

    email = social_user.email
    name = social_user.get_full_name()

    user = Register.objects.filter(email=email).first()
    if not user:
        user = Register.objects.create(
            name=name,
            email=email,
            phone_no="0000000000",  
            password="google_auth_user"
        )
        messages.success(request, "Account created.")
    else:
        messages.success(request, "Login successful!")

    request.session.flush()
    request.session['register_id'] = user.id
    request.session['user_email'] = user.email

    return redirect('home')



def delete_account(request):
    register_id = request.session.get('register_id')
    user = Register.objects.get(id = register_id)
    user.delete()
    request.session.flush()
    return redirect('home')


def profile(request):
    register_id = request.session.get('register_id')
    if not register_id:
        return redirect('login')

    try:
        user = Register.objects.get(id=register_id)
    except Register.DoesNotExist:
        return HttpResponse(f"No user found for ID {register_id}")

    return render(request, 'accounts/profile.html', {'user': user})


def forget_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        user = Register.objects.filter(email=email).first()  

        if user:
            otp = random.randint(100000, 999999)

            request.session['reset_email'] = email
            request.session['otp'] = str(otp)

            send_mail(
                subject='Your OTP for Password Reset',
                message=f'Your OTP is: {otp}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            return redirect('verify_otp')
        else:
            messages.error(request, "No account found with this email.")
    return render(request, 'accounts/forget_password.html')


def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if entered_otp == session_otp:
            return redirect('reset_password')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    return render(request, 'accounts/verify_otp.html')


def reset_password(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            email = request.session.get('reset_email')
            user = Register.objects.filter(email=email).first()
            if user:
                user.password = make_password(password)
                user.save()
                messages.success(request, "Password reset successful.")
                return redirect('login')
            else:
                messages.error(request, "Error: User not found.")
    return render(request, 'accounts/reset_password.html')


def order_history(request):
    user_id = request.session.get('register_id')
    user = Register.objects.get(id=user_id)
    orders = Order.objects.filter(user=user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'accounts/order_history.html', {'orders': orders})


def track_order(request , order_id):
    register_id = request.session.get('register_id')
    if not register_id:
        messages.error(request,"Please login to view your orders")
        return redirect('login')

    order = get_object_or_404(Order,id=order_id,user_id=register_id)
    tracking_steps = [
        'PENDING',
        'PROCESSING',
        'PACKED',
        'SHIPPED',
        'IN_TRANSIT',
        'OUT_FOR_DELIVERY',
        'DELIVERED',
    ]
    order_status = order.status.upper()
    if order_status not in tracking_steps:
        tracking_steps.insert(0,order_status)
    current_index = tracking_steps.index(order_status)
 
    return render(request, 'accounts/track_order.html', {
        'order': order,
        'steps' : tracking_steps ,
        'current_index' : current_index ,
        })

def help_center(request):
    return render(request , 'mart/help_center.html')