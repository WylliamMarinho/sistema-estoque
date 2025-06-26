> Sistema de Controle de Estoque - FastAPI + PostgreSQL

API feita com FastAPI e PostgreSQL para controle de estoque com as funcionalidades:

- Cadastro de produtos
- Entrada e saída de estoque
- Relatórios com exportação em PDF

> Como rodar

0. Banco de Dados:

Para inicializar o banco, use o script SQL incluso no arquivo `init_db.sql` dentro do pgAdmin ou psql.


1. Clone o repositório:

Faça um clone ou baixe o .zip de https://github.com/WylliamMarinho/sistema-estoque.git

2. Abra o projeto baixado no pycharm, vá no terminal e ative:

python -m venv venv

.\venv\Scripts\activate

3. Instale os pacotes:

pip install -r requirements.txt

4. Crie um .env com base no .env.example

5. Rode a API no terminal:

uvicorn main:app --reload

6. Acesse o Sistema em: http://localhost:8000/docs
