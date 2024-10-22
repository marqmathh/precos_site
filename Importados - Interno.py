from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
import requests
import json
import tkinter as tk
from tkinter import scrolledtext

# Função para obter as cotações
def obter_cotacoes():
    cotacoes = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL')
    cotacoes = cotacoes.json()
    return float(cotacoes['USDBRL']['bid']), float(cotacoes['EURBRL']['bid'])

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

Base.metadata.create_all(bind=db)

# Função para buscar produtos e exibir resultados
def buscar_produtos():
    nome_produto = entrada.get()  # Obtém o valor do campo de entrada
    nome_final_produto = f'%{nome_produto}%'
    
    cotacao_dolar, cotacao_euro = obter_cotacoes()  # Obtém cotações

    # Busca os produtos no banco de dados
    Achar_Produto = session.query(Produtos).filter(Produtos.Produto.like(nome_final_produto)).all()
    
    # Limpa a área de resultados antes de exibir novos
    resultado_texto.delete(1.0, tk.END)

    # Exibe os produtos encontrados
    for produto in Achar_Produto:
        if produto.Empresa == 'OPW':
            preco_calculado = produto.preco * 1.1 * 1.65 * 0.534 * cotacao_dolar
        else:
            preco_calculado = produto.preco * 1.1 * 1.65 * cotacao_dolar
        resultado_texto.insert(tk.END, f'{produto.Id} | {produto.Empresa.ljust(10)} | {produto.Produto.ljust(15)} | {produto.Descricao.ljust(20)} | R$ {round(preco_calculado, 2)}\n\n')

# Criação da janela principal
janela = tk.Tk()
janela.title("Buscar Produtos")

# Configuração do tamanho da janela
janela.geometry("1360x768")  # Largura x Altura

# Configuração do layout
tk.Label(janela, text="Digite o nome do produto a ser buscado:").pack()

entrada = tk.Entry(janela)
entrada.pack()

botao_buscar = tk.Button(janela, text="Buscar", command=buscar_produtos)
botao_buscar.pack()

resultado_texto = scrolledtext.ScrolledText(janela, height=30, width=120)
resultado_texto.pack()

# Inicia o loop da interface gráfica
janela.mainloop()
