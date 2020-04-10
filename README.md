# Web-shop backend api using rest api.

## Run
`$ docker-compose up`

## Описание архитектуры
Сервер запускается на `flask`. `Flask` вызывает создание класса `AppWrapper`, который умеет общаться с классом `DB`, который умеет напрямую общаться с `postgres` базой через библиотеку `psycopg2`.<br>
Классом товара является класс `Product`, который содержит `name` (строка, имя товара), `category` (строка, категория товара), `code` (строка, код товара).

## Описание API

Дата в методах передается в `json` формате, запросы возвращают данные в формате `json`.

| метод                          | тип      | описание                                                      | параметры в теле           | Пример                                                                                                    |
|--------------------------------|----------|---------------------------------------------------------------|----------------------------|-----------------------------------------------------------------------------------------------------------|
| `/add_product`                 | `POST`   | добавляет товар с указанными `name`, `code`, `category`       | `name`, `code`, `category` | `curl -d '{"name": "supercar", "code": "1", "category": "cars"}' "0.0.0.0:5000/add_product"`              |
| `/products`                    | `GET`    | возвращает список товаров                                     |                            | `curl "0.0.0.0:5000/products"`                                                                            |
| `/product_info/<product_name>` | `GET`    | возвращает информацию о товаре                                |                            | `curl "0.0.0.0:5000/product_info/supercar`                                                                |
| `/remove_product`              | `DELETE` | удаляет товар с указанными `name`                             | `name`                     | `curl -X DELETE -d '{"name": "supercar"}' 0.0.0.0:5000/remove_product`                                    |
| `/edit_product`                | `PUT`    | редактирует поля `code` и `category` у товара с данным `name` | `name`, `code`, `category` | `curl -X PUT -d '{"name": "supercar", "code": "2", "category": "fast_cars"}' "0.0.0.0:5000/edit_product"` |
