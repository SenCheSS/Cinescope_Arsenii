from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from db_models.user import UserDBModel
from db_models.movies import MovieDBModel


class DBHelper:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    """Класс с методами для работы с БД в тестах"""

    def create_test_user(self, user_data: dict) -> UserDBModel:
        """Создает тестового пользователя"""
        user = UserDBModel(**user_data)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def get_user_by_id(self, user_id: str):
        """Получает пользователя по ID"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    def get_user_by_email(self, email: str):
        """Получает пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).first()

    def get_movie_by_name(self, name: str):
        """Получает фильм по названию"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.name == name).first()

    def user_exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).count() > 0

    def delete_user(self, user: UserDBModel):
        """Удаляет пользователя"""
        self.db_session.delete(user)
        self.db_session.commit()

    def cleanup_test_data(self, objects_to_delete: list):
        """Очищает тестовые данные"""
        for obj in objects_to_delete:
            if obj:
                self.db_session.delete(obj)
        self.db_session.commit()

class MovieDBHelper:
    """Класс-хелпер для работы с фильмами в БД"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_movie(self, movie_data: Dict[str, Any]) -> MovieDBModel:
        """Создаем новый фильм в БД"""
        if 'created_at' not in movie_data:
            movie_data['created_at'] = datetime.now()
        movie = MovieDBModel(**movie_data)
        self.db_session.add(movie)
        self.db_session.commit()
        self.db_session.refresh(movie)
        return movie

    def create_movie_batch(self, movies_data: List[Dict[str, Any]]) -> List[MovieDBModel]:
        """Создает несколько фильмов сразу"""
        movies = []
        for data in movies_data:
            if 'created_at' not in data:
                data['created_at'] = datetime.now()
            movie = MovieDBModel(**data)
            movies.append(movie)
        self.db_session.add_all(movies)
        self.db_session.commit()

        for movie in movies:
            self.db_session.refresh(movie)
        return movies

    def get_movie_by_id(self, movie_id: str) -> Optional[MovieDBModel]:
        """Получает фильм по ID"""
        return self.db_session.query(MovieDBModel)\
            .filter(MovieDBModel.id == movie_id)\
            .first()

    def get_movie_by_name(self, name: str) -> Optional[MovieDBModel]:
        """Получаем фильм по названию(точное совпадение)"""

        return self.db_session.query(MovieDBModel)\
            .filter(MovieDBModel.name == name)\
            .first()

    def search_movies_by_name(self, search_term: str, limit: int = 10) -> List[MovieDBModel]:
        """Ищет фильм по частичному совпадению"""

        return self.db_session.query(MovieDBModel)\
            .filter(MovieDBModel.name.ilike(f'%{search_term}%'))\
            .limit(limit).all()

    def get_movies_by_genre(self, genre_id: str,
                            published_only: bool = True) -> List[MovieDBModel]:
        """Получает фильмы по жанру"""
        query = self.db_session.query(MovieDBModel) \
            .filter(MovieDBModel.genre_id == genre_id)
        if published_only:
            query = query.filter(MovieDBModel.published == True)
        return query.order_by(desc(MovieDBModel.rating)).all()

    def get_published_movies(self, limit: int = 50) -> List[MovieDBModel]:
        """Получает опубликованные фильмы"""

        return self.db_session.query(MovieDBModel) \
            .filter(MovieDBModel.published == True) \
            .order_by(desc(MovieDBModel.created_at)) \
            .limit(limit).all()

    def get_movies_by_price_range(self, min_price: float,
                                  max_price: float,
                                  published_only: bool = True) -> List[MovieDBModel]:
        """Получает фильмы в диапазоне цен"""
        query = self.db_session.query(MovieDBModel) \
            .filter(MovieDBModel.price.between(min_price, max_price))
        if published_only:
            query = query.filter(MovieDBModel.published == True)
        return query.order_by(MovieDBModel.price).all()

    def get_movies_by_rating(self, min_rating: float = 0.0,
                             max_rating: float = 10.0,
                             published_only: bool = True) -> List[MovieDBModel]:
        """Получает фильмы по рейтингу"""
        query = self.db_session.query(MovieDBModel)\
            .filter(MovieDBModel.rating.between(min_rating, max_rating))

        if published_only:
            query = query.filter(MovieDBModel.published == True)
        return query.order_by(desc(MovieDBModel.rating)).all()

    def get_all_movies(self, limit: int = 100) -> List[MovieDBModel]:
        """Получает все фильмы"""
        return self.db_session.query(MovieDBModel)\
            .order_by(desc(MovieDBModel.created_at))\
            .limit(limit).all()

    def get_movies_by_location(self, location: str,
                               published_only: bool = True) -> List[MovieDBModel]:
        """Получает фильмы по месту показа"""
        query = self.db_session.query(MovieDBModel)\
            .filter(MovieDBModel.location == location)
        if published_only:
            query = query.filter(MovieDBModel.published == True)
        return query.order_by(MovieDBModel.name).all()

        # ========== UPDATE OPERATIONS ==========

    def update_movie(self, movie_id: str,
                     update_data: Dict[str, Any]) -> Optional[MovieDBModel]:
        """Обновляет данные фильма"""
        movie = self.get_movie_by_id(movie_id)
        if not movie:
            return None

        # Обновляем поля
        for key, value in update_data.items():
            if hasattr(movie, key):
                setattr(movie, key, value)
        movie.updated_at = datetime.now()
        self.db_session.commit()
        self.db_session.refresh(movie)
        return movie

    def publish_movie(self, movie_id: str) -> Optional[MovieDBModel]:
        """Публикует фильм (устанавливает published = True)"""
        return self.update_movie(movie_id, {'published': True})

    def unpublish_movie(self, movie_id: str) -> Optional[MovieDBModel]:
        """Снимает фильм с публикации (устанавливает published = False)"""
        return self.update_movie(movie_id, {'published': False})

    def update_movie_rating(self, movie_id: str,
                            new_rating: float) -> Optional[MovieDBModel]:
        """Обновляет рейтинг фильма"""
        return self.update_movie(movie_id, {'rating': new_rating})

    # ========== DELETE OPERATIONS ==========

    def delete_movie(self, movie_id: str) -> bool:
        """Удаляет фильм по ID"""

        movie = self.get_movie_by_id(movie_id)
        if not movie:
            return False
        self.db_session.delete(movie)
        self.db_session.commit()
        return True

    # ========== UTILITY METHODS ==========

    def movie_exists(self, movie_id: str) -> bool:
        """Проверяет существование фильма по ID"""
        return self.db_session.query(MovieDBModel) \
            .filter(MovieDBModel.id == movie_id) \
            .count() > 0

    def movie_exists_by_name(self, name: str) -> bool:
        """Проверяет существование фильма по названию"""
        return self.db_session.query(MovieDBModel) \
            .filter(MovieDBModel.name == name) \
            .count() > 0

    def get_movies_count(self, published_only: bool = False) -> int:
        """Получает общее количество фильмов"""
        query = self.db_session.query(MovieDBModel)

        if published_only:
            query = query.filter(MovieDBModel.published == True)
        return query.count()
