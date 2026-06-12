import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from backend.app import db

if __name__ == '__main__':
    print('Initializing DB and seeding sample data...')
    db.init_db()
    print('Done')
