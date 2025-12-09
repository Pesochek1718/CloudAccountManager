"""
Account model for storing cloud provider accounts
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base

# Создаем Base  определения класса
Base = declarative_base()

class Account(Base):
    """Account model for all cloud providers"""
    
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    
    # Common fields for all providers
    provider = Column(String(50), nullable=False)  # AWS, DigitalOcean, Linode, Azure
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(Text)
    
    # AWS specific fields
    password = Column(String(255))  # For AWS, DigitalOcean, Linode, Azure
    mfa_secret = Column(String(255))
    access_key = Column(String(255))
    secret_key = Column(String(255))
    region = Column(String(100))  # Only for AWS
    country = Column(String(100))  # Registration country
    quota_used = Column(Integer, default=0)  # For AWS quota tracking
    quota_limit = Column(Integer, default=0)  # For AWS quota limit
    
    # DigitalOcean specific fields
    email_password = Column(String(255))  # Optional email password
    do_password = Column(String(255))
    do_2fa_secret = Column(String(255))
    limits = Column(String(255))  # e.g., "10 droplets, $100/month"
    
    # Linode specific fields
    linode_login = Column(String(255))
    linode_password = Column(String(255))
    linode_2fa_secret = Column(String(255))
    api_key = Column(String(255))
    payment_method = Column(String(50))  # Card, PayPal
    linode_country = Column(String(100))
    
    # Azure specific fields
    azure_password = Column(String(255))
    azure_2fa_secret = Column(String(255))
    subscription = Column(String(50))  # Pay as You Go, Free Trial 200$
    azure_country = Column(String(100))
    
    # Status fields
    is_active = Column(Boolean, default=True)
    last_check = Column(DateTime)
    check_result = Column(String(50))  # Success, Failed, Warning
    
    def __repr__(self):
        return f"<Account(provider='{self.provider}', email='{self.email}')>"
    
    def to_dict(self):
        """Convert account to dictionary"""
        data = {
            'id': self.id,
            'provider': self.provider,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'comment': self.comment,
            'country': self.country,
            'is_active': self.is_active,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'check_result': self.check_result
        }
        
        # Provider specific fields
        if self.provider == 'AWS':
            data.update({
                'password': self.password,
                'mfa_secret': self.mfa_secret,
                'access_key': self.access_key,
                'secret_key': self.secret_key,
                'region': self.region,
                'quota_used': self.quota_used,
                'quota_limit': self.quota_limit
            })
        elif self.provider == 'DigitalOcean':
            data.update({
                'email_password': self.email_password,
                'do_password': self.do_password,
                'do_2fa_secret': self.do_2fa_secret,
                'limits': self.limits,
                'country': self.country  # Override common country
            })
        elif self.provider == 'Linode':
            data.update({
                'email_password': self.email_password,
                'linode_login': self.linode_login,
                'linode_password': self.linode_password,
                'linode_2fa_secret': self.linode_2fa_secret,
                'api_key': self.api_key,
                'payment_method': self.payment_method,
                'country': self.linode_country
            })
        elif self.provider == 'Azure':
            data.update({
                'azure_password': self.azure_password,
                'azure_2fa_secret': self.azure_2fa_secret,
                'subscription': self.subscription,
                'country': self.azure_country
            })
        
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create account from dictionary"""
        account = cls()
        account.provider = data.get('provider', '')
        account.email = data.get('email', '')
        account.comment = data.get('comment', '')
        
        if account.provider == 'AWS':
            account.password = data.get('password', '')
            account.mfa_secret = data.get('mfa_secret', '')
            account.access_key = data.get('access_key', '')
            account.secret_key = data.get('secret_key', '')
            account.region = data.get('region', '')
            account.country = data.get('country', '')
        elif account.provider == 'DigitalOcean':
            account.email_password = data.get('email_password', '')
            account.do_password = data.get('do_password', '')
            account.do_2fa_secret = data.get('2fa_secret', '')
            account.limits = data.get('limits', '')
            account.country = data.get('country', '')
            account.payment_method = data.get('payment_method', '')
        elif account.provider == 'Linode':
            account.email_password = data.get('email_password', '')
            account.linode_login = data.get('linode_login', '')
            account.linode_password = data.get('linode_password', '')
            account.linode_2fa_secret = data.get('2fa_secret', '')
            account.api_key = data.get('api_key', '')
            account.payment_method = data.get('payment_method', 'Card')
            account.linode_country = data.get('country', '')
        elif account.provider == 'Azure':
            account.azure_password = data.get('azure_password', '')
            account.azure_2fa_secret = data.get('2fa_secret', '')
            account.subscription = data.get('subscription', 'Pay as You Go')
            account.azure_country = data.get('country', '')
        
        return account
