"""
Utilidades para procesamiento de texto
"""
import unicodedata


def normalize_text(text: str) -> str:
    """
    Normaliza un texto removiendo tildes y convirtiendo a minúsculas.
    
    Útil para comparaciones de nombres que ignoren acentos y mayúsculas.
    
    Args:
        text: Texto a normalizar
    
    Returns:
        Texto normalizado (sin tildes, en minúsculas)
    
    Examples:
        >>> normalize_text("José María")
        'jose maria'
        >>> normalize_text("RUBÉN")
        'ruben'
    """
    if not text:
        return ""
    
    # Convertir a minúsculas
    text_lower = text.lower()
    
    # Normalizar y remover tildes
    normalized = ''.join(
        c for c in unicodedata.normalize('NFD', text_lower)
        if unicodedata.category(c) != 'Mn'
    )
    
    return normalized


def text_contains_word(text: str, search_word: str, min_word_length: int = 3) -> bool:
    """
    Verifica si un texto contiene una palabra de búsqueda (ignorando tildes y mayúsculas).
    
    Args:
        text: Texto donde buscar
        search_word: Palabra o frase a buscar
        min_word_length: Longitud mínima de palabra para considerar coincidencia
    
    Returns:
        True si encuentra la palabra, False en caso contrario
        
    Examples:
        >>> text_contains_word("José María López", "maria")
        True
        >>> text_contains_word("Juan Pérez", "perez")
        True
    """
    text_normalized = normalize_text(text)
    search_normalized = normalize_text(search_word)
    
    # Verificar si alguna palabra del texto de búsqueda aparece en el texto original
    search_words = search_normalized.split()
    
    for word in search_words:
        if len(word) >= min_word_length and word in text_normalized:
            return True
    
    return False
