"""
Rastgele motivasyon cümleleri. Her sayfada bir tane gösterilir.
"""

import random

MOTIVATION_QUOTES = [
    "Disiplin, motivasyondan daha güçlüdür.",
    "Bugün yaptığın tercih, yarının seni inşa eder.",
    "Her set, hedefine bir adım daha yaklaştırır.",
    "Zorlanıyorsan doğru yoldasın.",
    "Protein hedefin bugün de tamamlansın.",
    "Serini kırma; zincir uzasın.",
    "Küçük adımlar, büyük sonuçlar getirir.",
    "Vücudun sana teşekkür edecek.",
    "Rekor kırmak için önce kaydet.",
    "Bugünkü antrenman, yarının gücü.",
    "Hedeflerini yaz, takip et, gerçekleştir.",
    "Yorgunluk geçer, gurur kalır.",
    "Bir set daha, bir rep daha.",
    "Beslenme antrenmanın yarısıdır.",
    "Düzenli olan kazanır.",
    "Başlamak bitirmenin yarısıdır.",
    "Her gün biraz daha güçleniyorsun.",
    "Vitamin ve protein, performansın temeli.",
    "Bugün atladığın set, yarın eksik kalan gelişim.",
    "Elite olmak için elite davran.",
]


def get_random_motivation() -> str:
    """Rastgele bir motivasyon cümlesi döndürür."""
    return random.choice(MOTIVATION_QUOTES)
