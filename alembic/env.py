from logging.config import fileConfig
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool
from alembic import context

from core.database import Base

# Import ALL model modules so Alembic can detect them
from models.user import User
from models.test_category import TestCategory
from models.question import Question
from models.question_result import QuestionResult
from models.test_attempt import TestAttempt
from models.survey_option import SurveyOption


# Load .env
load_dotenv()

# Alembic Config object
config = context.config

# Logging config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your models here and set target_metadata
# from your_app.models import Base
# target_metadata = Base.metadata
target_metadata = Base.metadata

# Read DB credentials from environment
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")  # must be string
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Build database URL
database_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
print("Using DATABASE URL:", database_url)

def run_migrations_offline():
    """Run migrations in offline mode."""
    context.configure(url=database_url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in online mode."""
    connectable = create_engine(database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
