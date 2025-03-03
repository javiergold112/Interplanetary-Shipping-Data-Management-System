from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager
from config import PostgresConfig

# Generate Database URL
DATABASE_URL = f"postgresql://{PostgresConfig.DATABASE_USERNAME}:{PostgresConfig.DATABASE_PASSWORD}@{PostgresConfig.DATABASE_HOSTNAME}:{PostgresConfig.DATABASE_PORT}/{PostgresConfig.DATABASE_NAME}"

# Create Database Engine
engine = create_engine(
    DATABASE_URL,
    echo=PostgresConfig.DATABASE_DEBUG_MODE,
    future=True,
    pool_size=PostgresConfig.POOL_SIZE,
    max_overflow=PostgresConfig.MAX_OVERFLOW,
)

# Create session factory
Session = sessionmaker(engine, expire_on_commit=False)


# Function to get a SQLAlchemy session
@contextmanager
def get_db_session():
    """Provide a SQLAlchemy session."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass