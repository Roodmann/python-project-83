from urllib.parse import urlparse, urlunparse


def normalize_url(url):
    """Нормализует указанный URL"""
    
    # Разбираем URL
    parsed_url = urlparse(url)

    # Приводим схему и домен к нижнему регистру
    scheme = parsed_url.scheme.lower()
    netloc = parsed_url.netloc.lower()

    # Удаляем путь, если он пустой
    path = parsed_url.path if parsed_url.path else '/'

    # Формируем нормализованный URL
    normalized_url = urlunparse((scheme, netloc, path, parsed_url.params, parsed_url.query, parsed_url.fragment))

    return normalized_url


def is_valid_url(url):
    """Проверяет длину URL"""
    
    if len(url) > 255:
        
        return False


