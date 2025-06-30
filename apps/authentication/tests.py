from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings # Kullanılmıyorsa kaldırılabilir

User = get_user_model()


class CustomUserTests(TestCase):
    """
    CustomUser modeli ile ilgili testler.
    """

    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123',
            user_type='jobseeker'
        )
        self.assertIsInstance(user, User)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertEqual(user.user_type, 'jobseeker')
        self.assertTrue(user.check_password('testpassword123'))

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123',
            user_type='admin'
        )
        self.assertIsInstance(admin_user, User)
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertEqual(admin_user.user_type, 'admin')
        self.assertTrue(admin_user.check_password('adminpassword123'))


class AuthenticationViewsTests(TestCase):
    """
    apps/authentication uygulamasındaki görünümlerin testleri.
    """

    def setUp(self):
        self.client = Client()
        # Testler için farklı doğrulama durumlarına sahip kullanıcılar oluştur
        self.user_verified = User.objects.create_user(
            username='testuser_verified',
            email='verified@example.com',
            password='testpassword123',
            user_type='jobseeker',
            email_verified=True, # Doğrulanmış e-posta
            phone_verified=True # Doğrulanmış telefon
        )
        self.user_unverified_email = User.objects.create_user(
            username='testuser_unverified_email',
            email='unverified_email@example.com',
            password='testpassword123',
            user_type='jobseeker',
            email_verified=False, # Doğrulanmamış e-posta
            phone_verified=True
        )
        self.user_unverified_phone = User.objects.create_user(
            username='testuser_unverified_phone',
            email='unverified_phone@example.com',
            phone='+905551112233', # Telefon numarası ekleyin
            password='testpassword123',
            user_type='jobseeker',
            email_verified=True,
            phone_verified=False # Doğrulanmamış telefon
        )
        self.admin_user = User.objects.create_superuser(
            username='adminuser_auth',
            email='admin_auth@example.com',
            password='adminpassword123',
            user_type='admin',
            email_verified=True,
            phone_verified=True
        )

    def test_login_view_get(self):
        """
        Giriş sayfasının başarılı bir şekilde yüklendiğini test eder.
        """
        response = self.client.get(reverse('authentication:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_login_view_post_success(self):
        """
        Doğru kimlik bilgileriyle giriş yapıldığında başarılı girişi test eder.
        Şimdi 302 yönlendirmesi bekliyoruz.
        """
        response = self.client.post(reverse('authentication:login'), {
            'username': self.user_verified.email, # Formdaki 'username' alanını kullanın
            'password': 'testpassword123'
        })
        # Başarılı giriş sonrası 302 yönlendirmesi beklenir
        self.assertEqual(response.status_code, 302)
        # Yönlendirilen URL'i kontrol edin. Varsayılan olarak '/' olmalı
        self.assertRedirects(response, '/')
        # Oturumda kullanıcı kimliğinin olup olmadığını kontrol edin
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_view_post_invalid_credentials(self):
        """
        Yanlış kimlik bilgileriyle giriş yapıldığında hatayı test eder.
        """
        response = self.client.post(reverse('authentication:login'), {
            'username': 'nonexistent@example.com', # Formdaki 'username' alanını kullanın
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200) # Hata mesajıyla giriş sayfası tekrar render edilmeli
        self.assertContains(response, 'E-posta veya şifre hatalı.') # Views.py'deki yeni mesajı kontrol edin

    def test_login_with_unverified_email(self):
        """
        Doğrulanmamış bir e-posta ile giriş denemesini test eder.
        """
        response = self.client.post(reverse('authentication:login'), {
            'username': self.user_unverified_email.email,
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 200) # Hata mesajıyla giriş sayfası tekrar render edilmeli
        self.assertContains(response, 'E-posta hesabınız doğrulanmamıştır. Lütfen e-postanıza gönderilen doğrulama bağlantısını tıklayın.')

    def test_login_with_unverified_phone_number(self):
        """
        Doğrulanmamış bir telefon numarası ile giriş denemesini test eder.
        """
        response = self.client.post(reverse('authentication:login'), {
            'username': self.user_unverified_phone.phone, # Telefon numarasını 'username' alanına gönderin
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 200) # Hata mesajıyla giriş sayfası tekrar render edilmeli
        self.assertContains(response, 'Telefon numaranız doğrulanmamıştır. Lütfen telefonunuza gönderilen doğrulama kodunu girin.')

    def test_admin_login_success(self):
        """
        Admin kullanıcısının başarılı girişini test eder.
        """
        response = self.client.post(reverse('authentication:login'), {
            'username': self.admin_user.email,
            'password': 'adminpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/') # Admin de ana sayfaya yönlendirilmeli (veya admin dashboard'a)
        self.assertTrue('_auth_user_id' in self.client.session)


    def test_logout_view(self):
        """
        Kullanıcı çıkışını test eder.
        """
        # Kullanıcıyı giriş yapılmış duruma getiriyoruz
        self.client.login(email='verified@example.com', password='testpassword123')

        # Çıkış isteği gönderiyoruz
        response = self.client.get(reverse('authentication:logout'))

        # Yanıtın bir yönlendirme (302) olup olmadığını kontrol ediyoruz
        self.assertEqual(response.status_code, 302)

        # Yönlendirmenin giriş sayfasına yapıldığını kontrol ediyoruz
        self.assertEqual(response.url, reverse('authentication:login'))

        # Opsiyonel: Yönlendirmeyi takip edip giriş sayfasındaki mesajı kontrol edebilirsiniz
        # response_after_redirect = self.client.get(response.url, follow=True)
        # self.assertEqual(response_after_redirect.status_code, 200)
        # self.assertContains(response_after_redirect, 'Başarıyla çıkış yaptınız. Tekrar görüşmek üzere!')

        
