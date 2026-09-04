import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    """Login/ro'yxatdan o'tish/parol-tiklash rate-limit'lari Django cache'da
    IP manzil bo'yicha saqlanadi — test client har doim bir xil soxta IP
    ishlatgani uchun, cache tozalanmasa turli test funksiyalari orasida
    hisoblagich to'planib, keyingi testlarni asossiz bloklab qo'yadi."""
    cache.clear()
    yield
    cache.clear()
