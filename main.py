import requests
import bs4
import pandas
import datetime
from concurrent.futures import ThreadPoolExecutor


site_url = 'https://hobbygames.ru/'
link_to_games = 'https://hobbygames.ru/nastolnie'
product_class = 'product-item'


def parse_page(page_url):
    response = requests.get(page_url)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        products = soup.find_all('div', product_class)

        data_list = []

        for product in products:
            name = product.find('a', 'name').text.strip()
            link = site_url + product.find('a', 'name')['href']

            if product.find('div', 'params__item players'):
                players = product.find('div', 'params__item players').text.strip()
            else:
                players = None

            if product.find('div', 'params__item time'):
                time = product.find('div', 'params__item time').text.strip()
            else:
                time = None

            if product.find('div', 'params__item age'):
                age = product.find('div', 'params__item age').text.strip()
            else:
                age = None

            images = product.find('div', 'image')
            image = images.find('img')['src']

            data_list.append({
                'name': name,
                'link': link,
                'players': players,
                'time': time,
                'age': age,
                'image': image
            })
        return data_list

    return []


def parse_all_games(category_link):
    num_pages = 55
    data_list = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(parse_page, f"{category_link}&page={page}&results_per_page=60") for page in range(1, num_pages + 1)]

    for future in futures:
        data_list.extend(future.result())

    df = pandas.DataFrame(data_list)
    df.to_excel('games.xlsx', index=False)
    return data_list


if __name__ == "__main__":
    # Замеряем время выполнения
    start_time = datetime.datetime.now()
    parse_all_games(link_to_games)
    end_time = datetime.datetime.now()
    print(f'Время выполнения: {end_time-start_time}')
