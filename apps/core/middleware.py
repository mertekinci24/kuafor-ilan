from django.http import HttpResponseNotFound
from django.utils.deprecation import MiddlewareMixin
import re


class WordPressProtectionMiddleware(MiddlewareMixin):
    """WordPress bot saldırılarını engeller"""
    
    # WordPress bot patterns
    BLOCKED_PATTERNS = [
        r'^/wp-',
        r'^/wordpress',
        r'^/blog/wp-',
        r'^/site/wp-',
        r'^/web/wp-',
        r'^/cms/wp-',
        r'^/test/wp-',
        r'^/demo/wp-',
        r'/wp-admin',
        r'/wp-login',
        r'/wp-content',
        r'/wp-includes',
        r'/wp-config',
        r'/wp-json',
        r'/xmlrpc.php',
        r'/phpmyadmin',
        r'/admin.php',
        r'/administrator',
    ]
    
    def process_request(self, request):
        path = request.path.lower()
        
        # WordPress patterns kontrolü
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, path):
                return HttpResponseNotFound("Not Found")
        
        # Diğer bot patterns
        suspicious_patterns = [
            r'\.php$',
            r'\.asp$',
            r'\.aspx$',
            r'/cgi-bin/',
            r'/phpmyadmin',
            r'/mysql',
            r'/database',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, path) and not path.startswith('/admin/'):
                return HttpResponseNotFound("Not Found")
        
        return None
      
