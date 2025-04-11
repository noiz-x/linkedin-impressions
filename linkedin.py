# linkedin.py

import asyncio
import os
import random
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

with open("user-agents.txt", "r") as file:
    user_agents = [line.strip() for line in file if line.strip()]

async def scrape_with_tor(playwright, url: str, iteration: int, headers: dict, proxy_config: dict):
    browser_context = await playwright.chromium.launch(
        headless=True,
        proxy=proxy_config
    )
    page = await browser_context.new_page()

    await page.set_extra_http_headers(headers)
    page.set_default_navigation_timeout(60000)

    await page.goto(url, wait_until="networkidle")

    # Attempt to dismiss modal if it appears
    try:
        # Wait for the dismiss button to appear with a short timeout
        await page.wait_for_selector('button.modal__dismiss[aria-label="Dismiss"]', timeout=5000)
        await page.click('button.modal__dismiss[aria-label="Dismiss"]')
        print(f"Iteration {iteration}: Dismissed the sign-in modal")
        await asyncio.sleep(1)  # Give the modal time to close
    except Exception as e:
        print(f"Iteration {iteration}: No sign-in modal to dismiss: {str(e)[:100]}")

    try:
        # Adjust the selector if LinkedIn updates its layout
        await page.wait_for_selector("section.core-rail", timeout=5000)
    except Exception as e:
        print(f"Iteration {iteration}: Expected selector not found: {e}")
        screenshot_path = f"screenshot_{iteration}.png"
        await page.screenshot(path=screenshot_path)
        print(f"Iteration {iteration}: Screenshot saved to {screenshot_path}")

    await asyncio.sleep(2)

    title = await page.title()
    print(f"Iteration {iteration}: Title: {title} (via Tor proxy, new browser instance)")

    await browser_context.close()

async def main():
    iterations = 500
    target_url = os.getenv("LINKEDIN_URL")
    proxy_config = {"server": "socks5://127.0.0.1:9050"}
    if not target_url:
        print("Please set the LINKEDIN_URL environment variable in your .env file.")
        return

    async with async_playwright() as playwright:
        for i in range(iterations):
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.linkedin.com/"
            }
            print(f"Iteration {i+1} headers: {headers}")
            await scrape_with_tor(playwright, target_url, i + 1, headers, proxy_config)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())