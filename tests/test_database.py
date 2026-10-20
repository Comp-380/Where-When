from sqlalchemy import create_engine, inspect, text

from backend.database import initialize_database


def test_upgrade_preserves_existing_users(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(100),
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN NOT NULL,
                is_verified BOOLEAN NOT NULL,
                created_at DATETIME NOT NULL
            )
        """))
        connection.execute(text("""
            INSERT INTO users VALUES (
                1, 'existing', 'existing@example.com', NULL, 'stored-hash',
                1, 1, '2026-10-19 00:00:00'
            )
        """))

    initialize_database(engine)
    initialize_database(engine)

    assert "avatar_url" in {c["name"] for c in inspect(engine).get_columns("users")}
    with engine.connect() as connection:
        user = connection.execute(text(
            "SELECT username, hashed_password, is_verified, avatar_url FROM users"
        )).one()
        assert tuple(user) == ("existing", "stored-hash", 1, None)
    engine.dispose()
