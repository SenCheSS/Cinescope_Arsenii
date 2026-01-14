import random

import pytest
from datetime import datetime
import uuid
from typing import Dict, Any
from db_helpers import MovieDBHelper
from decimal import Decimal
from db_models.movies import MovieDBModel


class TestMovieOperations:
    """Тесты для операций с фильмами"""

    def test_movie_does_not_exist_before_creation(
            self,
            movie_helper: MovieDBHelper,
            sample_movie_data: Dict[str, Any]
    ):
        """Проверка, что до создания фильма его нет в БД"""
        # ARRANGE
        movie_id = sample_movie_data['id']
        movie_name = sample_movie_data['name']

        # Проверка отсутствия по ID
        assert movie_helper.get_movie_by_id(movie_id) is None
        # Проверка отсутствия по имени
        assert movie_helper.get_movie_by_name(movie_name) is None
        # Проверка методов exists
        assert not movie_helper.movie_exists(movie_id)
        assert not movie_helper.movie_exists_by_name(movie_name)

    def test_movie_full_lifecycle_crud_simple(
            self,
            movie_helper: MovieDBHelper,
            sample_movie_data: Dict[str, Any]
    ):
        """
        Упрощенная версия теста CRUD
        """
        # ARRANGE
        movie_id = sample_movie_data['id']

        # ==================== CREATE ====================
        assert movie_helper.get_movie_by_id(movie_id) is None

        created_movie = movie_helper.create_movie(sample_movie_data)
        assert created_movie is not None

        # ==================== READ ====================
        retrieved = movie_helper.get_movie_by_id(movie_id)
        assert retrieved is not None

        # Сравниваем значения (price преобразуем к int для сравнения)
        assert retrieved.id == sample_movie_data['id']
        assert retrieved.name == sample_movie_data['name']
        assert int(retrieved.price) == int(sample_movie_data['price'])  # Ключевое изменение!
        assert abs(retrieved.rating - sample_movie_data['rating']) < 0.001
        assert retrieved.location == sample_movie_data['location']
        assert retrieved.published == sample_movie_data['published']
        assert retrieved.genre_id == sample_movie_data['genre_id']

        # ==================== UPDATE ====================
        update_data = {
            'price': 99,
            'rating': 9.5,
            'published': False,
            'location': 'SPB' if sample_movie_data['location'] == 'MSK' else 'MSK'
        }

        updated = movie_helper.update_movie(movie_id, update_data)
        assert updated is not None

        # ==================== DELETE ====================
        assert movie_helper.delete_movie(movie_id) is True
        assert movie_helper.get_movie_by_id(movie_id) is None