import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

def get_book_data(book_url: str) -> dict:
    """
    Получает данные о книге со страницы каталога сайта Books to Scrape.

    Функция получает HTML-страницу книги, извлекает и структурирует всю доступную
    информацию о книге, включая основные характеристики и дополнительную информацию
    из таблицы Product Information.

    Args:
        book_url (str): URL-адрес страницы книги для получения данных

    Returns:
        dict: Словарь с данными о книге, содержащий следующие ключи:
            - 'title': Название книги (str)
            - 'price': Цена книги (str)
            - 'rating': Рейтинг книги (str)
            - 'availability': Информация о наличии на складе (str)
            - 'description': Описание книги (str)
            - 'product_information': Словарь с дополнительными характеристиками из таблицы (Dict[str, str])

    Raises:
        requests.RequestException: Если произошла ошибка при запросе к странице
        Exception: Если не удалось получить данные со страницы
    """

    # НАЧАЛО ВАШЕГО РЕШЕНИЯ
    try:
        # Отправляем GET-запрос к странице книги
        response = requests.get(book_url)
        response.raise_for_status()

        # Создаем объект BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Извлекаем основные данные о книге
        title = _extract_title(soup)
        price = _extract_price(soup)
        rating = _extract_rating(soup)
        availability = _extract_availability(soup)
        description = _extract_description(soup)
        product_info = _extract_product_information(soup)

        # Формируем и возвращаем словарь с данными
        return {
            'title': title,
            'price': price,
            'rating': rating,
            'availability': availability,
            'description': description,
            'product_information': product_info
        }

    except requests.RequestException as e:
        raise requests.RequestException(f"Ошибка при запросе к {book_url}: {e}")
    except Exception as e:
        raise Exception(f"Ошибка при парсинге данных со страницы: {e}")


def _extract_title(soup: BeautifulSoup) -> str:
    """Извлекает название книги из HTML-страницы."""
    title_element = soup.find('h1')
    return title_element.text.strip() if title_element else "Название не найдено"


def _extract_price(soup: BeautifulSoup) -> str:
    """Извлекает цену книги из HTML-страницы."""
    price_element = soup.find('p', class_='price_color')
    return price_element.text.strip() if price_element else "Цена не найдена"


def _extract_rating(soup: BeautifulSoup) -> str:
    """Извлекает рейтинг книги из HTML-страницы."""
    # Рейтинг обычно хранится в классе элемента, например 'star-rating Five'
    rating_element = soup.find('p', class_='star-rating')
    if rating_element:
        rating_classes = rating_element.get('class', [])
        # Ищем класс, который начинается с 'star-rating' и содержит рейтинг
        for cls in rating_classes:
            if cls != 'star-rating':
                return cls
    return "Рейтинг не найден"


def _extract_availability(soup: BeautifulSoup) -> str:
    """Извлекает информацию о наличии книги на складе."""
    availability_element = soup.find('p', class_='availability')
    return availability_element.text.strip() if availability_element else "Информация о наличии не найдена"


def _extract_description(soup: BeautifulSoup) -> str:
    """Извлекает описание книги из HTML-страницы."""
    # Описание обычно находится в meta-теге или отдельном элементе
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        return meta_description.get('content', '').strip()

    # Альтернативный поиск описания
    product_description = soup.find('div', id='product_description')
    if product_description:
        next_sibling = product_description.find_next_sibling('p')
        if next_sibling:
            return next_sibling.text.strip()

    return "Описание не найдено"


def _extract_product_information(soup: BeautifulSoup) -> dict:
    """Извлекает дополнительную информацию из таблицы Product Information."""
    product_info = {}

    # Ищем таблицу с информацией о продукте
    table = soup.find('table', class_='table table-striped')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            header = row.find('th')
            value = row.find('td')
            if header and value:
                key = header.text.strip()
                product_info[key] = value.text.strip()

    return product_info
