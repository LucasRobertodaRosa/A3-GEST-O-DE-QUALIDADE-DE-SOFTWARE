from datetime import datetime

try:
    from .banco import conectar
except ImportError:
    from banco import conectar


def _obter_conexao(conexao=None):
    """
    Retorna uma conexão com o banco.

    Se uma conexão for passada, ela será reutilizada.
    Isso facilita os testes posteriormente.
    """
    if conexao is not None:
        return conexao, False

    return conectar(), True


def _validar_quantidade(quantidade):
    """
    Valida se a quantidade informada é numérica e maior que zero.
    """
    if isinstance(quantidade, bool) or not isinstance(
        quantidade, (int, float)
    ):
        raise ValueError("A quantidade deve ser numérica.")

    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")


def _data_atual():
    """
    Retorna a data e hora atuais.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _produto_existe(conexao, id_produto):
    """
    Verifica se o produto existe no banco.
    """
    cursor = conexao.execute(
        "SELECT id FROM produtos WHERE id = ?",
        (id_produto,),
    )

    return cursor.fetchone() is not None


def registrar_entrada(
    id_produto,
    quantidade,
    fornecedor,
    data_entrada=None,
    conexao=None,
):
    """
    Registra uma entrada no estoque e atualiza
    a quantidade disponível do produto.

    Retorna o ID da entrada criada.
    """

    _validar_quantidade(quantidade)

    if not fornecedor or not str(fornecedor).strip():
        raise ValueError("O fornecedor deve ser informado.")

    conn, deve_fechar = _obter_conexao(conexao)

    try:
        if not _produto_existe(conn, id_produto):
            raise ValueError("Produto não encontrado.")

        data_entrada = data_entrada or _data_atual()

        with conn:

            cursor = conn.execute(
                """
                INSERT INTO entradas
                (
                    id_produto,
                    quantidade,
                    data_entrada,
                    fornecedor
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    id_produto,
                    quantidade,
                    data_entrada,
                    str(fornecedor).strip(),
                ),
            )

            conn.execute(
                """
                UPDATE produtos
                SET quantidade = quantidade + ?
                WHERE id = ?
                """,
                (
                    quantidade,
                    id_produto,
                ),
            )

        return cursor.lastrowid

    finally:
        if deve_fechar:
            conn.close()