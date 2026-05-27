from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import Course, Cart, CartItem, Order, OrderItem
from .forms import CourseSearchForm, CartItemUpdateForm, CheckoutForm

# ============================
# ویوهای مربوط به نمایش دوره‌ها
# ============================
class CourseListView(ListView):
    model = Course
    template_name = 'course_list.html'
    context_object_name = 'courses'
    paginate_by = 6

    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True)
        self.form = CourseSearchForm(self.request.GET)
        if self.form.is_valid():
            q = self.form.cleaned_data.get('q')
            category = self.form.cleaned_data.get('category')
            if q:
                queryset = queryset.filter(
                    Q(title__icontains=q) | Q(short_description__icontains=q)
                )
            if category:
                queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form
        context['popular_courses'] = Course.objects.filter(is_popular=True, is_active=True)[:3]
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_courses'] = Course.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:3]
        # بررسی وجود دوره در سبد خرید کاربر (در صورت ورود)
        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
            context['in_cart'] = cart.items.filter(course=self.object).exists()
        return context


# ============================
# توابع کمکی برای سبد خرید
# ============================
def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


# ============================
# ویوهای سبد خرید (نیاز به لاگین)
# ============================
@login_required
def add_to_cart(request, slug):
    """افزودن دوره به سبد خرید (اگر موجود باشد، تعداد +1 می‌شود)"""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    cart = get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, course=course)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, f"تعداد دوره «{course.title}» در سبد خرید شما افزایش یافت.")
    else:
        messages.success(request, f"دوره «{course.title}» به سبد خرید اضافه شد.")
    return redirect('courses:cart_detail')


@login_required
def cart_detail(request):
    """نمایش محتویات سبد خرید با فرم آپدیت تعداد"""
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('course').all()
    # ساخت فرم برای هر آیتم
    item_forms = {}
    for item in items:
        item_forms[item.id] = CartItemUpdateForm(instance=item)
    
    if request.method == 'POST':
        # پردازش آپدیت تعداد
        item_id = request.POST.get('item_id')
        if item_id:
            item = get_object_or_404(CartItem, id=item_id, cart=cart)
            form = CartItemUpdateForm(request.POST, instance=item)
            if form.is_valid():
                form.save()
                messages.success(request, "تعداد با موفقیت به‌روزرسانی شد.")
            else:
                messages.error(request, "تعداد وارد شده معتبر نیست.")
            return redirect('courses:cart_detail')
    
    total = cart.total_price()
    return render(request, 'cart_detail.html', {
        'cart': cart,
        'items': items,
        'item_forms': item_forms,
        'total': total,
    })


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """حذف یک آیتم از سبد خرید"""
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    course_title = cart_item.course.title
    cart_item.delete()
    messages.success(request, f"دوره «{course_title}» از سبد خرید حذف شد.")
    return redirect('courses:cart_detail')


# ============================
# ویوهای تسویه حساب و سفارش
# ============================
@login_required
def checkout(request):
    """نمایش فرم دریافت اطلاعات و ایجاد سفارش"""
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('course').all()
    
    if not items.exists():
        messages.error(request, "سبد خرید شما خالی است.")
        return redirect('courses:cart_detail')
    
    total = cart.total_price()
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            # ایجاد سفارش
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                postal_code=form.cleaned_data['postal_code'],
                city=form.cleaned_data.get('city', ''),
                state=form.cleaned_data.get('state', ''),
                total_amount=total,
                status='pending'
            )
            # انتقال آیتم‌های سبد خرید به OrderItem
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    course=item.course,
                    price_at_purchase=item.course.price,
                    quantity=item.quantity
                )
            # خالی کردن سبد خرید
            cart.clear()
            messages.success(request, "سفارش شما با موفقیت ثبت شد. لطفاً برای پرداخت اقدام کنید.")
            return redirect('courses:payment', order_id=order.id)
        else:
            messages.error(request, "لطفاً اطلاعات را به درستی وارد کنید.")
    else:
        form = CheckoutForm(user=request.user)
    
    return render(request, 'checkout.html', {
        'form': form,
        'items': items,
        'total': total,
    })


@login_required
def payment(request, order_id):
    """صفحه پرداخت (mock) - درگاه واقعی را اینجا وصل کنید"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'paid':
        messages.info(request, "این سفارش قبلاً پرداخت شده است.")
        return redirect('courses:order_history')
    
    # در این نقطه معمولاً به درگاه پرداخت مانند زرین‌پال هدایت می‌کنید.
    # برای نمونه، یک پرداخت آزمایشی ساده شبیه‌سازی می‌کنیم.
    if request.method == 'POST':
        # فرض کنیم پرداخت موفق بوده است
        transaction_id = f"TRX-{order.id}-{request.user.id}"
        order.mark_as_paid(transaction_id=transaction_id)
        messages.success(request, "پرداخت با موفقیت انجام شد. به جمع دانشجویان خوش آمدید.")
        return redirect('courses:order_history')
    
    return render(request, 'payment.html', {'order': order})


@login_required
def order_history(request):
    """تاریخچه سفارشات کاربر"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__course').order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})