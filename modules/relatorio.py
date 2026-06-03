import datetime
from modules.db import conectar


def relatorio_diario(data=None):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    if data is None:
        data = datetime.date.today()

    cursor.execute("""
        SELECT v.id, p.nome AS produto_nome, p.preco AS preco_unitario,
               v.quantidade, (v.quantidade * p.preco) AS total_valor,
               v.dia_semana, v.data_venda
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        WHERE DATE(v.data_venda) = %s
        ORDER BY v.data_venda DESC
    """, (data,))

    vendas = cursor.fetchall()
    cursor.close()
    conexao.close()

    total_geral = 0.0
    for venda in vendas:
        total_geral += float(venda['total_valor'])

    return {
        'data': data.strftime('%d/%m/%Y'),
        'data_input': data.strftime('%Y-%m-%d'),
        'vendas': vendas,
        'total_geral': total_geral
    }


def historico_por_dia_semana():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT v.dia_semana,
               SUM(v.quantidade) AS total_itens_vendidos,
               SUM(v.quantidade * p.preco) AS total_valor
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY v.dia_semana
        ORDER BY total_itens_vendidos DESC
    """)

    historico = cursor.fetchall()
    cursor.close()
    conexao.close()
    return historico


def historico_por_produto():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.nome AS produto_nome, v.dia_semana,
               SUM(v.quantidade) AS total_vendido
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY p.nome, v.dia_semana
        ORDER BY p.nome, total_vendido DESC
    """)

    historico = cursor.fetchall()
    cursor.close()
    conexao.close()
    return historico


def vendas_por_data(data):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT v.id, p.nome AS produto_nome, p.preco AS preco_unitario,
               v.quantidade, (v.quantidade * p.preco) AS total_valor,
               v.dia_semana, v.data_venda
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        WHERE DATE(v.data_venda) = %s
        ORDER BY v.data_venda DESC
    """, (data,))

    vendas = cursor.fetchall()
    cursor.close()
    conexao.close()

    total_geral = 0.0
    for venda in vendas:
        total_geral += float(venda['total_valor'])

    return {
        'data': data.strftime('%d/%m/%Y'),
        'data_input': data.strftime('%Y-%m-%d'),
        'vendas': vendas,
        'total_geral': total_geral
    }
