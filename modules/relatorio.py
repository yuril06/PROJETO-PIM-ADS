# ============================================================
# Módulo: relatorio.py
# Responsabilidade: Relatório diário e histórico de consumo
# ============================================================

import datetime          # Para trabalhar com datas
from modules.db import conectar  # Função de conexão com o banco


def relatorio_diario():
    """
    Gera o relatório de vendas do dia atual.

    Agrupa todas as vendas do dia por produto e calcula:
    - Total de unidades vendidas por produto
    - Valor total arrecadado por produto
    - Total geral do dia

    Retorna:
        dict com 'data', 'vendas' (lista) e 'total_geral' (float)
    """
    conexao = conectar()
    cursor  = conexao.cursor(dictionary=True)

    # Data de hoje para filtrar as vendas
    hoje = datetime.date.today()

    # SQL que busca e agrupa as vendas do dia atual
    sql = """
        SELECT
            p.nome          AS produto_nome,
            p.preco         AS preco_unitario,
            SUM(v.quantidade)           AS total_vendido,
            SUM(v.quantidade * p.preco) AS total_valor,
            v.dia_semana
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        WHERE DATE(v.data_venda) = %s
        GROUP BY p.id, p.nome, p.preco, v.dia_semana
        ORDER BY total_vendido DESC
    """

    cursor.execute(sql, (hoje,))
    vendas = cursor.fetchall()

    # Calcula o total geral usando estrutura de repetição (for)
    total_geral = 0.0
    for venda in vendas:
        total_geral += float(venda['total_valor'])

    cursor.close()
    conexao.close()

    # Retorna os dados formatados
    return {
        'data':        hoje.strftime('%d/%m/%Y'),
        'vendas':      vendas,
        'total_geral': total_geral
    }


def historico_por_dia_semana():
    """
    Retorna o consumo total agrupado por dia da semana.

    Permite identificar quais dias têm maior movimento na cantina.
    (A quarta-feira historicamente tem o maior consumo.)

    Retorna:
        Lista de dicionários com dia_semana, total_itens_vendidos e total_valor
    """
    conexao = conectar()
    cursor  = conexao.cursor(dictionary=True)

    # SQL que agrupa todas as vendas por dia da semana
    sql = """
        SELECT
            v.dia_semana,
            SUM(v.quantidade)           AS total_itens_vendidos,
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
    """
    Retorna o consumo agrupado por produto e dia da semana.

    Útil para identificar padrões específicos de cada produto
    ao longo da semana.

    Retorna:
        Lista de dicionários com produto_nome, dia_semana e total_vendido
    """
    conexao = conectar()
    cursor  = conexao.cursor(dictionary=True)

    # SQL que cruza produto com dia da semana
    sql = """
        SELECT
            p.nome  AS produto_nome,
            v.dia_semana,
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
