# sistema de controle de estoque da cantina escolar
# projeto PIM - ADS 1 semestre
# tecnologias: Python, Flask, MySQL

from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from functools import wraps
import os

from modules.estoque import cadastrar_produto, listar_produtos, buscar_produto, registrar_venda, editar_produto, excluir_produto, excluir_venda
from modules.relatorio import relatorio_diario, historico_por_dia_semana, historico_por_produto, vendas_por_data
import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'cantina_escola_2024')


# decorator que protege rotas — redireciona para login se nao estiver logado
def login_required(f):
    @wraps(f)
    def verificar(*args, **kwargs):
        if not session.get('logado'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return verificar


# pagina de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # se ja estiver logado, manda pro painel
    if session.get('logado'):
        return redirect(url_for('painel'))

    if request.method == 'POST':
        usuario = request.form['usuario']
        senha   = request.form['senha']

        # le as credenciais das variaveis de ambiente
        usuario_correto = os.getenv('ADMIN_USER', 'admin')
        senha_correta   = os.getenv('ADMIN_PASSWORD', 'cantina123')

        # verifica se usuario e senha estao corretos
        if usuario == usuario_correto and senha == senha_correta:
            session['logado'] = True
            return redirect(url_for('painel'))
        else:
            flash('Usuario ou senha incorretos.', 'erro')

    return render_template('login.html')


# logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# pagina principal - mostra todos os produtos
@app.route('/')
@login_required
def painel():
    try:
        produtos = listar_produtos()

        # conta quantos produtos estao com estoque baixo (for + if)
        total_alertas = 0
        for produto in produtos:
            if produto['estoque_baixo']:
                total_alertas += 1

        return render_template('index.html', produtos=produtos, total_alertas=total_alertas)

    except Exception as erro:
        return render_template('erro_db.html', erro=str(erro)), 500


# pagina de cadastro de produto
@app.route('/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro():
    if request.method == 'POST':
        nome           = request.form['nome'].strip()
        quantidade     = int(request.form['quantidade'])
        preco          = float(request.form['preco'])
        estoque_minimo = int(request.form['estoque_minimo'])

        # valida os campos antes de salvar
        if not nome:
            flash('O nome do produto nao pode estar vazio.', 'erro')
            return render_template('cadastro.html')

        if quantidade < 0:
            flash('A quantidade nao pode ser negativa.', 'erro')
            return render_template('cadastro.html')

        if preco <= 0:
            flash('O preco deve ser maior que zero.', 'erro')
            return render_template('cadastro.html')

        if estoque_minimo < 1:
            flash('O estoque minimo deve ser pelo menos 1.', 'erro')
            return render_template('cadastro.html')

        try:
            sucesso = cadastrar_produto(nome, quantidade, preco, estoque_minimo)
            if sucesso:
                flash(f'Produto "{nome}" cadastrado com sucesso!', 'sucesso')
                return redirect(url_for('painel'))
            else:
                flash('Erro ao cadastrar produto.', 'erro')
        except Exception as erro:
            flash(f'Erro: {erro}', 'erro')

    return render_template('cadastro.html')


# pagina de registro de venda
@app.route('/venda', methods=['GET', 'POST'])
@login_required
def venda():
    try:
        produtos = listar_produtos()
    except Exception as erro:
        return render_template('erro_db.html', erro=str(erro)), 500

    if request.method == 'POST':
        produto_id = int(request.form['produto_id'])
        quantidade = int(request.form['quantidade'])

        if quantidade <= 0:
            flash('A quantidade deve ser maior que zero.', 'erro')
            return render_template('venda.html', produtos=produtos)

        try:
            resultado = registrar_venda(produto_id, quantidade)

            # verifica o resultado da venda (if/elif)
            if resultado == 'sucesso':
                flash('Venda registrada com sucesso!', 'sucesso')

                produto = buscar_produto(produto_id)
                if produto and produto['quantidade'] <= produto['estoque_minimo']:
                    flash(f'Atencao: "{produto["nome"]}" atingiu o estoque minimo.', 'aviso')

            elif resultado == 'estoque_insuficiente':
                flash('Estoque insuficiente para esta venda.', 'erro')

            elif resultado == 'produto_nao_encontrado':
                flash('Produto nao encontrado.', 'erro')

        except Exception as erro:
            flash(f'Erro ao registrar venda: {erro}', 'erro')

        return redirect(url_for('painel'))

    return render_template('venda.html', produtos=produtos)


# pagina de gerenciamento de produtos
@app.route('/produtos')
@login_required
def gerenciar_produtos():
    try:
        produtos = listar_produtos()
        return render_template('produtos.html', produtos=produtos)
    except Exception as erro:
        return render_template('erro_db.html', erro=str(erro)), 500


# editar produto
@app.route('/editar/<int:produto_id>', methods=['GET', 'POST'])
@login_required
def editar(produto_id):
    try:
        produto = buscar_produto(produto_id)
    except Exception as erro:
        return render_template('erro_db.html', erro=str(erro)), 500

    if produto is None:
        flash('Produto nao encontrado.', 'erro')
        return redirect(url_for('gerenciar_produtos'))

    if request.method == 'POST':
        nome           = request.form['nome'].strip()
        quantidade     = int(request.form['quantidade'])
        preco          = float(request.form['preco'])
        estoque_minimo = int(request.form['estoque_minimo'])

        if not nome or quantidade < 0 or preco <= 0 or estoque_minimo < 1:
            flash('Preencha todos os campos corretamente.', 'erro')
            return render_template('editar.html', produto=produto)

        ok = editar_produto(produto_id, nome, quantidade, preco, estoque_minimo)
        if ok:
            flash(f'Produto "{nome}" atualizado com sucesso!', 'sucesso')
            return redirect(url_for('gerenciar_produtos'))
        else:
            flash('Erro ao atualizar produto.', 'erro')

    return render_template('editar.html', produto=produto)


# excluir produto
@app.route('/excluir/<int:produto_id>', methods=['POST'])
@login_required
def excluir(produto_id):
    try:
        produto = buscar_produto(produto_id)
        if produto:
            ok = excluir_produto(produto_id)
            if ok:
                flash(f'Produto "{produto["nome"]}" excluido com sucesso.', 'sucesso')
            else:
                flash('Erro ao excluir produto.', 'erro')
        else:
            flash('Produto nao encontrado.', 'erro')
    except Exception as erro:
        flash(f'Erro: {erro}', 'erro')

    return redirect(url_for('gerenciar_produtos'))


# pagina de relatorio diario com filtro de data
@app.route('/relatorio')
@login_required
def relatorio():
    try:
        data_str = request.args.get('data')
        if data_str:
            data = datetime.date.fromisoformat(data_str)
        else:
            data = datetime.date.today()
        dados = relatorio_diario(data)
        return render_template('relatorio.html', dados=dados)
    except Exception as erro:
        return render_template('erro_db.html', erro=str(erro)), 500


# excluir uma venda e restaurar estoque
@app.route('/excluir_venda/<int:venda_id>', methods=['POST'])
@login_required
def excluir_venda_route(venda_id):
    origem = request.form.get('origem', 'relatorio')
    data   = request.form.get('data', '')
    ok = excluir_venda(venda_id)
    if ok:
        flash('Venda excluida. Estoque restaurado.', 'sucesso')
    else:
        flash('Erro ao excluir venda.', 'erro')
    if origem == 'historico':
        return redirect(url_for('historico', data=data))
    return redirect(url_for('relatorio', data=data))


# pagina de historico por dia da semana com busca por data
@app.route('/historico')
@login_required
def historico():
    try:
        dados_semana  = historico_por_dia_semana()
        dados_produto = historico_por_produto()
        data_str = request.args.get('data')
        if data_str:
            data = datetime.date.fromisoformat(data_str)
        else:
            data = datetime.date.today()
        resultado_data = vendas_por_data(data)
        return render_template('historico.html', historico=dados_semana, por_produto=dados_produto, resultado_data=resultado_data, data_buscada=data.strftime('%Y-%m-%d'))
    except Exception as erro:
        return render_template('erro_db.html', erro=str(erro)), 500


# health check para o Railway
@app.route('/health')
def health():
    return {'status': 'ok'}, 200


if __name__ == '__main__':
    porta = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=porta, debug=False)
