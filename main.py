import json
import os
import sys

# Ensure python finds the src folder
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_engine import DataEngine
from src.math_core import AnalyticsEngine
from src.ui_modern import ModernUI

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'settings.json')
DB_PATH = os.path.join(BASE_DIR, 'database', 'academic_data.db')
ICON_PATH = os.path.join(BASE_DIR, 'assets', 'app_icon.ico')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def main():
    try:
        config = load_config()
        
        # Initialize Engines
        db = DataEngine(DB_PATH)
        math_eng = AnalyticsEngine(config['grading_weights'])
        
        # Secure Auth Logic
        def authenticate(u, p):
            return u == config['security']['admin_user'] and p == config['security']['admin_hash']

        # Launch System
        app = ModernUI(authenticate, db, math_eng, ICON_PATH)
        app.mainloop()
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()