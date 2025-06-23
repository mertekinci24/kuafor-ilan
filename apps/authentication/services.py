import requests
import logging
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import timedelta
from .models import OTPVerification, CustomUser
import re

logger = logging.getLogger(__name__)


class OTPService:
    """OTP işlemleri için servis sınıfı"""
    
    @staticmethod
    def create_otp(phone_number=None, email_address=None, otp_type='login', user=None, request=None):
        """
        OTP oluştur ve gönder
        """
        try:
            # Telefon numarası formatını düzenle
            if phone_number:
                phone_number = OTPService.format_phone_number(phone_number)
                delivery_method = 'sms'
                target = phone_number
            else:
                delivery_method = 'email'
                target = email_address
            
            # OTP kodu üret
            otp_code = OTPVerification.generate_otp()
            
            # Son geçerlilik zamanı (5 dakika)
            expires_at = timezone.now() + timedelta(minutes=5)
            
            # IP adresi ve user agent bilgisi
            ip_address = None
            user_agent = ''
            if request:
                ip_address = OTPService.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # OTP kaydı oluştur
            otp_record = OTPVerification.objects.create(
                user=user,
                otp_code=otp_code,
                otp_type=otp_type,
                delivery_method=delivery_method,
                phone_number=phone_number,
                email_address=email_address,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # OTP gönder
            if delivery_method == 'sms':
                success = SMSService.send_otp_sms(phone_number, otp_code, otp_type)
            else:
                success = EmailService.send_otp_email(email_address, otp_code, otp_type)
            
            if success:
                logger.info(f"OTP sent successfully to {target}")
                return True, otp_record, f"OTP kodu {target} adresine gönderildi."
            else:
                logger.error(f"Failed to send OTP to {target}")
                return False, None, "OTP gönderilirken bir hata oluştu."
            
        except Exception as e:
            logger.error(f"OTP creation failed: {str(e)}")
            return False, None, f"OTP oluşturulurken hata: {str(e)}"
    
    @staticmethod
    def verify_otp(otp_code, phone_number=None, email_address=None, otp_type='login'):
        """
        OTP doğrula
        """
        try:
            # OTP kaydını bul
            if phone_number:
                phone_number = OTPService.format_phone_number(phone_number)
                otp_record = OTPVerification.objects.filter(
                    phone_number=phone_number,
                    otp_type=otp_type,
                    is_used=False
                ).order_by('-created_at').first()
            else:
                otp_record = OTPVerification.objects.filter(
                    email_address=email_address,
                    otp_type=otp_type,
                    is_used=False
                ).order_by('-created_at').first()
            
            if not otp_record:
                return False, None, "Geçerli bir OTP bulunamadı."
            
            # OTP doğrula
            is_valid, message = otp_record.verify(otp_code)
            
            if is_valid:
                logger.info(f"OTP verified successfully for {phone_number or email_address}")
                return True, otp_record, message
            else:
                logger.warning(f"OTP verification failed for {phone_number or email_address}: {message}")
                return False, otp_record, message
            
        except Exception as e:
            logger.error(f"OTP verification error: {str(e)}")
            return False, None, f"OTP doğrulama hatası: {str(e)}"
    
    @staticmethod
    def format_phone_number(phone):
        """
        Telefon numarasını +905551234567 formatına çevir
        """
        # Sadece rakamları al
        phone = re.sub(r'\D', '', phone)
        
        # Başında 90 varsa +90 ekle
        if phone.startswith('90') and len(phone) == 12:
            return f"+{phone}"
        
        # Başında 0 varsa 90 ile değiştir
        if phone.startswith('0') and len(phone) == 11:
            return f"+9{phone}"
        
        # Başında hiçbiri yoksa +90 ekle
        if len(phone) == 10:
            return f"+90{phone}"
        
        return phone
    
    @staticmethod
    def get_client_ip(request):
        """
        Kullanıcının IP adresini al
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SMSService:
    """SMS gönderme servisi"""
    
    @staticmethod
    def send_otp_sms(phone_number, otp_code, otp_type='login'):
        """
        OTP SMS gönder
        """
        try:
            # SMS mesajını hazırla
            if otp_type == 'login':
                message = f"Kuafor İlan giriş kodunuz: {otp_code}. Bu kodu kimseyle paylaşmayın."
            elif otp_type == 'register':
                message = f"Kuafor İlan kayıt onay kodunuz: {otp_code}. Hoş geldiniz!"
            elif otp_type == 'password_reset':
                message = f"Kuafor İlan şifre sıfırlama kodunuz: {otp_code}."
            else:
                message = f"Kuafor İlan doğrulama kodunuz: {otp_code}."
            
            # Development modunda console'a yazdır
            if settings.DEBUG:
                print(f"\n🔔 SMS CONSOLE DEBUG 🔔")
                print(f"📱 To: {phone_number}")
                print(f"💬 Message: {message}")
                print(f"🔢 OTP: {otp_code}")
                print(f"⏰ Time: {timezone.now()}")
                print("=" * 40)
                return True
            
            # Production modunda gerçek SMS gönder
            return SMSService.send_netgsm_sms(phone_number, message)
            
        except Exception as e:
            logger.error(f"SMS sending failed: {str(e)}")
            return False
    
    @staticmethod
    def send_netgsm_sms(phone_number, message):
        """
        Netgsm ile SMS gönder
        """
        try:
            # Netgsm API bilgileri (environment variables'dan al)
            username = getattr(settings, 'NETGSM_USERNAME', '')
            password = getattr(settings, 'NETGSM_PASSWORD', '')
            header = getattr(settings, 'NETGSM_HEADER', 'KUAFORILAN')
            
            if not username or not password:
                logger.warning("Netgsm credentials not configured")
                return False
            
            # API URL
            url = "https://api.netgsm.com.tr/sms/send/get"
            
            # Parametreler
            params = {
                'usercode': username,
                'password': password,
                'gsmno': phone_number.replace('+', ''),
                'message': message,
                'msgheader': header,
                'filter': '0'
            }
            
            # HTTP isteği gönder
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.text.strip()
                if result.startswith('00'):
                    logger.info(f"SMS sent successfully to {phone_number}")
                    return True
                else:
                    logger.error(f"Netgsm API error: {result}")
                    return False
            else:
                logger.error(f"Netgsm HTTP error: {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"Netgsm SMS error: {str(e)}")
            return False


class EmailService:
    """Email gönderme servisi"""
    
    @staticmethod
    def send_otp_email(email_address, otp_code, otp_type='login'):
        """
        OTP email gönder
        """
        try:
            # Email konusu ve içeriği
            if otp_type == 'login':
                subject = "Kuaför İlan - Giriş Doğrulama Kodu"
            elif otp_type == 'register':
                subject = "Kuaför İlan - Kayıt Doğrulama Kodu"
            elif otp_type == 'password_reset':
                subject = "Kuaför İlan - Şifre Sıfırlama Kodu"
            else:
                subject = "Kuaför İlan - Doğrulama Kodu"
            
            # Development modunda console'a yazdır
            if settings.DEBUG:
                print(f"\n📧 EMAIL CONSOLE DEBUG 📧")
                print(f"📧 To: {email_address}")
                print(f"📋 Subject: {subject}")
                print(f"🔢 OTP: {otp_code}")
                print(f"⏰ Time: {timezone.now()}")
                print("=" * 40)
                return True
            
            # Simple email message
            message = f"""
Merhaba,

{subject}

Doğrulama kodunuz: {otp_code}

Bu kod 5 dakika geçerlidir.

Kuaför İlan Ekibi
https://kuaforilan.com
            """
            
            # Email gönder
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_address],
                fail_silently=False
            )
            
            logger.info(f"OTP email sent to {email_address}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return False


class SocialAuthService:
    """Sosyal medya authentication servisi"""
    
    @staticmethod
    def create_user_from_social(provider, provider_data):
        """
        Sosyal medya verilerinden kullanıcı oluştur
        """
        try:
            email = provider_data.get('email')
            if not email:
                return None, "Email adresi bulunamadı."
            
            # Kullanıcı zaten var mı kontrol et
            user = CustomUser.objects.filter(email=email).first()
            
            if not user:
                # Yeni kullanıcı oluştur
                user = CustomUser.objects.create_user(
                    username=email,
                    email=email,
                    first_name=provider_data.get('given_name', ''),
                    last_name=provider_data.get('family_name', ''),
                    is_verified=True,  # Sosyal medya ile geldiği için doğrulanmış kabul et
                    email_verified=True
                )
            
            # Sosyal medya bağlantısını kaydet
            from .models import SocialAuthProvider
            SocialAuthProvider.objects.get_or_create(
                user=user,
                provider=provider,
                defaults={
                    'provider_id': provider_data.get('id', ''),
                    'provider_email': email,
                    'profile_data': provider_data
                }
            )
            
            return user, "Başarılı"
            
        except Exception as e:
            logger.error(f"Social auth user creation failed: {str(e)}")
            return None, f"Kullanıcı oluşturma hatası: {str(e)}"
            
