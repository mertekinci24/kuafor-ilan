import logging
import re


class IgnoreBotsFilter(logging.Filter):
    """Bot isteklerini log'dan filtreler"""
    
    BOT_PATTERNS = [
        r'wp-admin',
        r'wp-login',
        r'wp-content',
        r'wp-includes',
        r'wordpress',
        r'xmlrpc.php',
        r'phpmyadmin',
        r'\.php',
        r'\.asp',
        r'\.aspx',
    ]
    
    def filter(self, record):
        message = record.getMessage().lower()
        
        # Bot patterns varsa log'a yazma
        for pattern in self.BOT_PATTERNS:
            if re.search(pattern, message):
                return False
        
        return True
