import sys
import os
import traceback

print('='*60)
print('CLOUD ACCOUNT MANAGER - SIMPLE START')
print('='*60)

# обавляем пути
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)
sys.path.insert(0, os.path.join(project_path, 'database'))
sys.path.insert(0, os.path.join(project_path, 'models'))
sys.path.insert(0, os.path.join(project_path, 'ui'))

print(f'Project: {project_path}')
print(f'sys.path:')
for p in sys.path[:5]:
    print(f'  {p}')

try:
    # мпорты
    import yaml
    from PyQt6.QtWidgets import QApplication
    from database.database import DatabaseManager
    from ui.main_window import MainWindow
    
    print('✅ се импорты успешны!')
    
    # агрузка конфигурации
    config_path = os.path.join(project_path, 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f'✅ онфиг загружен: {config_path}')
    else:
        config = {'database': {'url': 'sqlite:///cloud_accounts.db'}}
        print('⚠️  спользуем конфиг по умолчанию')
    
    # нициализация 
    db_url = config.get('database', {}).get('url', 'sqlite:///cloud_accounts.db')
    print(f'📁 Database URL: {db_url}')
    
    db_manager = DatabaseManager(db_url)
    db_manager.init_db()
    print('✅ аза данных инициализирована')
    
    # апуск приложения
    app = QApplication(sys.argv)
    app.setApplicationName('Cloud Account Manager')
    
    window = MainWindow(db_manager)
    window.show()
    
    print('✅ риложение запущено')
    sys.exit(app.exec())
    
except Exception as e:
    print(f'❌ шибка: {e}')
    traceback.print_exc()
    input('ажмите Enter для выхода...')
