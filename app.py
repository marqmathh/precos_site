from flask import Flask, render_template, request 
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
import requests
import json

# Função para obter as cotações
def obter_cotacoes():
    cotacoes = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL')
    cotacoes = cotacoes.json()
    return float(cotacoes['USDBRL']['bid']), float(cotacoes['EURBRL']['bid'])

cotacao_dolar, cotacao_euro = obter_cotacoes()  # Obtém cotações

# Configuração do Flask
app = Flask(__name__)

# Configuração do banco de dados
db = create_engine('sqlite:///Importados.db')
Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()

class Produtos(Base):
    __tablename__ = 'Produtos'

    Id = Column('Id', Integer, primary_key=True, autoincrement=True)
    Empresa = Column('Empresa', String)
    Produto = Column('Produto', String)
    Descricao = Column('Descrição', String)
    preco = Column('preço', Float)

    def __init__(self, Empresa, Produto, Descricao, preco):
        self.Empresa = Empresa
        self.Produto = Produto
        self.Descricao = Descricao
        self.preco = preco

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para buscar produto
@app.route('/cotacao', methods=['POST'])
def cotacao():
    nome_produto = request.form['nome_produto']
    filtro = request.form['filtro']
    nome_final_produto = f'%{nome_produto}%'

    # Busca o produto no banco de dados com base no filtro
    produtos_encontrados = []
    if filtro == 'codigo':
        produtos_encontrados = session.query(Produtos).filter(Produtos.Produto.like(nome_final_produto)).all()
    elif filtro == 'empresa':
        produtos_encontrados = session.query(Produtos).filter(Produtos.Empresa.like(nome_final_produto)).all()
    else:
        produtos_encontrados = session.query(Produtos).filter(Produtos.Descricao.like(nome_final_produto)).all()

    # Verifica se foram encontrados produtos
    if not produtos_encontrados:
        return render_template('erro.html', nome_produto=nome_produto)

    # Exibir resultados
    resultados = []
    for produto in produtos_encontrados:
        # Condição para calcular o valor final
        if produto.Empresa == 'OPW':
            preco_final = round(produto.preco * cotacao_dolar * 1.10 * 1.65 * 0.534, 2)  # Calculo para OPW
        else:
            preco_final = round(produto.preco * cotacao_dolar * 1.10 * 1.65, 2)  # Calculo para outras empresas

        resultados.append({
            'id': produto.Id,
            'empresa': produto.Empresa,
            'produto': produto.Produto,
            'descricao': produto.Descricao,
            'preco': preco_final
        })
    
    return render_template('resultado.html', resultados=resultados)

# Rota para buscar todos os produtos
@app.route('/todos', methods=['GET'])
def todos():
    # Busca todos os produtos no banco de dados
    produtos_encontrados = session.query(Produtos).all()
    
    # Exibir resultados
    resultados = []
    for produto in produtos_encontrados:
        # Condição para calcular o valor final
        if produto.Empresa == 'OPW':
            preco_final = round(produto.preco * cotacao_dolar * 1.10 * 1.65 * 0.534, 2)  # Calculo para OPW
        else:
            preco_final = round(produto.preco * cotacao_dolar * 1.10 * 1.65, 2)  # Calculo para outras empresas

        resultados.append({
            'id': produto.Id,
            'empresa': produto.Empresa,
            'produto': produto.Produto,
            'descricao': produto.Descricao,
            'preco': preco_final
        })
    
    return render_template('resultado.html', resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
