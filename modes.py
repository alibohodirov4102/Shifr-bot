"""
Rejimlar Moduli — Xabarlarni turli usullarda o'zgartiradi

Rejimlar:
  random  → Tasodifiy rejim tanlaydi
  emoji   → Faqat smayllk
  morse   → Morse kodi
  binary  → Ikkilik son (0 va 1)
  reverse → Teskari matn
  zalgo   → Buzilgan (zalgo) matn
  ghost   → Spoiler (ko'rinmas) matn
  leet    → L33t speak
  meow    → Mushuk tili
  custom  → Admin tomonidan belgilangan matn
"""

import random
import unicodedata


class ModeManager:
    """Barcha shifrlash rejimlarini boshqaradi."""

    # ── Morse Kodlari ─────────────────────────────────────
    MORSE_CODE = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
        'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
        'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
        'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..',
        '0': '-----', '1': '.----', '2': '..---', '3': '...--',
        '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.',
        ' ': '/',
        # Lotin harflar bilan yaqin Kirill harflar
        'А': '.-', 'Б': '-...', 'В': '.--', 'Г': '--.',
        'Д': '-..', 'Е': '.', 'Ё': '.', 'Ж': '...-',
        'З': '--..', 'И': '..', 'Й': '.---', 'К': '-.-',
        'Л': '.-..', 'М': '--', 'Н': '-.', 'О': '---',
        'П': '.--.', 'Р': '.-.', 'С': '...', 'Т': '-',
        'У': '..-', 'Ф': '..-.', 'Х': '....', 'Ц': '-.-.',
        'Ч': '---.', 'Ш': '----', 'Щ': '--.-', 'Ъ': '.--.-.',
        'Ы': '-.--', 'Ь': '-..-', 'Э': '..-..', 'Ю': '..--',
        'Я': '.-.-',
    }

    # ── Leet Speak ────────────────────────────────────────
    LEET_MAP = {
        'a': '@', 'e': '3', 'i': '1', 'o': '0',
        's': '$', 't': '7', 'l': '|', 'g': '9',
        'b': '8', 'A': '@', 'E': '3', 'I': '1',
        'O': '0', 'S': '$', 'T': '7', 'L': '|',
        'G': '9', 'B': '8',
    }

    # ── Zalgo Belgilar ────────────────────────────────────
    ZALGO_UP = [
        '\u0300', '\u0301', '\u0302', '\u0303', '\u0304',
        '\u0305', '\u0306', '\u0307', '\u0308', '\u030A',
        '\u030B', '\u030C', '\u030D', '\u030E', '\u030F',
        '\u0311', '\u0312', '\u0313', '\u0314', '\u033D',
    ]
    ZALGO_DOWN = [
        '\u0316', '\u0317', '\u0318', '\u0319', '\u031C',
        '\u031D', '\u031E', '\u031F', '\u0320', '\u0321',
        '\u0322', '\u0323', '\u0324', '\u0325', '\u0326',
        '\u0329', '\u032A', '\u032B', '\u032C', '\u032D',
    ]

    # ── Mushuk so'zlari ───────────────────────────────────
    MEOW_WORDS = [
        "Miyov~ 🐱", "Prrrr~ 😺", "Mrrrow! 😸",
        "Meoow~ 🐾", "Purr purr~ 😻", "Nyaa~ 🐈",
        "Miyav miyav~ 🐱", "Mrr! 😼", "Fsss~ 😾",
        "Miyov miyov miyov~ 🐱💕",
    ]

    # ── Emoji to'plami ────────────────────────────────────
    EMOJIS = [
        "😂🤣😹", "🔥💥✨", "👀🤔💭", "🎉🎊🥳",
        "😍🥰💕", "😤😡🤬", "😭😢💔", "🤩⭐🌟",
        "👏🙌🤝", "🤦‍♂️🤷‍♀️😅", "🥱😪💤", "😱😨😰",
        "🤮🤢😷", "🤗😊🥹", "😏😎🕶️", "🦆🐸🦊",
        "🍕🍔🌮", "🎮🕹️👾", "💀☠️🦴", "🌈🌸🌺",
    ]

    # ─────────────────────────────────────────────────────

    def transform(self, text: str, mode: str, chat_id: int, db) -> str | None:
        """Matnni tanlangan rejimga ko'ra o'zgartiradi."""
        handlers = {
            "random":  self._random,
            "emoji":   self._emoji,
            "morse":   self._morse,
            "binary":  self._binary,
            "reverse": self._reverse,
            "zalgo":   self._zalgo,
            "ghost":   self._ghost,
            "leet":    self._leet,
            "meow":    self._meow,
            "custom":  lambda t: self._custom(t, chat_id, db),
        }
        handler = handlers.get(mode)
        if handler:
            return handler(text)
        return None

    # ══ Rejim Handlerlari ══════════════════════════════════

    def _random(self, text: str) -> str:
        """Tasodifiy rejimni tanlaydi."""
        modes = ["emoji", "morse", "binary", "reverse", "zalgo", "leet", "meow"]
        chosen = random.choice(modes)
        return self.transform(text, chosen, 0, None)

    def _emoji(self, text: str) -> str:
        """Matn o'rniga emoji ko'rsatadi."""
        return random.choice(self.EMOJIS)

    def _morse(self, text: str) -> str:
        """Matnni Morse kodiga o'giradi."""
        result = []
        for char in text.upper():
            if char in self.MORSE_CODE:
                result.append(self.MORSE_CODE[char])
            elif char == '\n':
                result.append('\n')
            else:
                result.append('?')
        return ' '.join(result)

    def _binary(self, text: str) -> str:
        """Matnni ikkilik songa o'giradi."""
        words = text.split()
        # Faqat birinchi 5 ta so'zni konvertatsiya qilish (juda uzun bo'lib ketmasin)
        converted = []
        for word in words[:5]:
            bits = ' '.join(format(ord(c), '08b') for c in word)
            converted.append(bits)
        result = '\n'.join(converted)
        if len(words) > 5:
            result += f"\n... (va {len(words)-5} ta so'z yana)"
        return f"`{result}`"

    def _reverse(self, text: str) -> str:
        """Matnni teskari yozadi."""
        return text[::-1]

    def _zalgo(self, text: str) -> str:
        """Matnni zalgo effekti bilan buzadi."""
        result = []
        for char in text:
            result.append(char)
            # Har belgiga 1-4 ta tasodifiy zalgo belgisi qo'shish
            for _ in range(random.randint(1, 4)):
                result.append(random.choice(self.ZALGO_UP + self.ZALGO_DOWN))
        return ''.join(result)

    def _ghost(self, text: str) -> str:
        """Spoiler (ko'rinmas) matn."""
        return f"||{text}||"

    def _leet(self, text: str) -> str:
        """L33t speak ga o'giradi."""
        return ''.join(self.LEET_MAP.get(c, c) for c in text)

    def _meow(self, text: str) -> str:
        """Mushuk tili — so'zlar soni asosida miyov."""
        word_count = len(text.split())
        meows = []
        for _ in range(min(word_count, 5)):
            meows.append(random.choice(self.MEOW_WORDS))
        return ' '.join(meows)

    def _custom(self, text: str, chat_id: int, db) -> str:
        """Admin tomonidan belgilangan matn."""
        if db:
            return db.get_custom_text(chat_id)
        return "Bu xabar shifrlangan 🔒"


# ── Test ──────────────────────────────────────────────────
if __name__ == "__main__":
    mm = ModeManager()
    test = "Salom dunyo!"
    print("Original :", test)
    print("Emoji    :", mm._emoji(test))
    print("Morse    :", mm._morse(test))
    print("Binary   :", mm._binary(test))
    print("Reverse  :", mm._reverse(test))
    print("Leet     :", mm._leet(test))
    print("Meow     :", mm._meow(test))
    print("Ghost    :", mm._ghost(test))
    print("Zalgo    :", mm._zalgo(test))
