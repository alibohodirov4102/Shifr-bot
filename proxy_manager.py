"""
Proxy Manager — Telegram API ga ulanishni ta'minlaydi.
Agar to'g'ridan-to'g'ri ulanish ishlamasa (bloklangan bo'lsa),
avtomatik ravishda ishlaydigan SOCKS5 proxy topadi va ulaydi.
"""

import asyncio
import os
import urllib.request
import httpx
import logging

logger = logging.getLogger(__name__)

WORKING_PROXY_FILE = "working_proxy.txt"

async def test_single_proxy(proxy_url: str, token: str, timeout: float = 3.5) -> bool:
    test_url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        async with httpx.AsyncClient(proxy=proxy_url, timeout=timeout) as client:
            resp = await client.get(test_url)
            if resp.status_code == 200 and resp.json().get("ok"):
                return True
    except Exception:
        pass
    return False

async def fetch_proxy_candidates() -> list[str]:
    urls = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
    ]
    candidates = []
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                text = resp.read().decode("utf-8", errors="ignore")
                for line in text.splitlines():
                    p = line.strip()
                    if p and ":" in p and not p.startswith("#"):
                        candidates.append(f"socks5://{p}")
            if len(candidates) >= 100:
                break
        except Exception:
            continue
    return list(dict.fromkeys(candidates))

async def get_working_proxy(token: str) -> str | None:
    # 1. To'g'ridan-to'g'ri ulanishni tekshirish
    logger.info("Tarmoq ulanishi tekshirilmoqda...")
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"https://api.telegram.org/bot{token}/getMe")
            if r.status_code == 200 and r.json().get("ok"):
                logger.info("To'g'ridan-to'g'ri ulanish muvaffaqiyatli! Proxy shart emas.")
                return None
    except Exception:
        pass

    logger.info("To'g'ridan-to'g'ri ulanish bloklangan. Proxy tekshirilmoqda...")

    # 2. Saqlangan oxirgi proxy ni tekshirish
    if os.path.exists(WORKING_PROXY_FILE):
        try:
            with open(WORKING_PROXY_FILE, "r", encoding="utf-8") as f:
                saved = f.read().strip()
            if saved and await test_single_proxy(saved, token, timeout=4.0):
                logger.info(f"Saqlangan proxy ishlayapti: {saved}")
                return saved
        except Exception:
            pass

    # 3. Yangi proxylarni yuklab tekshirish
    logger.info("Ishlaydigan proxy qidirilmoqda (bu bir necha soniya oladi)...")
    candidates = await fetch_proxy_candidates()
    logger.info(f"{len(candidates)} ta proxy topildi, sinab ko'rilmoqda...")

    for i in range(0, min(len(candidates), 150), 30):
        batch = candidates[i:i+30]
        tasks = [asyncio.create_task(test_single_proxy(p, token)) for p in batch]
        results = await asyncio.gather(*tasks)
        for proxy_url, is_ok in zip(batch, results):
            if is_ok:
                with open(WORKING_PROXY_FILE, "w", encoding="utf-8") as f:
                    f.write(proxy_url)
                logger.info(f"✅ Ishlaydigan proxy topildi: {proxy_url}")
                return proxy_url

    logger.warning("Mos proxy topilmadi!")
    return None
