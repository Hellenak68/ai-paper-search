from sqlalchemy.orm import Session
from app.core.database import engine, Base
from app.models import User, Project, File
from app.core.security import get_password_hash


def init_db():
    """Initialize database with tables and default data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create default admin user if not exists
    db = Session(bind=engine)
    try:
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created: admin@example.com / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
