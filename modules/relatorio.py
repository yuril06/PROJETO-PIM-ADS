# funcoes de relatorio e historico de vendas
import datetime
from modules.db import conectar


def relatorio_diario(data=None):
    # busca as vendas de uma data especifica, registro por registro
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    if data is None:
        data = datetime.date.today()

    sql = """
        SELECT v.id, p.nome AS produto_nome, p.preco AS preco_unitario,
               v.quantidade, (v.quantidade * p.preco) AS total_valor,
               v.dia_semana, v.data_venda
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        WHERE DATE(v.data_venda) = %s
        ORDER BY v.data_venda DESC
    """

    cursor.execute(sql, (data,))
    vendas = cursor.fetchall()

    total_geral = 0.0
    for venda in vendas:
        total_geral += float(venda['total_valor'])

    cursor.close()
    conexao.close()

    return {
        'data': data.strftime('%d/%m/%Y'),
        'data_input': data.strftime('%Y-%m-%d'),
        'vendas': vendas,
        'total_geral': total_geral
    }


def historico_por_dia_semana():
    # agrupa as vendas por dia da semana para ver qual dia vende mais
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    sql = """
        SELECT v.dia_semana,
               SUM(v.quantidade) AS total_itens_vendidos,
               SUM(v.quantidade * p.preco) AS total_valor
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY v.dia_semana
        ORDER BY total_itens_vendidos DESC
    """

    cursor.execute(sql)
    historico = cursor.fetchall()

    cursor.close()
    conexao.close()
    return historico


def historico_por_produto():
    # mostra quanto cada produto foi vendido por dia da semana
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    sql = """
        SELECT p.nome AS produto_nome, v.dia_semana,
               SUM(v.quantidade) AS total_vendido
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY p.nome, v.dia_semana
        ORDER BY p.nome, total_vendido DESC
    """

    cursor.execute(sql)
    historico = cursor.fetchall()

    cursor.close()
    conexao.close()
    return historico


def vendas_por_data(data):
    # retorna registros individuais de uma data para busca no historico
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    sql = """
        SELECT v.id, p.nome AS produto_nome, p.preco AS preco_unitario,
               v.quantidade, (v.quantidade * p.preco) AS total_valor,
               v.dia_semana, v.data_venda
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        WHERE DATE(v.data_venda) = %s
        ORDER BY v.data_venda DESC
    """

    cursor.execute(sql, (data,))
    vendas = cursor.fetchall()

    total_geral = 0.0
    for venda in vendas:
        total_geral += float(venda['total_valor'])

    cursor.close()
    conexao.close()

    return {
        'data': data.strftime('%d/%m/%Y'),
        'data_input': data.strftime('%Y-%m-%d'),
        'vendas': vendas,
        'total_geral': total_geral
    }
