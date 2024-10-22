from flask import Flask, render_template, request 
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

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

    def __init__(self, Empresa, Produto, Descricao, Preco):
        self.Empresa = Empresa
        self.Produto = Produto
        self.Descricao = Descricao
        self.preco = Preco

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
        produtos_encontrados = session.query(Produtos).filter(Produtos.Id.like(nome_final_produto)).all()
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
        resultados.append({
            'id': produto.Id,
            'empresa': produto.Empresa,
            'produto': produto.Produto,
            'descricao': produto.Descricao,
            'preco': round(produto.preco, 2)
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
        resultados.append({
            'id': produto.Id,
            'empresa': produto.Empresa,
            'produto': produto.Produto,
            'descricao': produto.Descricao,
            'preco': round(produto.preco, 2)
        })
    
    return render_template('resultado.html', resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
