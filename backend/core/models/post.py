from sqlalchemy import Integer, Column, String, Boolean, ForeignKey

from .base import Base


class Post(Base):
    __tablename__ = 'Post'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    content = Column(String(255))
    is_published = Column(Boolean, default=False)
    author_id = Column(Integer, ForeignKey('User.id'))
    likes = Column(Integer)
