# funcoes de cadastro e venda de produtos
import datetime
from modules.db import conectar

# dias da semana em portugues
DIAS_SEMANA = {
    0: 'Segunda-feira',
    1: 'Terca-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sabado',
    6: 'Domingo'
}


def cadastrar_produto(nome, quantidade, preco, estoque_minimo):
    # insere um novo produto no banco
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "INSERT INTO produtos (nome, quantidade, preco, estoque_minimo) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (nome, quantidade, preco, estoque_minimo))
        conexao.commit()

        cursor.close()
        conexao.close()
        return True

    except Exception as erro:
        print(f"Erro ao cadastrar: {erro}")
        return False


def listar_produtos():
    # retorna todos os produtos e marca quais estao com estoque baixo
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = cursor.fetchall()

    cursor.close()
    conexao.close()

    # verifica cada produto com estrutura de repeticao (for) e condicional (if/else)
    for produto in produtos:
        if produto['quantidade'] <= produto['estoque_minimo']:
            produto['estoque_baixo'] = True
        else:
            produto['estoque_baixo'] = False

    return produtos


def buscar_produto(produto_id):
    # busca um produto pelo id
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()

    cursor.close()
    conexao.close()
    return produto


def registrar_venda(produto_id, quantidade):
    # registra a venda e da baixa no estoque
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()

    # verifica se o produto existe
    if produto is None:
        cursor.close()
        conexao.close()
        return 'produto_nao_encontrado'

    # verifica se tem estoque suficiente
    if produto['quantidade'] < quantidade:
        cursor.close()
        conexao.close()
        return 'estoque_insuficiente'

    # calcula nova quantidade e salva
    nova_quantidade = produto['quantidade'] - quantidade
    dia_semana = DIAS_SEMANA[datetime.datetime.now().weekday()]

    cursor.execute("UPDATE produtos SET quantidade = %s WHERE id = %s", (nova_quantidade, produto_id))
    cursor.execute("INSERT INTO vendas (produto_id, quantidade, dia_semana) VALUES (%s, %s, %s)",
                   (produto_id, quantidade, dia_semana))

    conexao.commit()
    cursor.close()
    conexao.close()
    return 'sucesso'


def produtos_com_estoque_baixo():
    # retorna apenas os produtos abaixo do minimo
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE quantidade <= estoque_minimo ORDER BY nome")
    produtos = cursor.fetchall()

    cursor.close()
    conexao.close()
    return produtos


def editar_produto(produto_id, nome, quantidade, preco, estoque_minimo):
    # atualiza os dados de um produto existente
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """UPDATE produtos
                 SET nome = %s, quantidade = %s, preco = %s, estoque_minimo = %s
                 WHERE id = %s"""
        cursor.execute(sql, (nome, quantidade, preco, estoque_minimo, produto_id))
        conexao.commit()

        cursor.close()
        conexao.close()
        return True

    except Exception as erro:
        print(f"Erro ao editar: {erro}")
        return False


def excluir_venda(venda_id):
    # exclui uma venda e devolve a quantidade ao estoque
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("SELECT * FROM vendas WHERE id = %s", (venda_id,))
        venda = cursor.fetchone()

        if venda is None:
            cursor.close()
            conexao.close()
            return False

        cursor.execute("UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s",
                       (venda['quantidade'], venda['produto_id']))
        cursor.execute("DELETE FROM vendas WHERE id = %s", (venda_id,))
        conexao.commit()

        cursor.close()
        conexao.close()
        return True

    except Exception as erro:
        print(f"Erro ao excluir venda: {erro}")
        return False


def excluir_produto(produto_id):
    # exclui um produto e suas vendas do banco
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # precisa excluir as vendas primeiro por causa da chave estrangeira
        cursor.execute("DELETE FROM vendas WHERE produto_id = %s", (produto_id,))
        cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
        conexao.commit()

        cursor.close()
        conexao.close()
        return True

    except Exception as erro:
        print(f"Erro ao excluir: {erro}")
        return False
