import asyncio
import nest_asyncio
import pandas as pd
from datetime import datetime
import os
import re
from playwright.async_api import async_playwright

nest_asyncio.apply()

# File paths
CSV_PATH = "euler_apr_log_succeed.csv"
XLSX_PATH = "euler_apr_log_succeed.xlsx"

# URLs
USDC_URL = "https://app.euler.finance/vault/0xe0a80d35bB6618CBA260120b279d357978c42BCE?network=ethereum"
WETH_URL = "https://app.euler.finance/vault/0xD8b27CF359b7D15710a5BE299AF6e7Bf904984C2?network=ethereum"

# XPath directly targets the Supply APR value
USDC_XPATH = "/html/body/div/div[1]/div/div[2]/div/div[1]/div/ul/li[2]/div[1]/div[2]"
WETH_XPATH = "/html/body/div/div[1]/div/div[2]/div/div[1]/div/ul/li[2]/div[1]/div[2]"

# Initialize CSV file
def init_csv():
    if not os.path.exists(CSV_PATH):
        pd.DataFrame(columns=["timestamp", "coin", "APR"]).to_csv(CSV_PATH, index=False)
        print("[INFO] CSV file created.")
    else:
        print("[INFO] CSV file already exists.")

# Extract APR value from string
def parse_apr(text):
    match = re.search(r"[-+]?\d*\.\d+|\d+", text)
    if match:
        return float(match.group())
    raise ValueError(f"Could not parse APR value from text: {text}")

# Save APR data to CSV and Excel
def save_to_files(coin, apr_text):
    try:
        apr_value = parse_apr(apr_text)
    except Exception as e:
        print(f"[ERROR] Failed to parse APR for {coin}: {e}")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = pd.DataFrame([{"timestamp": now, "coin": coin, "APR": apr_value}])

    try:
        df = pd.read_csv(CSV_PATH)
        df = pd.concat([df, new_row], ignore_index=True)
    except:
        df = new_row

    df.to_csv(CSV_PATH, index=False)
    try:
        df.to_excel(XLSX_PATH, index=False)
    except Exception as e:
        print(f"[WARNING] Failed to save Excel file: {e}")

    print(f"[SUCCESS] {coin} APR recorded: {apr_value}%")

# Fetch APR using XPath
async def fetch_apr_with_xpath(page, xpath):
    element = page.locator(f"xpath={xpath}")
    await element.wait_for(state="visible", timeout=20000)
    apr_text = await element.text_content()
    if not apr_text:
        raise ValueError("APR value returned empty.")
    return apr_text.strip()

# Main function to fetch and save APR data
async def fetch_all():
    init_csv()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            print("[INFO] Navigating to USDC page...")
            await page.goto(USDC_URL)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            usdc_apr = await fetch_apr_with_xpath(page, USDC_XPATH)
            save_to_files("USDC", usdc_apr)
        except Exception as e:
            print(f"[ERROR] USDC failed: {e}")

        try:
            print("[INFO] Navigating to WETH page...")
            await page.goto(WETH_URL)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            weth_apr = await fetch_apr_with_xpath(page, WETH_XPATH)
            save_to_files("WETH", weth_apr)
        except Exception as e:
            print(f"[ERROR] WETH failed: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_all())
