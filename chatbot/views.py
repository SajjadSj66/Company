from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import json
from datetime import datetime
import random
import os
import re

# بارگذاری داده‌ها
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def find_course(query):
    query = query.lower()
    all_courses = []
    for category in data.get('sections', {}).get('courses', {}).get('categories', {}).values():
        all_courses.extend(category)
    for course in all_courses:
        keywords = course['title'].lower().split()
        keywords.extend(course.get('id', '').split('-'))
        for keyword in keywords:
            if keyword in query:
                return course
    return None

def find_instructor(query):
    query = query.lower()
    instructors = data.get('sections', {}).get('instructors', {}).get('items', [])
    for instructor in instructors:
        keywords = instructor['name'].lower().split()
        keywords.extend(instructor['expertise'].lower().split())
        if any(keyword in query for keyword in keywords):
            return instructor
    return None

def find_portfolio(query):
    query = query.lower()
    portfolio_items = data.get('sections', {}).get('portfolio', {}).get('items', [])
    for item in portfolio_items:
        keywords = item['name'].lower().split()
        keywords.extend(item['category'].lower().split())
        keywords.extend(item['tech'].lower().split())
        if any(keyword in query for keyword in keywords):
            return item
    return None

def get_consultation_info():
    consultation = data.get('sections', {}).get('consultation', {})
    fields = consultation.get('fields', [])
    response = f"""💬 **{consultation.get('title', 'مشاوره رایگان')}**

{consultation.get('description', '')}

📋 **اطلاعات مورد نیاز:**
"""
    for field in fields:
        response += f"• {field}\n"
    response += f"\n{consultation.get('message', 'کارشناسان ما با شما تماس می‌گیرند.')}"
    return response

def find_answer(message, user_name=None):
    message_lower = message.lower()
    
    # سلام با اسم
    if any(w in message_lower for w in ['سلام', 'خوبی', 'چطوری', 'سلامت']):
        if user_name:
            return f"سلام {user_name} جان! 👋 چطور می‌تونم کمکت کنم؟\n\nدر مورد دوره‌ها، اساتید، نمونه کارها یا مشاوره بپرس."
        return "سلام! 👋 به آذریزدان خوش اومدی.\n\nدر مورد دوره‌ها، اساتید، نمونه کارها یا مشاوره بپرس."
    
    # خداحافظی
    if any(w in message_lower for w in ['خداحافظ', 'بای', 'goodbye', 'فعلا', 'بعدا']):
        if user_name:
            return f"خداحافظ {user_name} جان! 🌟 خوشحال شدم کمکت کنم.\n\nهر وقت سوالی داشتی، من اینجام!"
        return random.choice(data.get('goodbye', ['خداحافظ! 🌟 خوشحال شدم کمکت کنم.']))
    
    # 1. سوالات متداول
    for item in data.get('faq', []):
        for keyword in item.get('keywords', []):
            if keyword in message_lower:
                return item.get('answer', '')
    
    # 2. دوره‌ها
    course = find_course(message)
    if course:
        response = f"""📚 **{course['title']}**

👨‍🏫 مدرس: {course['instructor']}
📊 سطح: {course['level']}
⏱️ مدت: {course['duration']}
💰 هزینه: {course['price']}
📝 توضیحات: {course['description']}

🔑 پیش‌نیاز: {course.get('prerequisites', 'در توضیحات دوره مشخص شده')}

برای ثبت‌نام با شماره {data.get('company', {}).get('phone', '')} تماس بگیرید."""
        if user_name:
            response = f"{user_name} جان، {response}"
        return response
    
    # 3. اساتید
    instructor = find_instructor(message)
    if instructor:
        response = f"""👨‍🏫 **{instructor['name']}**

🎯 تخصص: {instructor['expertise']}
📅 سابقه: {instructor['experience']}
📝 درباره: {instructor['bio']}"""
        if user_name:
            response = f"{user_name} عزیز، {response}"
        return response
    
    # 4. نمونه کارها
    portfolio = find_portfolio(message)
    if portfolio:
        response = f"""🌟 **{portfolio['name']}**

📂 دسته‌بندی: {portfolio['category']}
💻 تکنولوژی‌ها: {portfolio['tech']}
📝 توضیحات: {portfolio['description']}"""
        if user_name:
            response = f"{user_name} جان، {response}"
        return response
    
    # 5. مشاوره
    if any(word in message_lower for word in ['مشاوره', 'فرم', 'راهنمایی', 'کمک', 'تماس']):
        return get_consultation_info()
    
    # 6. شرکت
    if any(word in message_lower for word in ['شرکت', 'آذریزدان', 'تاسیس', 'کی', 'درباره']):
        company = data.get('company', {})
        response = f"""🏢 **درباره آذریزدان**

{company.get('description', '')}

📅 تاسیس: {company.get('founded', '')}
📞 تلفن: {company.get('phone', '')}
✉️ ایمیل: {company.get('email', '')}
📍 آدرس: {company.get('address', '')}
🌐 وب‌سایت: {company.get('website', '')}"""
        return response
    
    # 7. تشخیص موضوع برای پاسخ هوشمند
    topics = []
    if any(w in message_lower for w in ['برنامه', 'کد', 'برنامه‌نویسی', 'پروژه', 'برنامه نویسی']):
        topics.append("برنامه‌نویسی")
    if any(w in message_lower for w in ['هوش', 'مصنوعی', 'ai', 'یادگیری', 'علم داده']):
        topics.append("هوش مصنوعی")
    if any(w in message_lower for w in ['سایت', 'وب', 'طراحی', 'wordpress', 'وردپرس']):
        topics.append("طراحی وب‌سایت")
    if any(w in message_lower for w in ['آموزش', 'کلاس', 'دوره', 'استاد', 'مدرس']):
        topics.append("آموزش")
    if any(w in message_lower for w in ['فروش', 'بازاریابی', 'تبلیغات', 'سئو', 'seo']):
        topics.append("بازاریابی و سئو")
    
    if topics:
        topic_str = "، ".join(topics)
        if user_name:
            return f"{user_name} جان! 😊 سوالت درباره {topic_str} هست.\n\nمتخصصان ما در آذریزدان می‌تونن کمک کنن.\n\n📞 برای مشاوره دقیق‌تر با شماره {data.get('company', {}).get('phone', '')} تماس بگیرید.\n\nیا فرم مشاوره رو پر کنید تا کارشناسان ما با شما تماس بگیرن."
        return f"😊 سوالت درباره {topic_str} هست.\n\nمتخصصان ما در آذریزدان می‌تونن کمک کنن.\n\n📞 برای مشاوره دقیق‌تر با شماره {data.get('company', {}).get('phone', '')} تماس بگیرید.\n\nیا فرم مشاوره رو پر کنید تا کارشناسان ما با شما تماس بگیرن."
    
    # 8. پاسخ پیش‌فرض با پیشنهاد تماس با پشتیبانی
    fallbacks = [
        "سوال خوبی پرسیدی! 🧐\n\nمتخصصان ما در آذریزدان می‌تونن کمک کنن.\n\n📞 با شماره {phone} تماس بگیرید.\n\n✉️ یا فرم مشاوره رو پر کنید تا کارشناسان ما با شما تماس بگیرن.",
        "دقیقاً متوجه نشدم! 😊\n\nموضوعات قابل پرسش:\n🔹 دوره‌های آموزشی\n🔹 اساتید\n🔹 نمونه کارها\n🔹 مشاوره\n🔹 درباره شرکت\n\n📞 یا با شماره {phone} با پشتیبانی تماس بگیرید."
    ]
    reply = random.choice(fallbacks).format(phone=data.get('company', {}).get('phone', '۰۴۱۳-۵۵۷۹۳۹۶'))
    if user_name:
        reply = f"{user_name} جان، {reply}"
    return reply

def chatbot_view(request):
    return render(request, 'chatbot.html')

@csrf_exempt
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user_name = request.session.get('user_name', None)
    body = json.loads(request.body)
    user_message = body.get('message', '').strip()
    
    if not user_message:
        return JsonResponse({'reply': 'لطفاً یه سوال بپرسید! 😊'})
    
    bot_reply = find_answer(user_message, user_name)
    return JsonResponse({
        'reply': bot_reply,
        'timestamp': datetime.now().strftime('%H:%M')
    })

@csrf_exempt
def upload_file(request):
    """آپلود فایل در چت‌بات"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'فایلی ارسال نشده'}, status=400)
    
    file = request.FILES['file']
    
    # بررسی نوع فایل
    allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.zip', '.rar']
    ext = os.path.splitext(file.name)[1].lower()
    
    if ext not in allowed_extensions:
        return JsonResponse({'error': 'نوع فایل پشتیبانی نمی‌شود'}, status=400)
    
    # بررسی حجم فایل (حداکثر ۱۰ مگابایت)
    if file.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'حجم فایل باید کمتر از ۱۰ مگابایت باشد'}, status=400)
    
    # ذخیره فایل
    file_name = f"chatbot_uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
    path = default_storage.save(file_name, ContentFile(file.read()))
    
    return JsonResponse({
        'success': True,
        'message': 'فایل با موفقیت آپلود شد ✅',
        'file_name': file.name,
        'file_url': default_storage.url(path)
    })

def get_user_api(request):
    user_name = request.session.get('user_name', None)
    return JsonResponse({
        'name': user_name,
        'is_logged_in': user_name is not None
    })

def quick_action(request, action):
    user_name = request.session.get('user_name', None)
    name_prefix = f"{user_name} جان، " if user_name else ""
    
    responses = {
        'active': {
            'user': 'چقدر طول میکشه یه سایت فروشگاهی طراحی کنید؟',
            'bot': f"""{name_prefix}بستگی به پیچیدگی پروژه داره ولی معمولاً سایت‌های فروشگاهی بین ۳ تا ۶ هفته زمان می‌بره. اگر قالب آماده استفاده کنید سریع‌تر تموم میشه، ولی اگر سفارشی‌سازی کامل بدید، زمان بیشتری نیازه.

📌 پیشنهاد من: بیا یه مشاوره رایگان با تیممون هماهنگ کنم تا دقیقاً نیازت رو بررسی کنیم. موافقی؟"""
        },
        'academy': {
            'user': 'دوره پایتون دارید؟',
            'bot': f"""{name_prefix}چشم! 🐍 ما دوره‌های پایتون رو در سه سطح برگزار می‌کنیم:

1. مقدماتی — مناسب افراد بدون سابقه کدنویسی
2. متوسط — با تمرکز بر پروژه‌محوری و جنگو
3. پیشرفته — همراه با هوش مصنوعی و یادگیری ماشین

دوره بعدی ۱۵ شهریور شروع میشه. می‌خوای برات ثبت‌نام کنم؟"""
        },
        'technical': {
            'user': 'برای پروژه‌ای که قراره روزانه ۱۰ هزار کاربر داشته باشه، چه معماری پیشنهاد می‌دید؟',
            'bot': f"""سوال خیلی خوبی پرسیدی! 👌 برای این حجم کاربری، این معماری رو پیشنهاد می‌کنم:

- Backend: Django یا FastAPI (با معماری میکروسرویس)
- Database: PostgreSQL به همراه Redis برای کش
- Load Balancer: Nginx برای توزیع ترافیک
- Deployment: روی Docker و Kubernetes

تیم ما دقیقاً همین رو برای چندین پروژه بزرگ پیاده کرده. اگر نیاز به مشاوره تخصصی داری، خوشحال میشیم کمکت کنیم."""
        },
        'contact': {
            'user': 'می‌خوام فرم مشاوره رو پر کنم',
            'bot': f"""💬 مشاوره رایگان!

برای دریافت مشاوره تخصصی در حوزه‌های برنامه‌نویسی، هوش مصنوعی، طراحی وب‌سایت و آموزش، فرم زیر رو پر کنید:

📌 نام و نام خانوادگی
📌 شماره تماس
📌 ایمیل
📌 موضوع مورد نظر
📌 پیام شما

پس از ثبت، کارشناسان ما در اسرع وقت با شما تماس می‌گیرند."""
        }
    }
    
    return JsonResponse(responses.get(action, {}))