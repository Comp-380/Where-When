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
    """Create tables and upgrade databases created before avatar/profile support."""
    from backend import models  # Register models before creating tables
    Base.metadata.create_all(bind=db_engine)
    
    inspector = inspect(db_engine)
    columns = {column["name"] for column in inspector.get_columns("users")}
    profile_columns = {
        "avatar_url": "VARCHAR(255)",
        "display_name": "VARCHAR(100)",
        "profile_picture": "VARCHAR(255)",
        "general_location": "VARCHAR(100)",
        "activity_interests": "VARCHAR(255)",
        "bio": "VARCHAR(500)",
    }
    with db_engine.begin() as connection:
        for col_name, col_type in profile_columns.items():
            if col_name not in columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))


def get_db():
    """Dependency that yields a database session and ensures it closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()