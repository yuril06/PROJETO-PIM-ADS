# ============================================================
# Módulo: estoque.py
# Responsabilidade: Cadastro de produtos e registro de vendas
# ============================================================

import datetime          # Para obter a data e dia da semana atual
from modules.db import conectar  # Função de conexão com o banco

# Dicionário (variável) que mapeia o número do dia para o nome em português
DIAS_SEMANA = {
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
}


def cadastrar_produto(nome, quantidade, preco, estoque_minimo):
    """
    Cadastra um novo produto no banco de dados.

    Parâmetros:
        nome           (str)  : Nome do produto
        quantidade     (int)  : Quantidade inicial em estoque
        preco          (float): Preço unitário
        estoque_minimo (int)  : Quantidade mínima antes do alerta

    Retorna:
        True se o cadastro foi bem-sucedido, False em caso de erro
    """
    # Tenta conectar ao banco e inserir o produto
    try:
        conexao = conectar()
        cursor  = conexao.cursor()

        # Comando SQL para inserir o produto na tabela
        sql = """
            INSERT INTO produtos (nome, quantidade, preco, estoque_minimo)
            VALUES (%s, %s, %s, %s)
        """

        # Executa a inserção com os valores recebidos
        cursor.execute(sql, (nome, quantidade, preco, estoque_minimo))
        conexao.commit()  # Confirma a operação no banco

        cursor.close()
        conexao.close()

        return True

    except Exception as erro:
        print(f"ERRO ao cadastrar produto: {erro}")
        return False


def listar_produtos():
    """
    Retorna todos os produtos cadastrados, ordenados por nome.

    Adiciona o campo 'estoque_baixo' (True/False) para cada produto,
    indicando se a quantidade está abaixo do mínimo configurado.

    Retorna:
        Lista de dicionários com os dados de cada produto
    """
    conexao = conectar()
    cursor  = conexao.cursor(dictionary=True)

    # Busca todos os produtos ordenados alfabeticamente
    cursor.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = cursor.fetchall()

    cursor.close()
    conexao.close()

    # Estrutura de repetição (for) para verificar cada produto
    for produto in produtos:
        # Estrutura condicional (if/else) para marcar estoque baixo
        if produto['quantidade'] <= produto['estoque_minimo']:
            produto['estoque_baixo'] = True   # Produto precisa de reposição
        else:
            produto['estoque_baixo'] = False  # Estoque ainda está OK

    return produtos


def buscar_produto(produto_id):
    """
    Busca um produto específico pelo seu ID.

    Parâmetro:
        produto_id (int): ID do produto no banco de dados

    Retorna:
        Dicionário com os dados do produto, ou None se não encontrado
    """
    conexao = conectar()
    cursor  = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()

    cursor.close()
    conexao.close()

    return produto


def registrar_venda(produto_id, quantidade):
    """
    Registra uma venda e diminui a quantidade do produto no estoque.

    Parâmetros:
        produto_id (int): ID do produto vendido
        quantidade (int): Quantidade vendida

    Retorna:
        'sucesso'               - Venda registrada com sucesso
        'estoque_insuficiente'  - Quantidade em estoque menor que a venda
        'produto_nao_encontrado'- Produto não existe no banco
    """
    conexao = conectar()
    cursor  = conexao.cursor(dictionary=True)

    # Busca o produto para verificar o estoque disponível
    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()

    # Estrutura condicional (if/elif) para validar a venda

    # 1. Verifica se o produto existe
    if produto is None:
        cursor.close()
        conexao.close()
        return 'produto_nao_encontrado'

    # 2. Verifica se há estoque suficiente para a venda
    if produto['quantidade'] < quantidade:
        cursor.close()
        conexao.close()
        return 'estoque_insuficiente'

    # 3. Calcula a nova quantidade após a venda
    nova_quantidade = produto['quantidade'] - quantidade

    # 4. Obtém o dia da semana atual em português
    hoje       = datetime.datetime.now()
    dia_semana = DIAS_SEMANA[hoje.weekday()]

    # 5. Atualiza o estoque do produto no banco
    cursor.execute(
        "UPDATE produtos SET quantidade = %s WHERE id = %s",
        (nova_quantidade, produto_id)
    )

    # 6. Registra a venda no histórico
    cursor.execute(
        """
        INSERT INTO vendas (produto_id, quantidade, dia_semana)
        VALUES (%s, %s, %s)
        """,
        (produto_id, quantidade, dia_semana)
    )

    conexao.commit()  # Confirma as duas operações juntas
    cursor.close()
    conexao.close()

    return 'sucesso'


def produtos_com_estoque_baixo():
    """
    Retorna apenas os produtos que estão abaixo do estoque mínimo.

    Usada para disparar notificações em lote quando necessário.

    Retorna:
        Lista de produtos com quantidade <= estoque_minimo
    """
    conexao = conectar()
    cursor  = conexao.cursor(dictionary=True)

    # SQL com condição WHERE para filtrar apenas os produtos críticos
    sql = """
        SELECT * FROM produtos
        WHERE quantidade <= estoque_minimo
        ORDER BY nome
    """

    cursor.execute(sql)
    produtos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return produtos
