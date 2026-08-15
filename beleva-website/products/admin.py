from django.contrib import admin
from .models import Contact, AllProducts , CartItem , ProductDetails , Size , Wishlist

class ProductDetailsInline(admin.TabularInline):
    model = ProductDetails
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name' , 'discount_price' , 'original_price' , 'stock' , 'category' , 'is_available' , 'modified_date')
    prepopulated_fields = {'slug' : ('product_name' , )}
    inlines = [ProductDetailsInline]

admin.site.register(Contact)
admin.site.register(CartItem)
admin.site.register(AllProducts , ProductAdmin)
admin.site.register(ProductDetails)
admin.site.register(Size)
admin.site.register(Wishlist)
