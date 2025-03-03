# migrations
import os
migrations = 'alembic revision --autogenerate -m "New Migration"'
migrate = 'alembic upgrade head'
os.system(migrations)
os.system(migrate)
