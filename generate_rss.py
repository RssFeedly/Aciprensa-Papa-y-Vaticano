import os
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

urls = [
    "https://www.aciprensa.com/tags/42/vaticano",
    "https://www.aciprensa.com/noticias/vaticano",
    "https://www.aciprensa.com/tags/14365/papa-leon-xiv",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

fg = FeedGenerator()
fg.title("RSS Aci Prensa Papa y Vaticano")
fg.link(href="https://www.aciprensa.com")
fg.description("Feed generado automáticamente con GitHub Actions")

print("Iniciando scrap de URLs específicas...")
total_entries = 0
seen_links = set()

for url in urls:
    print(f"Leyendo {url}")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Error al leer {url}: {e}")
        continue

    soup = BeautifulSoup(r.content, "html.parser")
    found_count = 0

    # Busca cualquier etiqueta <a> que lleve a una noticia y tenga texto de título
    for a in soup.find_all("a", href=True):
        link = a.get("href")
        title = a.get_text(strip=True)
        
        # Filtro: debe ser una URL de noticia y el texto debe parecerse a un titular (>15 caracteres)
        if "/noticias/" in link and len(title) > 15:
            full_link = urljoin("https://www.aciprensa.com", link)
            
            # Evitar duplicados si la misma noticia aparece varias veces en la página
            if full_link not in seen_links:
                seen_links.add(full_link)
                
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=full_link)
                total_entries += 1
                found_count += 1
                
                # Limitar a 5 noticias por cada URL específica para mantener el feed limpio
                if found_count >= 5:
                    break

rss_file_path = "rss.xml"
fg.rss_file(rss_file_path)
print(f"RSS generado en {rss_file_path} con {total_entries} entradas únicas")

if os.path.exists(rss_file_path):
    print("rss.xml existe y está listo para commit")
else:
    print("Error: rss.xml no se creó")
