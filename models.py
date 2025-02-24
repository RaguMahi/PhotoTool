from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class ImageLibrary(Base):
    __tablename__ = 'image_library'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    category = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    file_path = sa.Column(sa.String, nullable=False)
    processing_params = sa.Column(sa.JSON)  # Store the parameters used for processing

class TemplateLibrary(Base):
    __tablename__ = 'template_library'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    file_path = sa.Column(sa.String, nullable=False)
    default_params = sa.Column(sa.JSON)  # Store default scale and position parameters

class JobTemplate(Base):
    __tablename__ = 'job_templates'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    template_id = sa.Column(sa.Integer, sa.ForeignKey('template_library.id'))
    screenshot_path = sa.Column(sa.String, nullable=False)
    alignment_params = sa.Column(sa.JSON)  # Store scale and position parameters
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = sa.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()