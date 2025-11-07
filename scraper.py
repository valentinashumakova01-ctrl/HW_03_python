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

def scrape_books(save_to_file=False, base_url="http://books.toscrape.com"):
    """
    Парсит все страницы каталога книг и собирает данные о книгах.
    
    Args:
        save_to_file (bool): Флаг для сохранения результатов в файл
        base_url (str): Базовый URL каталога
        
    Returns:
        list: Список словарей с данными о книгах
    """
    all_books_data = []
    page_number = 1
    
    while True:
        # Формируем URL страницы - исправлен путь
        if page_number == 1:
            url = f"{base_url}/catalogue/page-1.html"
        else:
            url = f"{base_url}/catalogue/page-{page_number}.html"
        
        try:
            print(f"Парсинг страницы {page_number}...")
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Проверяем, есть ли книги на странице - исправленный селектор
            books = soup.find_all('article', class_='product_pod')
            print(f"Найдено книг на странице: {len(books)}")
            
            if not books:
                print("Больше книг не найдено. Завершение...")
                break
            
            # Парсим данные о каждой книге на странице
            for book in books:
                try:
                    # Получаем ссылку на страницу книги
                    book_link_element = book.find('h3').find('a')
                    if not book_link_element:
                        continue
                        
                    book_link = book_link_element['href']
                    
                    # Обрабатываем относительные ссылки
                    if book_link.startswith('../../../'):
                        book_link = book_link.replace('../../../', 'http://books.toscrape.com/catalogue/')
                    elif book_link.startswith('../'):
                        book_link = book_link.replace('../', f'{base_url}/catalogue/')
                    elif not book_link.startswith('http'):
                        book_link = f'{base_url}/catalogue/{book_link}'
                    
                    print(f"  Обрабатывается книга: {book_link}")
                    
                    # Получаем данные о книге используя вашу функцию
                    book_data = get_book_data(book_link)
                    all_books_data.append(book_data)
                    print(f"  ✓ Обработана: {book_data.get('title', 'Unknown')}")
                    
                except Exception as e:
                    print(f"  ✗ Ошибка при обработке книги: {e}")
                    continue
            
            # Проверяем наличие следующей страницы
            next_button = soup.find('li', class_='next')
            if not next_button:
                print("Достигнута последняя страница.")
                break
                
            page_number += 1
            
            # Небольшая задержка чтобы не перегружать сервер
            time.sleep(1)
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                print("Достигнута последняя страница (404).")
                break
            else:
                print(f"Ошибка HTTP при запросе {url}: {e}")
                break
        except Exception as e:
            print(f"Ошибка при парсинге страницы {page_number}: {e}")
            break
    
    # Сохранение в файл если указан флаг
    if save_to_file and all_books_data:
        save_books_to_file(all_books_data)
    
    print(f"Парсинг завершен. Найдено книг: {len(all_books_data)}")
    return all_books_data


def save_books_to_file(books_data, filename="books_data.txt"):
    """
    Сохраняет данные о книгах в текстовый файл.
    
    Args:
        books_data (list): Список словарей с данными о книгах
        filename (str): Имя файла для сохранения
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for i, book in enumerate(books_data, 1):
                file.write(f"Книга #{i}\n")
                file.write(f"Название: {book.get('title', 'N/A')}\n")
                file.write(f"Цена: {book.get('price', 'N/A')}\n")
                file.write(f"Рейтинг: {book.get('rating', 'N/A')}\n")
                file.write(f"Наличие: {book.get('availability', 'N/A')}\n")
                
                description = book.get('description', 'N/A')
                if len(description) > 200:
                    description = description[:200] + "..."
                file.write(f"Описание: {description}\n")
                
                # Записываем дополнительную информацию
                product_info = book.get('product_information', {})
                if product_info:
                    file.write("Дополнительная информация:\n")
                    for key, value in product_info.items():
                        file.write(f"  {key}: {value}\n")
                
                file.write("=" * 60 + "\n")
        
        print(f"Данные сохранены в файл: {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении в файл: {e}")
