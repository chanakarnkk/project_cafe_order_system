from django.contrib import admin
from .models import Category, MenuItem, Table, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'created_at']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']
    list_editable = ['is_available']

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'capacity', 'status']
    list_filter = ['status']
    list_editable = ['status']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['subtotal']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'customer_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'table__number']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['total_amount', 'created_at', 'updated_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity', 'price', 'subtotal']
    list_filter = ['order__status']