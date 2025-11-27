from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="ชื่อหมวดหมู่")
    description = models.TextField(blank=True, verbose_name="รายละเอียด")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "หมวดหมู่"
        verbose_name_plural = "หมวดหมู่"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', verbose_name="หมวดหมู่")
    name = models.CharField(max_length=200, verbose_name="ชื่อเมนู")
    description = models.TextField(verbose_name="รายละเอียด")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคา")
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True, verbose_name="รูปภาพ")
    is_available = models.BooleanField(default=True, verbose_name="พร้อมจำหน่าย")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "เมนูอาหาร"
        verbose_name_plural = "เมนูอาหาร"

    def __str__(self):
        return self.name


class Table(models.Model):
    STATUS_CHOICES = [
        ('available', 'ว่าง'),
        ('occupied', 'มีคนนั่ง'),
        ('reserved', 'จอง'),
    ]
    
    number = models.CharField(max_length=10, unique=True, verbose_name="หมายเลขโต๊ะ")
    capacity = models.IntegerField(verbose_name="จำนวนที่นั่ง")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="สถานะ")

    class Meta:
        verbose_name = "โต๊ะ"
        verbose_name_plural = "โต๊ะ"

    def __str__(self):
        return f"โต๊ะ {self.number}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอดำเนินการ'),
        ('preparing', 'กำลังเตรียม'),
        ('ready', 'พร้อมเสิร์ฟ'),
        ('completed', 'เสร็จสิ้น'),
        ('cancelled', 'ยกเลิก'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="โต๊ะ")
    customer_name = models.CharField(max_length=100, blank=True, verbose_name="ชื่อลูกค้า")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="สถานะ")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="ยอดรวม")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สั่ง")
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, verbose_name="หมายเหตุ")

    class Meta:
        verbose_name = "ออเดอร์"
        verbose_name_plural = "ออเดอร์"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.table}"

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="ออเดอร์")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name="เมนู")
    quantity = models.IntegerField(default=1, verbose_name="จำนวน")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคา")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคารวม")
    special_instructions = models.TextField(blank=True, verbose_name="คำขอพิเศษ")

    class Meta:
        verbose_name = "รายการสั่ง"
        verbose_name_plural = "รายการสั่ง"

    def save(self, *args, **kwargs):
        self.price = self.menu_item.price
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
        self.order.calculate_total()

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"