import pytest
from unittest.mock import Mock, patch
import requests
from bs4 import BeautifulSoup

# Импортируем реальные функции из вашего основного файла
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from books_scraper import get_book_data, scrape_books, save_books_to_file


def test_get_book_data_returns_dict():
    """Тест: get_book_data возвращает словарь"""
    # Используем mock чтобы не делать реальные запросы
    with patch('books_scraper.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.content = """
        <html>
            <body>
                <h1>A Light in the Attic</h1>
                <p class="price_color">£51.77</p>
                <p class="star-rating Three">Three</p>
                <p class="availability">In stock (22 available)</p>
                <meta name="description" content="Test description">
                <table class="table table-striped">
                    <tr><th>UPC</th><td>a897fe39b1053632</td></tr>
                    <tr><th>Product Type</th><td>Books</td></tr>
                </table>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_book_data("http://test.com")
        assert isinstance(result, dict)


def test_get_book_data_has_required_keys():
    """Тест: get_book_data имеет все необходимые ключи"""
    with patch('books_scraper.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.content = "<html><body><h1>Test</h1></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_book_data("http://test.com")
        required_keys = ['title', 'price', 'rating', 'availability', 'description', 'product_information']
        for key in required_keys:
            assert key in result


def test_scrape_books_returns_list():
    """Тест: scrape_books возвращает список"""
    # Мокаем все сетевые запросы
    with patch('books_scraper.requests.get') as mock_get, \
         patch('books_scraper.time.sleep') as mock_sleep:
        
        mock_response = Mock()
        mock_response.content = """
        <html>
            <body>
                <article class="product_pod">
                    <h3><a href="book1.html">Book 1</a></h3>
                </article>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = scrape_books(save_to_file=False)
        assert isinstance(result, list)


def test_book_structure():
    """Тест структуры данных книги"""
    with patch('books_scraper.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.content = """
        <html>
            <body>
                <h1>Test Book</h1>
                <p class="price_color">£20.00</p>
                <p class="star-rating Three">Three</p>
                <p class="availability">In stock</p>
                <meta name="description" content="Test description">
                <table class="table table-striped">
                    <tr><th>UPC</th><td>test123</td></tr>
                </table>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        book = get_book_data("http://test.com")
        assert isinstance(book['title'], str)
        assert isinstance(book['price'], str)
        assert isinstance(book['rating'], str)
        assert isinstance(book['availability'], str)
        assert isinstance(book['description'], str)
        assert isinstance(book['product_information'], dict)


def test_save_books_to_file():
    """Тест сохранения книг в файл"""
    test_books = [
        {
            'title': 'Test Book 1',
            'price': '£20.00',
            'rating': 'Three',
            'availability': 'In stock',
            'description': 'Test description 1',
            'product_information': {'UPC': 'test123'}
        },
        {
            'title': 'Test Book 2', 
            'price': '£25.00',
            'rating': 'Four',
            'availability': 'In stock',
            'description': 'Test description 2',
            'product_information': {'UPC': 'test456'}
        }
    ]
    
    # Тестируем сохранение в файл
    test_filename = "test_books_output.txt"
    save_books_to_file(test_books, test_filename)
    
    # Проверяем что файл создан
    assert os.path.exists(test_filename)
    
    # Читаем и проверяем содержимое
    with open(test_filename, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'Test Book 1' in content
        assert 'Test Book 2' in content
        assert '£20.00' in content
        assert '£25.00' in content
    
    # Убираем за собой
    os.remove(test_filename)


def test_scrape_books_save_to_file_flag():
    """Тест флага save_to_file"""
    with patch('books_scraper.requests.get') as mock_get, \
         patch('books_scraper.time.sleep') as mock_sleep, \
         patch('books_scraper.save_books_to_file') as mock_save:
        
        mock_response = Mock()
        mock_response.content = """
        <html>
            <body>
                <article class="product_pod">
                    <h3><a href="book1.html">Book 1</a></h3>
                </article>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Тест с save_to_file=True
        result1 = scrape_books(save_to_file=True)
        assert mock_save.called
        
        # Сбрасываем mock
        mock_save.reset_mock()
        
        # Тест с save_to_file=False  
        result2 = scrape_books(save_to_file=False)
        assert not mock_save.called


def test_smoke_test():
    """Дымовой тест - проверяет что тесты вообще работают"""
    assert True


def test_product_information_parsing():
    """Тест парсинга дополнительной информации"""
    with patch('books_scraper.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.content = """
        <html>
            <body>
                <h1>Test Book</h1>
                <p class="price_color">£20.00</p>
                <p class="star-rating Three">Three</p>
                <p class="availability">In stock</p>
                <meta name="description" content="Test description">
                <table class="table table-striped">
                    <tr><th>UPC</th><td>test123</td></tr>
                    <tr><th>Product Type</th><td>Books</td></tr>
                    <tr><th>Price (excl. tax)</th><td>£20.00</td></tr>
                    <tr><th>Price (incl. tax)</th><td>£20.00</td></tr>
                    <tr><th>Tax</th><td>£0.00</td></tr>
                    <tr><th>Availability</th><td>In stock</td></tr>
                    <tr><th>Number of reviews</th><td>0</td></tr>
                </table>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        book = get_book_data("http://test.com")
        product_info = book['product_information']
        
        assert isinstance(product_info, dict)
        assert 'UPC' in product_info
        assert 'Product Type' in product_info
        assert 'Price (excl. tax)' in product_info
        assert product_info['UPC'] == 'test123'
        assert product_info['Product Type'] == 'Books'
