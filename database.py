from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# This creates a database file called database.db in your project folder
DATABASE_URL = 'sqlite:///./database.db'

# Engine = the connection to your database
engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False}
)

# Base = the parent class all your table models inherit from
Base = declarative_base()

# SessionLocal = a factory that creates database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# This is your table — each attribute = one column
class GeneratedDoc(Base):
    __tablename__ = 'generated_docs'

    id           = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    doc_type     = Column(String)
    content      = Column(Text)
    tokens_used  = Column(Integer)
    created_at   = Column(DateTime, default=datetime.utcnow)


# This function creates the table in the database file if it doesn't exist
def create_tables():
    Base.metadata.create_all(bind=engine)


# This function gives us a database session to use in endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()