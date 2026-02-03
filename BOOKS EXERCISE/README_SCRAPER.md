# Web Scraper de Livros

Um web scraper Python que extrai títulos e preços de livros do site [books.toscrape.com](http://books.toscrape.com/) e salva os dados em um arquivo CSV.

## Arquivos

- **scraper.py**: Script principal que faz o scraping dos dados
- **requirements.txt**: Dependências do projeto
- **books.csv**: Arquivo CSV com os dados dos livros (gerado após executar o scraper)

## Requisitos

- Python 3.7+
- pip (gerenciador de pacotes do Python)

## Instalação

1. Clone ou acesse o repositório:
```bash
cd /workspaces/miningwebcourse
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

Execute o scraper com o comando:

```bash
python scraper.py
```

O script irá:
1. Acessar o site books.toscrape.com
2. Fazer a raspagem de todas as páginas disponíveis
3. Extrair o título e preço de cada livro
4. Salvar os dados no arquivo `books.csv`

## Dependências

- **requests**: Biblioteca para fazer requisições HTTP
- **beautifulsoup4**: Biblioteca para fazer parsing de HTML

## Estrutura do CSV

O arquivo `books.csv` contém as seguintes colunas:

| Coluna | Descrição |
|--------|-----------|
| title  | Título do livro |
| price  | Preço do livro em libras esterlinas (£) |

## Exemplo de Saída

```
title,price
A Light in the Attic,51.77
Tipping the Velvet,53.74
Soumission,50.10
Sharp Objects,47.82
Sapiens: A Brief History of Humankind,54.23
...
```

## Notas

- O scraper navega automaticamente entre todas as páginas do site
- Os preços estão em libras esterlinas (£)
- O script inclui um User-Agent para evitar bloqueios
- O arquivo CSV é sobrescrito a cada execução do scraper

## Customização

Você pode modificar o comportamento do scraper alterando os parâmetros da função `scrape_books()`:

```python
scrape_books(
    url="http://books.toscrape.com/",  # URL base do site
    output_file="books.csv"              # Nome do arquivo de saída
)
```

## Aviso Legal

Por favor, respeite o arquivo `robots.txt` do site e as suas políticas de uso. Este scraper foi desenvolvido apenas para fins educacionais.
