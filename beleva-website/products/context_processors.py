from .models import Wishlist , CartItem
from accounts.models import Register

def wishlist_processor(request):
    wishlist_ids = []
    user_id = request.session.get('register_id')
    if user_id:
        wishlist_ids = list(Wishlist.objects.filter(user_id=user_id).values_list('product_id', flat=True))
    return {'wishlist_ids': wishlist_ids}

def cart_item_count(request):
    user_id = request.session.get('register_id')
    if user_id:   
        try:
            user = Register.objects.get(id = user_id)
            count = CartItem.objects.filter(user=user).count()
        except Register.DoesNotExist:
            count = 0
    else:
        count = 0
    return {'cart_items_count': count}