from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Category, MenuItem, Table, Order, OrderItem
from django.db.models import Q

def home(request):
    """หน้าแรก - เลือกโต๊ะ"""
    tables = Table.objects.all()
    return render(request, 'orders/home.html', {'tables': tables})

def menu(request, table_id):
    """หน้าเมนูอาหาร"""
    table = get_object_or_404(Table, id=table_id)
    categories = Category.objects.all().prefetch_related('items')
    
    # ดึง order ที่ยังไม่เสร็จของโต๊ะนี้
    current_order = Order.objects.filter(
        table=table, 
        status__in=['pending', 'preparing']
    ).first()
    
    context = {
        'table': table,
        'categories': categories,
        'current_order': current_order,
    }
    return render(request, 'orders/menu.html', context)

def add_to_order(request, table_id, item_id):
    """เพิ่มรายการอาหารเข้า order"""
    if request.method == 'POST':
        table = get_object_or_404(Table, id=table_id)
        menu_item = get_object_or_404(MenuItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        special_instructions = request.POST.get('special_instructions', '')
        
        # หา order ที่กำลังใช้งานหรือสร้างใหม่
        order, created = Order.objects.get_or_create(
            table=table,
            status__in=['pending', 'preparing'],
            defaults={'status': 'pending'}
        )
        
        # เพิ่มรายการอาหาร
        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=quantity,
            special_instructions=special_instructions
        )
        
        if created:
            table.status = 'occupied'
            table.save()
        
        messages.success(request, f'เพิ่ม {menu_item.name} เข้าออเดอร์แล้ว')
        return redirect('menu', table_id=table_id)
    
    return redirect('menu', table_id=table_id)

def view_order(request, order_id):
    """ดูรายละเอียด order"""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/view_order.html', context)

def update_order_status(request, order_id):
    """อัพเดทสถานะ order"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            if new_status == 'completed':
                order.table.status = 'available'
                order.table.save()
            
            messages.success(request, 'อัพเดทสถานะเรียบร้อย')
        
    return redirect('view_order', order_id=order_id)

def all_orders(request):
    """ดูออเดอร์ทั้งหมด"""
    status_filter = request.GET.get('status', '')
    
    orders = Order.objects.all()
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_filter': status_filter,
    }
    return render(request, 'orders/all_orders.html', context)

def delete_order_item(request, item_id):
    """ลบรายการอาหารจาก order"""
    if request.method == 'POST':
        item = get_object_or_404(OrderItem, id=item_id)
        order = item.order
        item.delete()
        order.calculate_total()
        messages.success(request, 'ลบรายการเรียบร้อย')
        return redirect('view_order', order_id=order.id)
    
    return redirect('home')