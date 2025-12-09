"""
Proxy Service for Cloud Account Manager
Handles SOCKS5 proxy connections for cloud account checking
"""

import requests
import time
import json
import os
import socket
import socks
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PyQt6.QtCore import QObject, pyqtSignal

class ProxyService(QObject):
    """Service for managing proxy connections"""
    
    connection_test_complete = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.settings_file = os.path.join("config", "proxy_settings.json")
        self.proxy_settings = self.load_settings()
        self.session = None
        
    def load_settings(self):
        """Load proxy settings from file"""
        default_settings = {
            'enabled': False,
            'host': '74.81.81.81',
            'port': '10000',
            'username': '26a928403f27ed635073__cr.ar,au,at,bd,ba,bg;sessttl.5',
            'password': '860de985d1795b42',
            'change_ip_url': '',
            'proxy_type': 'socks5'
        }
        
        try:
            # Create config directory if not exists
            os.makedirs("config", exist_ok=True)
            
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading proxy settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save proxy settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.proxy_settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving proxy settings: {e}")
            return False
    
    def set_proxy(self, settings):
        """Set new proxy settings"""
        self.proxy_settings.update(settings)
        self.save_settings()
        self.session = None  # Reset session to apply new settings
        
    def get_proxy_dict(self):
        """Get proxy dictionary for requests library"""
        if not self.proxy_settings['enabled'] or not self.proxy_settings['host']:
            return None
        
        proxy_type = self.proxy_settings.get('proxy_type', 'socks5').lower()
        host = self.proxy_settings['host']
        port = self.proxy_settings['port']
        
        # Construct proxy URL
        if self.proxy_settings['username'] and self.proxy_settings['password']:
            proxy_url = f"{proxy_type}://{self.proxy_settings['username']}:{self.proxy_settings['password']}@{host}:{port}"
        else:
            proxy_url = f"{proxy_type}://{host}:{port}"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_proxy_for_boto3(self):
        """Get proxy URL for boto3 (AWS SDK)"""
        if not self.proxy_settings['enabled'] or not self.proxy_settings['host']:
            return None
        
        proxy_type = self.proxy_settings.get('proxy_type', 'socks5')
        host = self.proxy_settings['host']
        port = self.proxy_settings['port']
        
        if self.proxy_settings['username'] and self.proxy_settings['password']:
            return f"{proxy_type}://{self.proxy_settings['username']}:{self.proxy_settings['password']}@{host}:{port}"
        else:
            return f"{proxy_type}://{host}:{port}"
    
    def get_session(self):
        """Get or create requests session with proxy"""
        if self.session is None:
            self.session = self.create_session()
        return self.session
    
    def create_session(self):
        """Create requests session with proxy and retry strategy"""
        session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set proxies if enabled
        if self.proxy_settings['enabled'] and self.proxy_settings['host']:
            proxies = self.get_proxy_dict()
            if proxies:
                session.proxies.update(proxies)
                
                # Setup SOCKS proxy for socket level
                if self.proxy_settings.get('proxy_type', 'socks5') == 'socks5':
                    self.setup_socks_proxy()
        
        return session
    
    def setup_socks_proxy(self):
        """Setup SOCKS5 proxy at socket level"""
        try:
            socks.set_default_proxy(
                socks.SOCKS5,
                self.proxy_settings['host'],
                int(self.proxy_settings['port']),
                username=self.proxy_settings.get('username'),
                password=self.proxy_settings.get('password')
            )
            socket.socket = socks.socksocket
            return True
        except Exception as e:
            print(f"Error setting up SOCKS proxy: {e}")
            return False
    
    def test_connection(self):
        """Test proxy connection"""
        try:
            if not self.proxy_settings['enabled']:
                return False, "Proxy is not enabled"
            
            if not self.proxy_settings['host'] or not self.proxy_settings['port']:
                return False, "Proxy host or port not configured"
            
            session = self.get_session()
            
            # Test URLs
            test_urls = [
                'http://httpbin.org/ip',
                'http://api.ipify.org?format=json',
                'https://checkip.amazonaws.com'
            ]
            
            for test_url in test_urls:
                try:
                    print(f"Testing proxy with {test_url}")
                    response = session.get(test_url, timeout=10)
                    
                    if response.status_code == 200:
                        try:
                            if 'json' in test_url:
                                ip_data = response.json()
                                ip = ip_data.get('ip', ip_data.get('origin', 'Unknown'))
                            else:
                                ip = response.text.strip()
                            
                            return True, f"✅ Connection successful!\nYour IP: {ip}\nProxy: {self.proxy_settings['host']}:{self.proxy_settings['port']}"
                        except:
                            return True, f"✅ Connection successful! Status: {response.status_code}"
                except requests.exceptions.Timeout:
                    continue
                except Exception as e:
                    continue
            
            return False, "❌ Connection failed: All test URLs failed"
            
        except Exception as e:
            return False, f"❌ Connection error: {str(e)}"
    
    def change_ip_if_needed(self):
        """Change IP if change_ip_url is configured"""
        if not self.proxy_settings['enabled']:
            return True, "Proxy not enabled"
        
        if not self.proxy_settings.get('change_ip_url'):
            return True, "No IP change URL configured"
        
        try:
            session = self.get_session()
            change_url = self.proxy_settings['change_ip_url']
            
            print(f"Changing IP via: {change_url}")
            response = session.get(change_url, timeout=30)
            
            if response.status_code == 200:
                time.sleep(3)  # Wait for IP change
                return True, "✅ IP changed successfully"
            else:
                return False, f"❌ IP change failed: Status {response.status_code}"
                
        except Exception as e:
            return False, f"❌ IP change error: {str(e)}"
    
    def get_current_settings(self):
        """Get current proxy settings"""
        return self.proxy_settings.copy()
    
    def is_enabled(self):
        """Check if proxy is enabled"""
        return self.proxy_settings['enabled'] and bool(self.proxy_settings['host'])
