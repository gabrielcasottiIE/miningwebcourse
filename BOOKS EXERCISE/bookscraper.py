#!/usr/bin/env python3
"""
Web scraper para extrair títulos e preços de livros do site books.toscrape.com
Salva os dados em um arquivo CSV
"""

import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin


def scrape_books(url="http://books.toscrape.com/", output_file="books.csv"):
    """
    Extrai títulos e preços de livros do site books.toscrape.com
    
    Args:
        url (str): URL base do site
        output_file (str): Nome do arquivo CSV para salvar os dados
    """
    
    all_books = []
    current_url = url
    
    try:
        while current_url:
            print(f"Raspando: {current_url}")
            
            # Fazer requisição HTTP
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(current_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontrar todos os livros na página
            books = soup.find_all('article', class_='product_pod')
            
            if not books:
                print(f"Nenhum livro encontrado. Finalizando...")
                break
            
            # Extrair informações de cada livro
            for book in books:
                # O título está em <h3><a title="...">
                h3 = book.find('h3')
                if h3 and h3.a:
                    title = h3.a['title']
                else:
                    continue
                
                price_elem = book.find('p', class_='price_color')
                if price_elem:
                    price_text = price_elem.text
                    price = price_text.replace('£', '').strip()
                else:
                    price = "N/A"
                    price_text = "N/A"
                
                # O rating está em <p class="star-rating ClassName">
                rating_elem = book.find('p', class_='star-rating')
                rating_mapping = {
                    'One': 1,
                    'Two': 2,
                    'Three': 3,
                    'Four': 4,
                    'Five': 5
                }
                if rating_elem:
                    rating_class = rating_elem.get('class', [])
                    rating_text = next((r for r in rating_class if r in rating_mapping), 'N/A')
                    rating = rating_mapping.get(rating_text, 'N/A')
                else:
                    rating = "N/A"
                
                all_books.append({
                    'title': title,
                    'price': price,
                    'rating': rating
                })
                
                print(f"  ✓ {title} - {price_text} - Rating: {rating}")
            
            # Procurar pelo link da próxima página
            next_button = soup.find('li', class_='next')
            if next_button and next_button.a:
                next_url = next_button.a['href']
                current_url = urljoin(current_url, next_url)
            else:
                current_url = None
        
        # Salvar dados em arquivo CSV
        if all_books:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['title', 'price', 'rating']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(all_books)
            
            print(f"\n✅ Sucesso! {len(all_books)} livros foram salvos em '{output_file}'")
        else:
            print("Nenhum livro foi extraído.")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao fazer a requisição: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    scrape_books()
