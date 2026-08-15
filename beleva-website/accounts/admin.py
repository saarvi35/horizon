from django.contrib import admin
from .models import Register , BillingAddress , Order , OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = [ 'id','user','status','created_at']
    list_filter = ['status']
    search_fields = ['user__name','id']

admin.site.register(Register)
admin.site.register(Order , OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(BillingAddress)
