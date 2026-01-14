import datetime
import random
import string
from string import digits
from typing import Optional

from faker import Faker
faker = Faker()

class DataGenerator:

    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f'kek{random_string}@gmail.com'

    @staticmethod
    def generate_random_name():
        return f'{faker.first_name()} {faker.last_name()}'

    @staticmethod
    def generate_random_password():
        """
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        """

        # Гарантируем наличие хотя бы одной буквы и одной цифры
        letters = random.choice(string.ascii_letters) # Одна буква
        digits = random.choice(string.digits) # Одна цифра

        # Дополняем пароль случайными символами из допустимого набора
        special_chars = '?@#$%^&*|:'
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18) # Остальная длина пароля
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        # Перемешиваем пароль для рандомизации
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    def generate_random_string(length=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    @staticmethod
    def generate_movie_data():
        """Генерация данных для создания фильма"""
        valid_genre_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        return {
            "name": f"Фильм {DataGenerator.generate_random_string(6)}",
            "imageUrl": f"https://example.com/movie{random.randint(1, 1000)}.jpg",
            "price": random.randint(100, 1000),
            "description": f"Описание фильма {faker.text(max_nb_chars=50)}",
            "location": random.choice(['SPB', 'MSK']),
            "published": random.choice([True, False]),
            "genreId": random.choice(valid_genre_ids)
        }

    @staticmethod
    def generate_movie_update_data():
        """Генерация данных для обновления фильма"""
        valid_genre_ids = [1, 2, 3, 4, 5, 6, 7, 8]

        return {
            "name": f"Обновленный фильм {DataGenerator.generate_random_string(6)}",
            "price": random.randint(100, 1000),
            "description": f"Обновленное описание {faker.text(max_nb_chars=30)}",
            "location": random.choice(['SPB', 'MSK']),
            "published": random.choice([True, False]),
            "genreId": random.choice(valid_genre_ids)
        }

    @staticmethod
    def generate_user_data() -> dict:
        """Генерирует данные для тестового пользователя"""
        from uuid import uuid4

        return {
            'id': f'{uuid4()}',  # генерируем UUID как строку
            'email': DataGenerator.generate_random_email(),
            'full_name': DataGenerator.generate_random_name(),
            'password': DataGenerator.generate_random_password(),
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
            'verified': False,
            'banned': False,
            'roles': '{USER}'
        }

    @staticmethod
    def generate_random_int(length: int = 6) -> int:
        """
        Генерирует случайное целое число с заданным количеством цифр

        Args:
            length: Количество цифр в числе (по умолчанию 6)

        Returns:
            int: Случайное целое число

        Examples:
            generate_random_int(6) -> 123456
            generate_random_int(10) -> 1234567890
        """
        if length <= 0:
            return 0

        # Генерируем первую цифру (не может быть 0, если длина > 1)
        if length == 1:
            first_digit = random.randint(0, 9)
        else:
            first_digit = random.randint(1, 9)  # Первая цифра не может быть 0

        # Преобразуем первую цифру в строку
        result = str(first_digit)

        # Генерируем остальные цифры
        for _ in range(length - 1):
            result += str(random.randint(0, 9))

        return int(result)