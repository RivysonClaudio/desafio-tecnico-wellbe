import os
from dotenv import load_dotenv

load_dotenv()

from setup_django import init
init()

from playwright.sync_api import sync_playwright
from apps.movies.models import Movie
from src.utils.zip_util import ZipBuilder

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)

    page = browser.new_page()

    page.goto("https://rpachallenge.com/")

    print("\nETAPA 1: BUSCA DE FILMES E SALVAMENTO NO BANCO DE DADOS\n")

    page.get_by_role("link", name="Movie Search").click()

    page.locator("input").fill("Avengers")

    page.get_by_role("button", name="Find").click()

    page.locator(".card-reveal")

    cards = page.locator(".card-reveal")

    results = []

    for i in range(cards.count()):
        card = cards.nth(i)
        
        results.append({
            "title": card.locator("span").inner_text(),
            "description": card.locator("p").inner_text()
        })

    for result in results:
        Movie.objects.update_or_create(
            title=result['title'],
            defaults={'description': result['description']}
        )

        print(f"Salvo: {result['title']}")

    print("\nETAPA 2: EXTRAÇÃO DE FATURAS E SALVAMENTO NO ZIP\n")

    page.locator("a:has-text('Invoice Extraction')").click()

    page.locator("#tableSandbox tbody tr").first.wait_for(state="visible")

    rows = page.locator("#tableSandbox tbody tr").all()

    zip_builder = ZipBuilder().builder()

    for row in rows:
        cells = row.locator("td")

        if cells.nth(0).inner_text().strip() in ["2", "4"]:
            invoice_id = cells.nth(0).inner_text().strip()

            with page.context.expect_page() as new_page_info:
                cells.last.locator("a").click()
            
            new_page = new_page_info.value
            new_page.wait_for_load_state("networkidle")
            
            img_url = new_page.locator("img").get_attribute("src")
            img_extension = img_url.split(".")[-1]

            if img_url:
                response = page.request.get(img_url)
                img_binary = response.body()

                zip_builder.add_file(f"invoice_{invoice_id}.{img_extension}", img_binary)
                print(f"Invoice {invoice_id} added to zip file in memory")

            new_page.close()

    os.makedirs("storage", exist_ok=True)

    zip_file = zip_builder.build()
    print("Zip file built in memory")

    with open("storage/invoices.zip", "wb") as f:
        f.write(zip_file)

    print("Zip file saved as invoices.zip in storage folder")

    print("\nFIM DO DESAFIO\n")

    browser.close()