"""
Database manager for the application
"""

import os
import sys
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from models.account import Base, Account

class DatabaseManager:
    """Manager for database operations"""
    
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)
        self.engine = None
        self.Session = None
        self.db_path = self._get_db_path()
        print(f"📁 Database path: {self.db_path}")
        self._init_database()
    
    def _get_db_path(self):
        """Get the absolute path to the database file"""
        db_url = self.config.get('database', {}).get('url', 'sqlite:///cloud_accounts.db')
        
        if 'sqlite:///' in db_url:
            db_path = db_url.replace('sqlite:///', '')
            
            if not os.path.isabs(db_path):
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                db_path = os.path.join(project_root, db_path)
            
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            return db_path
        
        return None
    
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_in_root = os.path.join(project_root, 'config.yaml')
        
        if os.path.exists(config_in_root):
            with open(config_in_root, 'r') as f:
                return yaml.safe_load(f)
        
        print("⚠️ Config file not found, using defaults")
        return {'database': {'url': 'sqlite:///cloud_accounts.db'}}
    
    def _init_database(self):
        """Initialize database connection and create tables"""
        db_url = f'sqlite:///{self.db_path}'
        print(f"🔗 Database URL: {db_url}")
        
        self.engine = create_engine(
            db_url,
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
            echo=True
        )
        
        print("🗄️ Creating tables...")
        Base.metadata.create_all(self.engine)
        
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
        if os.path.exists(self.db_path):
            file_size = os.path.getsize(self.db_path)
            print(f"✅ Database created: {self.db_path} ({file_size} bytes)")
        else:
            print(f"❌ Database file not found at: {self.db_path}")
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def save_account(self, account_data):
        """Save account to database"""
        session = self.get_session()
        try:
            account = Account.from_dict(account_data)
            session.add(account)
            session.commit()
            session.refresh(account)
            return account.id
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving account: {e}")
            raise e
        finally:
            session.close()
    
    def get_all_accounts(self, provider=None):
        """Get all accounts, optionally filtered by provider"""
        session = self.get_session()
        try:
            query = session.query(Account)
            if provider:
                query = query.filter(Account.provider == provider)
            return query.order_by(Account.created_at.desc()).all()
        finally:
            session.close()
    
    def delete_account(self, account_id):
        """Delete account by ID"""
        session = self.get_session()
        try:
            account = session.query(Account).filter(Account.id == account_id).first()
            if account:
                session.delete(account)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"❌ Error deleting account: {e}")
            return False
        finally:
            session.close()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
