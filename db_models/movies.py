from sqlalchemy import Column, String,Integer, Float, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from typing import Dict, Any

Base = declarative_base()


class MovieDBModel(Base):
    """Модель фильма"""
    __tablename__ = 'movies'

    id = Column(String, primary_key=True)  # text в БД
    name = Column(String)  # text в БД
    price = Column(Float)
    description = Column(String)
    image_url = Column(String)
    location = Column(String)
    published = Column(Boolean)
    rating = Column(Float)
    genre_id = Column(String)
    created_at = Column(DateTime)  # timestamp в БД


    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'image_url': self.image_url,
            'location': self.location,
            'published': self.published,
            'rating': self.rating,
            'genre_id': self.genre_id,
            'created_at': self.created_at
        }

    def __repr__(self):
        return f"<Movie(id='{self.id}', name='{self.name}', price={self.price})>"
