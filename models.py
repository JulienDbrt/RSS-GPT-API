import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class SourceStatusEnum(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=False, unique=True)
    status = Column(Enum(SourceStatusEnum), default=SourceStatusEnum.ACTIVE, nullable=False)
    max_items = Column(Integer, default=10)
    last_fetched_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    title = Column(String(1024), nullable=False)
    url = Column(String(2048), nullable=False, unique=True)
    published_at = Column(DateTime, index=True)
    content = Column(Text)
    summary = Column(Text)
    keywords = Column(String(255))
    language = Column(String(10))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    source = relationship("Source", back_populates="articles")