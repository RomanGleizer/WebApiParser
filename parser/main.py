import httpx
import re
from bs4 import BeautifulSoup

def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')

    names_elements = soup.find_all('div', class_='l-product__name')
    prices_elements = soup.find_all('div', class_='l-product__price')

    products = []

    if len(names_elements) != len(prices_elements):
        raise ValueError("Количество элементов с названиями и ценами не совпадают.")

    for i in range(len(names_elements)):
        name_element = names_elements[i]
        price_element = prices_elements[i]

        name = name_element.text.strip().split('\n')[0]
        price_text = price_element.text.strip()
        price_match = re.search(r'\d+\s*\d+', price_text)

        if price_match:
            price = price_match.group(0).replace('\xa0', '') + ' ₽'
        else:
            raise ValueError("Ошибка получения цены товара. Разметка не удовлетворяет текущим настройкам")

        products.append({'name': name, 'price': price})

    return products

def display_products(page_num, products):
    print(f"\nСобраны данные со страницы {page_num}")
    print(f"{'№':<5}{'Название':<50}{'Цена':>10}")
    print("-" * 65)
    for i, product in enumerate(products, 1):
        print(f"{i:<5}{product['name']:<50}{product['price']:>10}")

def scrape_products(base_url, pages=10):
    with httpx.Client() as client:
        for page_num in range(1, pages + 1):
            url = f'{base_url}&PAGEN_10={page_num}'

            response = client.get(url)
            if response.status_code == 200:
                html = response.text
                try:
                    page_data = parse_page(html)
                except Exception as elem:
                    print(f'Ошибка при разборе страницы {page_num}: {elem}')
                    continue

                display_products(page_num, page_data)
            else:
                print(f'Ошибка при получении страницы {page_num}: статус-код {response.status_code}')

search_category = input("Введите категорию поиска: ")
pages_amount = int(input("Введите количество страниц для отображения: "))

if len(search_category) == 0:
    raise ValueError("Была введена пустая категория.")

if pages_amount <= 0:
    raise ValueError(f'Невозможно отобразить товары {pages_amount} страницы')

page_url = f'https://www.maxidom.ru/search/catalog/?q={search_category}&amount=30'

try:
    scrape_products(page_url, pages_amount)
except Exception as e:
    print(f"Произошла ошибка при сборе данных: {e}")
