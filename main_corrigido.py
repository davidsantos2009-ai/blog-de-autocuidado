from flask import Flask, request, redirect, render_template_string
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
BANCO = "autocuidado.db"

# PRODUTOS: preços ilustrativos, do mais caro ao mais barato.
# Confira os preços nas lojas antes de comprar.

PRODUTOS = {
    "rosto": {
        "titulo": "Cuidados com o rosto",
        "descricao": "Cuide da sua pele com uma rotina adequada às suas necessidades.",
        "produtos": [
            ("Sérum facial de vitamina C", "Antioxidante para a rotina facial.", 180.00),
            ("Hidratante facial", "Ajuda a manter a hidratação da pele.", 95.00),
            ("Protetor solar facial FPS 50", "Ajuda a proteger contra os raios UV.", 75.00),
            ("Gel de limpeza facial", "Ajuda a remover oleosidade e impurezas.", 45.00),
            ("Hidratante facial simples", "Opção para hidratação diária.", 30.00),
        ],
        "dica": "Pele com acne: prefira produtos não comedogênicos. Evite espremer espinhas e use protetor solar."
    },
    "cabelo-liso": {
        "titulo": "Cuidados com cabelo liso",
        "descricao": "Brilho, maciez e cuidados para os fios lisos.",
        "produtos": [
            ("Máscara capilar profissional", "Tratamento cosmético para os fios.", 160.00),
            ("Óleo finalizador capilar", "Ajuda a reduzir o aspecto de frizz.", 85.00),
            ("Condicionador hidratante", "Ajuda a desembaraçar os fios.", 55.00),
            ("Shampoo para uso diário", "Limpeza do couro cabeludo e dos fios.", 35.00),
            ("Creme para pentear leve", "Ajuda no alinhamento dos fios.", 25.00),
        ],
        "dica": "Evite excesso de calor e use um protetor térmico antes de utilizar secador ou chapinha."
    },
    "cabelo-cacheado": {
        "titulo": "Cuidados com cabelo cacheado",
        "descricao": "Definição, hidratação e valorização dos cachos.",
        "produtos": [
            ("Máscara de tratamento intensivo", "Ajuda a melhorar a maciez dos fios.", 150.00),
            ("Gelatina para definição", "Ajuda na definição dos cachos.", 75.00),
            ("Creme de pentear para cachos", "Facilita o desembaraço e a finalização.", 50.00),
            ("Óleo vegetal para cabelo", "Pode ajudar na finalização dos fios.", 35.00),
            ("Shampoo hidratante", "Limpeza adequada à rotina capilar.", 28.00),
        ],
        "dica": "Desembarace delicadamente, começando pelas pontas. Experimente finalizar os cachos com os fios úmidos."
    },
    "corpo": {
        "titulo": "Cuidados com o corpo",
        "descricao": "Hidratação e cuidados para uma pele confortável e macia.",
        "produtos": [
            ("Loção corporal intensiva", "Ajuda a manter a hidratação da pele.", 110.00),
            ("Esfoliante corporal", "Ajuda a remover células superficiais da pele.", 65.00),
            ("Creme hidratante corporal", "Ajuda a reduzir o ressecamento.", 45.00),
            ("Óleo corporal", "Ajuda a manter a pele macia.", 35.00),
            ("Hidratante corporal básico", "Uma opção acessível para o dia a dia.", 22.00),
        ],
        "dica": "Hidrate a pele após o banho. Evite esfoliação agressiva, principalmente em regiões irritadas ou recém-depiladas."
    },
    "mente": {
        "titulo": "Autocuidado com a mente",
        "descricao": "Pequenos hábitos também fazem parte do seu bem-estar.",
        "produtos": [],
        "dica": "Você não precisa fazer tudo perfeitamente. Um pequeno passo por dia já pode fazer diferença."
    }
}

FRASES = [
    "Você merece o mesmo carinho que oferece às outras pessoas.",
    "Descansar também é uma forma de cuidar de si.",
    "Seu valor não depende da sua aparência.",
    "Respeite seu tempo e reconheça suas conquistas.",
    "Você não precisa ser perfeita para ser incrível.",
    "Começar de novo também é progresso."
]

HABITOS = [
    "Beber água ao longo do dia.",
    "Manter uma rotina de sono adequada.",
    "Reservar alguns minutos para descansar.",
    "Fazer uma caminhada ou alongamento, se possível.",
    "Diminuir o tempo de tela antes de dormir.",
    "Escrever seus sentimentos em um caderno.",
    "Aprender a dizer não quando necessário.",
    "Conversar com alguém de confiança quando precisar."
]


def conectar_banco():
    conexao = sqlite3.connect(BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_banco():
    with conectar_banco() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS comentarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                data TEXT NOT NULL,
                origem TEXT NOT NULL DEFAULT 'inicio'
            )
        """)

        # Adiciona a coluna origem caso o banco antigo ainda não a tenha.
        colunas = [
            linha["name"]
            for linha in conexao.execute(
                "PRAGMA table_info(comentarios)"
            ).fetchall()
        ]

        if "origem" not in colunas:
            conexao.execute("""
                ALTER TABLE comentarios
                ADD COLUMN origem TEXT NOT NULL DEFAULT 'inicio'
            """)


criar_banco()


HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Blog de autocuidado: rosto, cabelo,
    corpo, hábitos saudáveis e bem-estar.">
    <title>{{ titulo }} | Blog de Autocuidado</title>

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, sans-serif;
            background: #fff7fa;
            color: #573746;
            line-height: 1.6;
        }

        header {
            background: #f7bfd4;
            text-align: center;
            padding: 32px 15px;
        }

        header h1 {
            color: #a81758;
            font-family: Georgia, serif;
            font-size: clamp(28px, 6vw, 44px);
        }

        header p {
            margin-top: 8px;
        }

        nav {
            background: #e83e83;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 5px;
            padding: 12px;
        }

        nav a {
            color: white;
            text-decoration: none;
            padding: 9px 12px;
            border-radius: 20px;
            font-size: 14px;
        }

        nav a:hover {
            background: #b91e60;
        }

        .banner {
            background: linear-gradient(135deg, #ffe0eb, #f8b4ce);
            text-align: center;
            padding: 48px 20px;
        }

        .banner h2 {
            font-family: Georgia, serif;
            color: #a81758;
            font-size: clamp(26px, 5vw, 38px);
            margin-bottom: 12px;
        }

        .banner p {
            max-width: 650px;
            margin: auto;
        }

        main {
            max-width: 1100px;
            margin: auto;
            padding: 28px 16px;
        }

        h2.secao {
            color: #b51e62;
            font-family: Georgia, serif;
            font-size: 28px;
            margin-bottom: 18px;
        }

        .categorias, .produtos {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
            margin-bottom: 35px;
        }

        .categoria, .produto, .painel {
            background: white;
            border-radius: 18px;
            padding: 22px;
            box-shadow: 0 4px 15px #8b355515;
        }

        .categoria {
            border-top: 5px solid #ed79a8;
            text-decoration: none;
            color: inherit;
            transition: transform 0.2s;
        }

        .categoria:hover {
            transform: translateY(-4px);
        }

        .categoria .emoji {
            font-size: 36px;
        }

        .categoria h3, .produto h3 {
            color: #b51e62;
            margin: 8px 0;
        }

        .produto {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .preco {
            color: #c21c62;
            font-size: 21px;
            font-weight: bold;
            margin-top: auto;
        }

        .aviso {
            background: #ffe7f0;
            padding: 16px;
            border-radius: 12px;
            margin: 20px 0;
        }

        .painel {
            margin-bottom: 25px;
        }

        .painel h3 {
            color: #b51e62;
            margin-bottom: 12px;
        }

        .lista-habitos {
            padding-left: 22px;
        }

        blockquote {
            background: #ffe7f0;
            border-left: 5px solid #e83e83;
            padding: 18px;
            margin: 12px 0;
            font-family: Georgia, serif;
            font-size: 19px;
        }

        form {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-top: 18px;
        }

        input, textarea {
            width: 100%;
            padding: 13px;
            border: 1px solid #e6afc6;
            border-radius: 10px;
            font: inherit;
        }

        textarea {
            min-height: 110px;
            resize: vertical;
        }

        button {
            background: #e83e83;
            color: white;
            padding: 13px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
        }

        button:hover {
            background: #b91e60;
        }

        .comentario {
            border-bottom: 1px solid #f2d4e0;
            padding: 16px 0;
            overflow-wrap: anywhere;
        }

        .comentario strong {
            color: #b51e62;
        }

        .data {
            font-size: 12px;
            color: #8b7480;
        }

        .voltar {
            color: #b51e62;
            display: inline-block;
            margin-bottom: 18px;
        }

        footer {
            background: #f7bfd4;
            text-align: center;
            padding: 28px 15px;
            margin-top: 25px;
        }

        footer a {
            color: #8d174b;
        }

        @media (max-width: 480px) {
            .categorias, .produtos {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>
    <header>
        <h1>♡ Blog de Autocuidado ♡</h1>
        <p>Um espaço para cuidar de você, por dentro e por fora.</p>
    </header>

    <nav>
        <a href="/">Início</a>
        <a href="/categoria/rosto">Rosto</a>
        <a href="/categoria/cabelo-liso">Cabelo liso</a>
        <a href="/categoria/cabelo-cacheado">Cabelo cacheado</a>
        <a href="/categoria/corpo">Corpo</a>
        <a href="/categoria/mente">Mente</a>
        <a href="/#comentarios">Comentários</a>
    </nav>

    {% if inicio %}
    <section class="banner">
        <h2>Seu momento de autocuidado</h2>
        <p>
            Descubra dicas, produtos e hábitos para construir uma rotina
            de autocuidado que combine com você. Beleza também é se sentir bem.
        </p>
    </section>
    {% endif %}

    <main>
        {% if inicio %}
            <h2 class="secao">Explore nossas categorias ♡</h2>

            <section class="categorias">
                {% for chave, categoria in categorias.items() %}
                <a class="categoria" href="/categoria/{{ chave }}">
                    <div class="emoji">
                        {% if chave == 'rosto' %}🌸
                        {% elif chave == 'cabelo-liso' %}💇🏻‍♀️
                        {% elif chave == 'cabelo-cacheado' %}🦱
                        {% elif chave == 'corpo' %}🧴
                        {% else %}🧠{% endif %}
                    </div>
                    <h3>{{ categoria.titulo }}</h3>
                    <p>{{ categoria.descricao }}</p>
                    <p><strong>Descobrir dicas →</strong></p>
                </a>
                {% endfor %}
            </section>

            <section class="painel">
                <h2 class="secao">Inspire-se hoje ✨</h2>
                <blockquote>{{ frase }}</blockquote>
            </section>

            <section class="painel">
                <h2 class="secao">Hábitos para cuidar da mente</h2>
                <ul class="lista-habitos">
                    {% for habito in habitos %}
                    <li>{{ habito }}</li>
                    {% endfor %}
                </ul>
            </section>

        {% else %}
            <a class="voltar" href="/">← Voltar ao início</a>

            <h2 class="secao">{{ categoria.titulo }}</h2>
            <p>{{ categoria.descricao }}</p>

            {% if chave == 'mente' %}
                <section class="painel">
                    <h3>Frases para lembrar ♡</h3>
                    {% for frase_item in frases %}
                    <blockquote>{{ frase_item }}</blockquote>
                    {% endfor %}
                </section>

                <section class="painel">
                    <h3>Hábitos simples para experimentar</h3>
                    <ul class="lista-habitos">
                        {% for habito in habitos %}
                        <li>{{ habito }}</li>
                        {% endfor %}
                    </ul>
                </section>
            {% else %}
                <h3 style="margin: 24px 0 12px; color: #b51e62;">
                    Produtos do mais caro ao mais barato
                </h3>

                <div class="produtos">
                    {% for nome, descricao, preco in categoria.produtos|sort(attribute=2, reverse=true) %}
                    <article class="produto">
                        <h3>{{ nome }}</h3>
                        <p>{{ descricao }}</p>
                        <p class="preco">
                            R$ {{ "%.2f"|format(preco)|replace(".", ",") }}
                        </p>
                        <small>Preço ilustrativo; consulte as lojas.</small>
                    </article>
                    {% endfor %}
                </div>

                <div class="aviso">
                    <strong>Dica de autocuidado:</strong>
                    {{ categoria.dica }}
                </div>
            {% endif %}
        {% endif %}

        <section class="painel" id="comentarios">
            <h2 class="secao">♡ Comentários dos visitantes</h2>
            <p>Compartilhe sua experiência, dica ou mensagem com a comunidade.</p>

            <form action="/comentar" method="POST">
                <input type="text" name="nome" maxlength="60"
                       placeholder="Seu nome ou apelido" required>

                <textarea name="mensagem" maxlength="1000"
                          placeholder="Escreva seu comentário..."
                          required></textarea>

                <input type="hidden" name="origem" value="{{ origem }}">

                <button type="submit">Publicar comentário ♡</button>
            </form>

            <p style="margin-top: 18px;">
                <strong>{{ comentarios|length }}</strong>
                comentário(s) nesta página.
            </p>

            {% for comentario in comentarios %}
            <article class="comentario">
                <strong>{{ comentario.nome }}</strong>
                <p class="data">{{ comentario.data }}</p>
                <p>{{ comentario.mensagem }}</p>
            </article>
            {% else %}
                <p style="margin-top: 15px;">
                    Ainda não há comentários. Seja a primeira pessoa a comentar!
                </p>
            {% endfor %}
        </section>
    </main>

    <footer>
        <h3>♡ Blog de Autocuidado ♡</h3>
        <p>Cuide de você com carinho, no seu tempo.</p>
        <p>Conteúdo informativo. Cada pele e cabelo têm necessidades diferentes.</p>
        <p>© 2026 Blog de Autocuidado</p>
    </footer>
</body>
</html>
"""


def buscar_comentarios(origem):
    with conectar_banco() as conexao:
        return conexao.execute(
            """
            SELECT nome, mensagem, data
            FROM comentarios
            WHERE origem = ?
            ORDER BY id DESC
            """,
            (origem,)
        ).fetchall()


def renderizar_pagina(titulo, inicio=False, chave=None):
    categoria = PRODUTOS.get(chave, {})
    origem = chave if chave else "inicio"

    return render_template_string(
        HTML,
        titulo=titulo,
        inicio=inicio,
        categorias=PRODUTOS,
        categoria=categoria,
        chave=chave,
        origem=origem,
        frase=FRASES[datetime.now().day % len(FRASES)],
        frases=FRASES,
        habitos=HABITOS,
        comentarios=buscar_comentarios(origem)
    )


@app.route("/")
def inicio():
    return renderizar_pagina("Início", inicio=True)


@app.route("/categoria/<chave>")
def mostrar_categoria(chave):
    if chave not in PRODUTOS:
        return "Categoria não encontrada.", 404

    return renderizar_pagina(PRODUTOS[chave]["titulo"], chave=chave)


@app.route("/comentar", methods=["POST"])
def comentar():
    nome = request.form.get("nome", "").strip()
    mensagem = request.form.get("mensagem", "").strip()
    origem = request.form.get("origem", "inicio").strip()

    if origem not in ["inicio"] + list(PRODUTOS.keys()):
        origem = "inicio"

    if not nome or not mensagem:
        return "Preencha o nome e o comentário.", 400

    if len(nome) > 60 or len(mensagem) > 1000:
        return "O nome ou comentário ultrapassou o limite permitido.", 400

    with conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO comentarios (nome, mensagem, data, origem)
            VALUES (?, ?, ?, ?)
            """,
            (
                nome,
                mensagem,
                datetime.now().strftime("%d/%m/%Y às %H:%M"),
                origem
            )
        )

    return redirect("/#comentarios" if origem == "inicio"
                    else f"/categoria/{origem}#comentarios")


if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta, debug=False)