from pydantic import BaseModel, Field
import json


# 1. Создание модели
class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    in_stock: bool = Field(default=True)

    def __str__(self):
        return f"{self.name} - {self.price:.2f} руб. ({'В наличии' if self.in_stock else 'Нет в наличии'})"


def main():
    print("=" * 60)
    print("РАБОТА С МОДЕЛЬЮ PRODUCT")
    print("=" * 60)

    # Создание объекта
    print("\n1. СОЗДАНИЕ ОБЪЕКТА PRODUCT:")
    product = Product(name="Смартфон iPhone", price=99999.99, in_stock=False)
    print(f"   Создан: {product}")

    # Сериализация в JSON
    print("\n2. СЕРИАЛИЗАЦИЯ В JSON:")
    json_str = product.model_dump_json(indent=2)
    print(f"   JSON строка:\n{json_str}")

    # Десериализация из JSON
    print("\n3. ДЕСЕРИАЛИЗАЦИЯ ИЗ JSON:")

    # Новый JSON для десериализации
    new_json = '{"name": "Планшет Samsung", "price": 45999.50, "in_stock": true}'
    new_product = Product.model_validate_json(new_json)
    print(f"   Из JSON: {new_json}")
    print(f"   Получен объект: {new_product}")

    # Вывод на экран
    print("\n4. ВЫВОД НА ЭКРАН РАЗНЫМИ СПОСОБАМИ:")
    print(f"   a) Простой вывод: {product}")
    print(f"   b) Доступ к полям: Название={product.name}, Цена={product.price}")
    print(f"   c) Как словарь: {product.model_dump()}")

    # Сериализация/десериализация коллекции
    print("\n5. РАБОТА С КОЛЛЕКЦИЕЙ ПРОДУКТОВ:")
    products = [
        Product(name="Ноутбук", price=75000.00, in_stock=True),
        Product(name="Монитор", price=25000.00, in_stock=True),
        Product(name="Мышь", price=1500.00, in_stock=False)
    ]

    # Сериализуем список в JSON
    products_json = json.dumps([p.model_dump() for p in products], indent=2)
    print(f"   Список продуктов в JSON:\n{products_json}")

    # Восстанавливаем из JSON
    restored_products = [Product(**item) for item in json.loads(products_json)]
    print(f"\n   Восстановлено {len(restored_products)} продуктов:")
    for p in restored_products:
        print(f"   • {p}")


if __name__ == "__main__":
    main()
    print("\n" + "=" * 60)
    print("✅ ЗАДАЧА ВЫПОЛНЕНА!")
    print("=" * 60)