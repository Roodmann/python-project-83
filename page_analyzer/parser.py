from bs4 import BeautifulSoup


def check_h1(soup):
    """
    Находит тег <h1> на странице и возвращает его текст без лишних пробелов.
    Если тег <h1> отсутствует, возвращает None.
    """
    h1_tag = soup.find('h1')
    
    return h1_tag.get_text(strip=True) if h1_tag else None


def check_title(soup):
    """
    Находит тег <title> на странице и возвращает его текст без лишних пробелов.
    Если тег <title> отсутствует, возвращает None.
    """
    title_tag = soup.find('title')
    
    return title_tag.get_text(strip=True) if title_tag else None


def check_meta_description(soup):
    """
    Находит мета-тег с атрибутом name='description' и возвращает значение 
    его content.
    Если мета-тег отсутствует или не содержит атрибута content, возвращает None.
    """
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and 'content' in meta_desc.attrs:
        return meta_desc['content'].strip()
    return None


def check_page(html):
    """
    Анализирует HTML-код страницы, создает объект BeautifulSoup и возвращает словарь
    с ключами 'h1', 'title' и 'description', содержащими соответствующие текстовые 
    значения.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    return {
        'h1': check_h1(soup),
        'title': check_title(soup),
        'description': check_meta_description(soup)
    }
