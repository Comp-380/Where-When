import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_FILE = os.getenv("DATABASE_FILE", "users.db")
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def initialize_database(db_engine=engine):
    """Create tables and upgrade databases created before avatar support."""
    from backend import models  # Register models before creating tables.

    Base.metadata.create_all(bind=db_engine)
    columns = {column["name"] for column in inspect(db_engine).get_columns("users")}
    if "avatar_url" not in columns:
        with db_engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255)"))


def get_db():
    """Dependency that yields a database session and ensures it closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
