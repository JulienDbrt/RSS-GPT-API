from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum, ForeignKey, Table
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

import enum

class SourceStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DELETED = "deleted"

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    max_items = Column(Integer, nullable=False, default=10)
    status = Column(Enum(SourceStatusEnum), nullable=False, default=SourceStatusEnum.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    articles = relationship("Article", back_populates="source")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    published_at = Column(DateTime)
    content = Column(Text)
    summary = Column(Text)
    keywords = Column(Text)
    language = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    source = relationship("Source", back_populates="articles")
    tags = relationship("Tag", secondary="article_tags", back_populates="articles")
    history = relationship("History", back_populates="article", uselist=False)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    articles = relationship("Article", secondary="article_tags", back_populates="tags")

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow)
    article = relationship("Article", back_populates="history")