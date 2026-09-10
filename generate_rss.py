from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import os
from urllib.parse import urljoin

urls = [
    "https://www.aciprensa.com/tags/42/vaticano",
    "https://www.aciprensa.com/noticias/vaticano",
    "https://www.aciprensa.com/tags/14365/papa-leon-xiv",
]

# Cabecera para simular un navegador y evitar bloqueos
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

fg = FeedGenerator()
fg.title("RSS Aci Prensa Papa y Vaticano")
fg.link(href="https://www.aciprensa.com")
fg.description("Feed generado automáticamente con GitHub Actions")

print("Iniciando scrap de URLs...")

total_entries = 0

for url in urls:
    print(f"Leyendo {url}")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Error al leer {url}: {e}")
        continue

    soup = BeautifulSoup(r.content, "html.parser")
    
    # Intenta buscar h2 a o ajusta según la estructura de la web
    articles = soup.select("h2 a")[:5]  
    if not articles:
        print(f"No se encontraron titulares en {url}")
        continue

    for a in articles:
        title = a.get_text(strip=True)
        link = a.get("href")
        
        if title and link:
            # Asegurar que el enlace sea absoluto
            full_link = urljoin("https://www.aciprensa.com", link)
            
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=full_link)
            total_entries += 1

rss_file_path = "rss.xml"

fg.rss_file(rss_file_path)
print(f"RSS generado en {rss_file_path} con {total_entries} entradas")

if os.path.exists(rss_file_path):
    print("rss.xml existe y está listo para commit")
else:
    print("Error: rss.xml no se creó")
