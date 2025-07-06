import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import os
import re  # Sayıları metinden ayıklamak için

# Hedef URL ve XPath’ler
URL = "https://app.turtle.club/campaigns/katana"
USDC_XPATH = "/html/body/div/div/div/div/main/div/div[1]/div[2]/div/div[2]/div[1]/div/div[1]/div[2]/div[3]/span"
WETH_XPATH = "/html/body/div/div/div/div/main/div/div[1]/div[2]/div/div[2]/div[3]/div/div[1]/div[2]/div[3]/span"

CSV_PATH = "turtle_apr_log.csv"

# CSV başlatıcı (sadece bir kere oluşturur)
def init_csv():
    if not os.path.exists(CSV_PATH):
        df = pd.DataFrame(columns=["timestamp", "coin", "APR"])
        df.to_csv(CSV_PATH, index=False)
        print("[🆕] Yeni CSV dosyası oluşturuldu.")

# Metinden güvenli şekilde float sayı çıkarır
def string_to_float(text):
    match = re.search(r"[-+]?\d*\.\d+|\d+", text)
    if match:
        return float(match.group())
    else:
        raise ValueError(f"Sayı bulunamadı: {text}")

# CSV'ye veri ekleyici
def save_apr(coin, apr_raw_text):
    try:
        apr_value = string_to_float(apr_raw_text)
    except ValueError as e:
        print(f"[❌] {coin} APR sayıya çevrilemedi: {e}")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = pd.DataFrame([{"timestamp": now, "coin": coin, "APR": apr_value}])

    try:
        df = pd.read_csv(CSV_PATH)
        df = pd.concat([df, new_row], ignore_index=True)
    except Exception as e:
        print(f"[⚠️] CSV okunamadı, yeni oluşturuluyor: {e}")
        df = new_row  # dosya bozulduysa sıfırdan başlat

    df.to_csv(CSV_PATH, index=False)
    print(f"[✔️] {coin} APR kaydedildi: {apr_value}%")

# Asenkron veri çekici
async def fetch_aprs():
    init_csv()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # headless=False → debug için
        page = await browser.new_page()
        await page.goto(URL)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5)  # sayfanın yüklenmesini bekle

        try:
            usdc_raw = await page.locator(f"xpath={USDC_XPATH}").text_content()
            weth_raw = await page.locator(f"xpath={WETH_XPATH}").text_content()

            print(f"[📊] USDC APR Raw: {usdc_raw}")
            print(f"[📊] WETH APR Raw: {weth_raw}")

            save_apr("USDC", usdc_raw)
            save_apr("WETH", weth_raw)

        except Exception as e:
            print(f"[❌] XPath verisi alınamadı: {e}")

        await browser.close()

# Ana fonksiyon
if __name__ == "__main__":
    asyncio.run(fetch_aprs())
