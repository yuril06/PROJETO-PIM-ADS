import datetime
from modules.db import conectar

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
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, quantidade, preco, estoque_minimo) VALUES (%s, %s, %s, %s)",
            (nome, quantidade, preco, estoque_minimo)
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception as erro:
        print(f"Erro: {erro}")
        return False


def listar_produtos():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = cursor.fetchall()
    cursor.close()
    conexao.close()

    for produto in produtos:
        if produto['quantidade'] <= produto['estoque_minimo']:
            produto['estoque_baixo'] = True
        else:
            produto['estoque_baixo'] = False

    return produtos


def buscar_produto(produto_id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()
    cursor.close()
    conexao.close()
    return produto


def registrar_venda(produto_id, quantidade):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()

    if produto is None:
        cursor.close()
        conexao.close()
        return 'produto_nao_encontrado'

    if produto['quantidade'] < quantidade:
        cursor.close()
        conexao.close()
        return 'estoque_insuficiente'

    nova_quantidade = produto['quantidade'] - quantidade
    dia_semana = DIAS_SEMANA[datetime.datetime.now().weekday()]

    cursor.execute("UPDATE produtos SET quantidade = %s WHERE id = %s", (nova_quantidade, produto_id))
    cursor.execute("INSERT INTO vendas (produto_id, quantidade, dia_semana) VALUES (%s, %s, %s)",
                   (produto_id, quantidade, dia_semana))

    conexao.commit()
    cursor.close()
    conexao.close()
    return 'sucesso'


def excluir_venda(venda_id):
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
        print(f"Erro: {erro}")
        return False


def editar_produto(produto_id, nome, quantidade, preco, estoque_minimo):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = %s, quantidade = %s, preco = %s, estoque_minimo = %s WHERE id = %s",
            (nome, quantidade, preco, estoque_minimo, produto_id)
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception as erro:
        print(f"Erro: {erro}")
        return False


def excluir_produto(produto_id):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM vendas WHERE produto_id = %s", (produto_id,))
        cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception as erro:
        print(f"Erro: {erro}")
        return False
