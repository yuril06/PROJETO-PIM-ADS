# sistema de controle de estoque da cantina escolar
# projeto PIM - ADS 1 semestre
# tecnologias: Python, Flask, MySQL

from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import os

from modules.estoque import cadastrar_produto, listar_produtos, buscar_produto, registrar_venda
from modules.notificacao import verificar_e_notificar
from modules.relatorio import relatorio_diario, historico_por_dia_semana, historico_por_produto

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'cantina_escola_2024')


# pagina principal - mostra todos os produtos
@app.route('/')
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

                # verifica se o produto atingiu o estoque minimo
                produto = buscar_produto(produto_id)
                if produto and produto['quantidade'] <= produto['estoque_minimo']:
                    email_ok = verificar_e_notificar(produto)
                    if email_ok:
                        flash(f'Atencao: "{produto["nome"]}" atingiu o estoque minimo. E-mail enviado.', 'aviso')
                    else:
                        flash(f'Atencao: "{produto["nome"]}" atingiu o estoque minimo.', 'aviso')

            elif resultado == 'estoque_insuficiente':
                flash('Estoque insuficiente para esta venda.', 'erro')

            elif resultado == 'produto_nao_encontrado':
                flash('Produto nao encontrado.', 'erro')

        except Exception as erro:
            flash(f'Erro ao registrar venda: {erro}', 'erro')

        return redirect(url_for('painel'))

    return render_template('venda.html', produtos=produtos)


# pagina de relatorio diario
@app.route('/relatorio')
def relatorio():
    try:
        dados = relatorio_diario()
        return render_template('relatorio.html', dados=dados)
    except Exception as erro:
        return render_template('erro_db.html', erro=str(erro)), 500


# pagina de historico por dia da semana
@app.route('/historico')
def historico():
    try:
        dados_semana  = historico_por_dia_semana()
        dados_produto = historico_por_produto()
        return render_template('historico.html', historico=dados_semana, por_produto=dados_produto)
    except Exception as erro:
        return render_template('erro_db.html', erro=str(erro)), 500


# rota de health check para o Railway saber que o app esta rodando
@app.route('/health')
def health():
    return {'status': 'ok'}, 200


if __name__ == '__main__':
    porta = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=porta, debug=False)
