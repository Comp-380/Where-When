import os
import secrets
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
    """Create tables and upgrade databases created before address/group invite/poll deletion support."""
    from backend import models  # Register models before creating tables
    Base.metadata.create_all(bind=db_engine)

    inspector = inspect(db_engine)
    tables = inspector.get_table_names()
    
    if "users" in tables:
        columns = {column["name"] for column in inspector.get_columns("users")}
        profile_columns = {
            "avatar_url": "VARCHAR(255)",
            "display_name": "VARCHAR(100)",
            "profile_picture": "VARCHAR(255)",
            "general_location": "VARCHAR(100)",
            "activity_interests": "VARCHAR(255)",
            "bio": "VARCHAR(500)",
            "street_address": "VARCHAR(255)",
            "state": "VARCHAR(2)",
            "zip_code": "VARCHAR(10)",
            "max_travel_distance": "INTEGER DEFAULT 25",  # <--- Added
        }
        with db_engine.begin() as connection:
            for col_name, col_type in profile_columns.items():
                if col_name not in columns:
                    connection.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))

    if "groups" in tables:
        columns = {column["name"] for column in inspector.get_columns("groups")}
        if "invite_code" not in columns:
            with db_engine.begin() as connection:
                connection.execute(text("ALTER TABLE groups ADD COLUMN invite_code VARCHAR(32)"))
        if "group_photo_url" not in columns:
            with db_engine.begin() as connection:
                connection.execute(text("ALTER TABLE groups ADD COLUMN group_photo_url VARCHAR(255)"))

        SessionClass = sessionmaker(bind=db_engine)
        with SessionClass() as session:
            try:
                groups_without_code = session.query(models.Group).filter(
                    (models.Group.invite_code.is_(None)) | (models.Group.invite_code == "")
                ).all()
                for g in groups_without_code:
                    g.invite_code = models.generate_invite_code()
                session.commit()
            except Exception:
                session.rollback()

    if "hangout_polls" in tables:
        poll_columns = {column["name"] for column in inspector.get_columns("hangout_polls")}
        if "is_deleted" not in poll_columns:
            with db_engine.begin() as connection:
                connection.execute(text("ALTER TABLE hangout_polls ADD COLUMN is_deleted BOOLEAN DEFAULT 0"))


def get_db():
    """Dependency that yields a database session and ensures it closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()