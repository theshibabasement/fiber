import xml.etree.ElementTree as ET
import csv
import requests
from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def run_script():
    # Fazer uma requisição GET para a URL do XML
    response = requests.get('https://www.fiberoficial.com.br/collections/all.atom')

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Analisar o conteúdo XML da resposta
        root = ET.fromstring(response.content)
        
        # Abrir o arquivo CSV para escrita
        with open('produtos.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escrever o cabeçalho do CSV
            writer.writerow(['Produto', 'Descrição', 'Cor', 'Tamanho', 'Preço', 'Link Produto', 'Link Imagem'])
            
            # Iterar sobre cada entrada (produto) no XML
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                # Extrair os dados do produto
                product_id = entry.find('{http://www.w3.org/2005/Atom}id').text
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                link = entry.find('{http://www.w3.org/2005/Atom}link').get('href')
                
                # Extrair a descrição do produto
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
                description = ''
                if summary:
                    start_index = summary.find('<td colspan="2">') + len('<td colspan="2">')
                    end_index = summary.find('</td>', start_index)
                    if start_index != -1 and end_index != -1:
                        description = summary[start_index:end_index].strip()
                
                # Extrair o link da imagem do produto
                image_link = ''
                if summary:
                    start_index = summary.find('<img width="200" src="') + len('<img width="200" src="')
                    end_index = summary.find('"', start_index)
                    if start_index != -1 and end_index != -1:
                        image_link = summary[start_index:end_index]
                
                # Iterar sobre cada variante do produto
                for variant in entry.findall('{http://jadedpixel.com/-/spec/shopify}variant'):
                    variant_title = variant.find('{http://www.w3.org/2005/Atom}title').text
                    price = variant.find('{http://jadedpixel.com/-/spec/shopify}price').text
                    
                    # Extrair a cor e o tamanho da variante
                    color = ''
                    size = ''
                    if '/' in variant_title:
                        parts = variant_title.split('/')
                        size = parts[0].strip()
                        color = parts[1].strip()
                    else:
                        size = variant_title.strip()
                    
                    # Escrever uma linha no CSV para cada variante
                    writer.writerow([title, description, color, size, price, link, image_link])
        
        # Retornar o arquivo CSV como resposta
        return send_file('produtos.csv', mimetype='text/csv', as_attachment=True)
    else:
        return 'Falha ao fazer a requisição. Código de status: {}'.format(response.status_code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
