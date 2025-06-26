from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
import os

app = FastAPI()
load_dotenv()  # Carrega variáveis de ambiente do .env

# Conexão segura com PostgreSQL usando os dados do .env
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

# MODELOS
class Produto(BaseModel):
    nome: str
    descricao: str
    preco: float
    quantidade: int = 0

class Movimentacao(BaseModel):
    produto_id: int
    tipo: str  # entrada ou saida
    quantidade: int

class Caixa(BaseModel):
    tipo: str  # entrada ou saida
    valor: float
    descricao: str

# ROTAS

@app.post("/produtos")
def cadastrar_produto(produto: Produto):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO produtos (nome, descricao, preco, quantidade) VALUES (%s, %s, %s, %s)",
            (produto.nome, produto.descricao, produto.preco, produto.quantidade)
        )
        conn.commit()
    return {"mensagem": "Produto cadastrado com sucesso"}

@app.post("/movimentacao")
def movimentar_produto(mov: Movimentacao):
    with conn.cursor() as cur:
        if mov.tipo == "entrada":
            cur.execute("UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s", (mov.quantidade, mov.produto_id))
        elif mov.tipo == "saida":
            cur.execute("UPDATE produtos SET quantidade = quantidade - %s WHERE id = %s", (mov.quantidade, mov.produto_id))
        else:
            return {"erro": "Tipo inválido"}
        cur.execute(
            "INSERT INTO movimentacoes (produto_id, tipo, quantidade) VALUES (%s, %s, %s)",
            (mov.produto_id, mov.tipo, mov.quantidade)
        )
        conn.commit()
    return {"mensagem": f"Movimentação de {mov.tipo} realizada com sucesso"}

@app.post("/caixa")
def registrar_movimentacao_caixa(entry: Caixa):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO caixa (tipo, valor, descricao) VALUES (%s, %s, %s)",
            (entry.tipo, entry.valor, entry.descricao)
        )
        conn.commit()
    return {"mensagem": "Movimentação no caixa registrada"}

@app.get("/relatorio/estoque")
def relatorio_estoque():
    with conn.cursor() as cur:
        cur.execute("SELECT id, nome, preco, quantidade FROM produtos")
        produtos = cur.fetchall()
    return {"produtos": produtos}

@app.get("/relatorio/movimentacoes")
def relatorio_movimentacoes():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM movimentacoes ORDER BY data DESC")
        movimentacoes = cur.fetchall()
    return {"movimentacoes": movimentacoes}

from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
from datetime import datetime

@app.get("/relatorio/estoque/pdf")
def gerar_relatorio_pdf():
    cur = conn.cursor()
    cur.execute("SELECT id, nome, preco, quantidade FROM produtos")
    produtos = cur.fetchall()
    cur.close()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Cabeçalho
    title = Paragraph("Relatório de Estoque", styles['Title'])
    date = Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal'])
    elements.extend([title, date, Spacer(1, 12)])

    # Tabela de produtos
    data = [["ID", "Nome", "Preço (R$)", "Quantidade"]]
    total_qtd = 0
    for prod in produtos:
        data.append([
            str(prod[0]),
            prod[1],
            f"{prod[2]:.2f}",
            str(prod[3])
        ])
        total_qtd += prod[3]

    table = Table(data, colWidths=[20*mm, 70*mm, 30*mm, 30*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER')
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Total de produtos: {len(produtos)}", styles['Normal']))
    elements.append(Paragraph(f"Quantidade total em estoque: {total_qtd}", styles['Normal']))

    doc.build(elements)
    return FileResponse(path=temp_file.name, filename="relatorio_estoque.pdf", media_type="application/pdf")
