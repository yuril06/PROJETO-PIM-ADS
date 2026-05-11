# ============================================================
# app.py - Aplicação Principal
# Sistema de Controle de Estoque - Cantina Escolar
# Projeto PIM - ADS 1º Semestre
# ============================================================

from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import os

# Importa as funções dos módulos do sistema
from modules.estoque import (
    cadastrar_produto,
    listar_produtos,
    buscar_produto,
    registrar_venda,
    produtos_com_estoque_baixo
)
from modules.notificacao import verificar_e_notificar
from modules.relatorio import (
    relatorio_diario,
    historico_por_dia_semana,
    historico_por_produto
)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Cria a instância da aplicação Flask
app = Flask(__name__)

# Chave secreta necessária para o sistema de mensagens flash
app.secret_key = os.getenv('SECRET_KEY', 'cantina_escola_pim_2024')


# ============================================================
# ROTA: Painel Principal de Estoque
# URL: /
# ============================================================
@app.route('/')
def painel():
    """
    Página inicial do sistema.
    Exibe todos os produtos em cards.
    Produtos com estoque baixo aparecem em vermelho com aviso.
    """
    try:
        # Variável que recebe a lista de todos os produtos
        produtos = listar_produtos()

        # Conta quantos produtos estão com estoque baixo
        # Estrutura de repetição (for) + condicional (if)
        total_alertas = 0
        for produto in produtos:
            if produto['estoque_baixo']:
                total_alertas += 1

        return render_template('index.html',
                               produtos=produtos,
                               total_alertas=total_alertas)

    except Exception as erro:
        # Exibe página de erro amigável se o banco não estiver disponível
        return render_template('erro_db.html', erro=str(erro)), 500


# ============================================================
# ROTA: Cadastro de Produtos
# URL: /cadastro
# Métodos: GET (exibe formulário) e POST (salva produto)
# ============================================================
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """
    Página para cadastrar novos produtos no estoque.
    """
    if request.method == 'POST':

        # Lê os dados enviados pelo formulário HTML
        nome           = request.form['nome'].strip()
        quantidade     = int(request.form['quantidade'])
        preco          = float(request.form['preco'])
        estoque_minimo = int(request.form['estoque_minimo'])

        # Validação dos dados com estrutura condicional (if)
        if not nome:
            flash('O nome do produto não pode estar vazio.', 'erro')
            return render_template('cadastro.html')

        if quantidade < 0:
            flash('A quantidade não pode ser negativa.', 'erro')
            return render_template('cadastro.html')

        if preco <= 0:
            flash('O preço deve ser maior que zero.', 'erro')
            return render_template('cadastro.html')

        if estoque_minimo < 1:
            flash('O estoque mínimo deve ser pelo menos 1.', 'erro')
            return render_template('cadastro.html')

        try:
            sucesso = cadastrar_produto(nome, quantidade, preco, estoque_minimo)

            if sucesso:
                flash(f'Produto "{nome}" cadastrado com sucesso!', 'sucesso')
                return redirect(url_for('painel'))
            else:
                flash('Erro ao cadastrar produto. Tente novamente.', 'erro')

        except Exception as erro:
            flash(f'Erro de banco de dados: {erro}', 'erro')

    return render_template('cadastro.html')


# ============================================================
# ROTA: Registro de Venda
# URL: /venda
# Métodos: GET (exibe formulário) e POST (registra venda)
# ============================================================
@app.route('/venda', methods=['GET', 'POST'])
def venda():
    """
    Página para registrar vendas (baixa no estoque).
    Após a venda, verifica se o produto atingiu o estoque mínimo
    e dispara notificação por e-mail automaticamente.
    """
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

            # Estrutura condicional (if/elif) para tratar o resultado
            if resultado == 'sucesso':
                flash('Venda registrada com sucesso!', 'sucesso')

                produto_atualizado = buscar_produto(produto_id)

                if produto_atualizado:
                    if produto_atualizado['quantidade'] <= produto_atualizado['estoque_minimo']:
                        email_enviado = verificar_e_notificar(produto_atualizado)

                        if email_enviado:
                            flash(
                                f'⚠️ ALERTA: "{produto_atualizado["nome"]}" atingiu '
                                f'o estoque mínimo! E-mail enviado automaticamente.',
                                'aviso'
                            )
                        else:
                            flash(
                                f'⚠️ ALERTA: "{produto_atualizado["nome"]}" atingiu '
                                f'o estoque mínimo! Verifique o painel.',
                                'aviso'
                            )

            elif resultado == 'estoque_insuficiente':
                flash('Estoque insuficiente para realizar esta venda.', 'erro')

            elif resultado == 'produto_nao_encontrado':
                flash('Produto não encontrado no sistema.', 'erro')

        except Exception as erro:
            flash(f'Erro ao registrar venda: {erro}', 'erro')

        return redirect(url_for('painel'))

    return render_template('venda.html', produtos=produtos)


# ============================================================
# ROTA: Relatório Diário de Vendas
# URL: /relatorio
# ============================================================
@app.route('/relatorio')
def relatorio():
    """
    Exibe o relatório de vendas do dia atual com totais.
    """
    try:
        dados = relatorio_diario()
        return render_template('relatorio.html', dados=dados)
    except Exception as erro:
        return render_template('erro_db.html', erro=str(erro)), 500


# ============================================================
# ROTA: Histórico de Consumo por Dia da Semana
# URL: /historico
# ============================================================
@app.route('/historico')
def historico():
    """
    Exibe o histórico de consumo agrupado por dia da semana.
    Destaca a quarta-feira, que historicamente tem maior consumo.
    """
    try:
        dados_semana  = historico_por_dia_semana()
        dados_produto = historico_por_produto()
        return render_template('historico.html',
                               historico=dados_semana,
                               por_produto=dados_produto)
    except Exception as erro:
        return render_template('erro_db.html', erro=str(erro)), 500


# ============================================================
# ROTA: Verificação de saúde da aplicação
# URL: /health — usada pelo Railway para checar se está online
# ============================================================
@app.route('/health')
def health():
    return {'status': 'ok'}, 200


# ============================================================
# INICIALIZAÇÃO DO SERVIDOR
# ============================================================
if __name__ == '__main__':
    porta = int(os.getenv('PORT', 5000))

    print("=" * 55)
    print("  Sistema de Estoque - Cantina Escolar")
    print("  Projeto PIM - ADS 1º Semestre")
    print("=" * 55)
    print(f"  Acesse no navegador: http://localhost:{porta}")
    print("=" * 55)

    modo_debug = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=porta, debug=modo_debug)
