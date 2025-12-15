from urllib.parse import urlparse, urlunparse


def normalize_url(url):
    """Нормализует указанный URL"""
    
    # Разбираем URL
    parsed_url = urlparse(url)

    # Приводим схему и домен к нижнему регистру
    scheme = parsed_url.scheme.lower()
    netloc = parsed_url.netloc.lower()

    return f"{scheme}://{netloc}"


def is_valid_url(url):
    """Проверяет, что URL валиден и длина не превышает 255 символов."""
    if len(url) > 255:
        return False
    parsed = urlparse(url)
    
    return all([parsed.scheme in ("http", "https"), parsed.netloc])
