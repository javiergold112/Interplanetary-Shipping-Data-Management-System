# migrations
import os

print(os.getcwd())
os.chdir('/home/python_user/src')

migrations = 'alembic revision --autogenerate -m "New Migration"'
migrate = 'alembic upgrade head'
os.system(migrations)
os.system(migrate)
