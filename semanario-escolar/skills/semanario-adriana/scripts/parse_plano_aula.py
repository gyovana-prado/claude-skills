#!/usr/bin/env python3
"""
Parser de Plano de Aula (formato Adriana — CPB).

Extrai do .docx do plano de aula um JSON estruturado com:
- Cabeçalho: ano, bimestre, plano, capítulo, texto, páginas, duração, materiais
- Objetos de conhecimento (lista)
- Habilidades BNCC por categoria (Leitura/escuta, Escrita, Análise linguística/semiótica, Oralidade, etc.)
- Objetivos de aprendizagem
- Princípios e valores
- Interdisciplinaridade
- Materiais, tecnologias e recursos
- Aulas (AULA 1 ... AULA N) com Introdução / Desenvolvimento / Conclusão / Tarefa de casa
- Verificação da aprendizagem
- Referências

Uso:
    uv run --with python-docx python parse_plano_aula.py <input.docx> [output.json]

Se output não for fornecido, imprime no stdout.
"""

import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def extrair_paragrafos(docx_path: Path) -> list[str]:
    """Extrai a lista de parágrafos de texto do .docx (sem usar python-docx)."""
    import zipfile

    with zipfile.ZipFile(docx_path) as z:
        with z.open("word/document.xml") as f:
            tree = ET.parse(f)

    paragrafos = []
    root = tree.getroot()
    for p in root.iter(f"{{{NS['w']}}}p"):
        texts = []
        for t in p.iter(f"{{{NS['w']}}}t"):
            if t.text:
                texts.append(t.text)
        texto_paragrafo = "".join(texts).strip()
        if texto_paragrafo:
            paragrafos.append(texto_paragrafo)
    return paragrafos


# ── Detectores de seção ──────────────────────────────────────────────

RE_AULA = re.compile(r"^AULA\s+(\d+)\s*$", re.IGNORECASE)
RE_SUBSECAO_AULA = re.compile(r"^(\d+)\s*[.)]\s*(Introdu[çc][aã]o|Desenvolvimento|Conclus[aã]o|Tarefa de casa)\s*$", re.IGNORECASE)
RE_CODIGO_BNCC = re.compile(r"\((EF\d{2,3}[A-Z]{2}\d{1,3}[^)]*)\)")

SECOES_CABECALHO = {
    "ano": re.compile(r"^Ano\s*:\s*(.+)", re.IGNORECASE),
    "bimestre": re.compile(r"^Bimestre\s*:\s*(.+)", re.IGNORECASE),
    "plano_aula": re.compile(r"^Plano\s+de\s+aula\s*:\s*(.+)", re.IGNORECASE),
    "capitulo": re.compile(r"^Cap[ií]tulo\s+(.+)", re.IGNORECASE),
    "texto": re.compile(r"^Texto\s*:\s*(.+)", re.IGNORECASE),
    "paginas": re.compile(r"^P[aá]ginas?\s*:\s*(.+)", re.IGNORECASE),
    "orientacoes": re.compile(r"^Orienta[çc][õo]es\s+did[áa]ticas\s*:\s*(.+)", re.IGNORECASE),
    "duracao": re.compile(r"^Dura[çc][aã]o.*?:\s*(.+)", re.IGNORECASE),
}

MARCADORES_SECAO = {
    "Objetos de conhecimento": "objetos_conhecimento",
    "Habilidades BNCC": "habilidades_bncc",
    "Objetivos de aprendizagem": "objetivos_aprendizagem",
    "Princípios e valores": "principios_valores",
    "Interdisciplinaridade": "interdisciplinaridade",
    "Materiais, tecnologias, recursos": "materiais_recursos",
    "Materiais, tecnologias e recursos": "materiais_recursos",
    "Verificação da aprendizagem": "verificacao_aprendizagem",
    "Autoavaliação": "autoavaliacao",
    "Referências": "referencias",
    "Para aprofundamento do professor": "aprofundamento_professor",
}

# Subcategorias de BNCC (LP) — agrupa por prática de linguagem
CATEGORIAS_BNCC = [
    "Leitura/escuta",
    "Leitura / escuta",
    "Leitura",
    "Escrita",
    "Análise linguística/ semiótica",
    "Análise linguística / semiótica",
    "Análise linguística e semiótica",
    "Análise linguística",
    "Oralidade",
    "Produção de textos",
    # Matemática
    "Números",
    "Álgebra",
    "Geometria",
    "Grandezas e medidas",
    "Probabilidade e estatística",
]


def detectar_marcador_secao(p: str) -> str | None:
    p_norm = p.strip().rstrip(":").strip()
    for marcador, chave in MARCADORES_SECAO.items():
        if p_norm.lower() == marcador.lower():
            return chave
    return None


def detectar_categoria_bncc(p: str) -> str | None:
    p_norm = p.strip().rstrip(":").strip()
    for cat in CATEGORIAS_BNCC:
        if p_norm.lower() == cat.lower():
            return cat
    return None


def parse_cabecalho(paragrafos: list[str], i: int, dest: dict) -> int:
    """Tenta casar cada padrão de cabeçalho na linha. Retorna i + 1 sempre."""
    p = paragrafos[i]
    for chave, regex in SECOES_CABECALHO.items():
        m = regex.match(p)
        if m:
            dest[chave] = m.group(1).strip()
            return i + 1
    return i + 1


def parse_bncc_section(paragrafos: list[str], inicio: int) -> tuple[dict, int]:
    """Parseia o bloco de Habilidades BNCC. Retorna (dict_por_categoria, próximo_índice)."""
    por_categoria: dict[str, list[dict]] = {}
    categoria_atual = "Geral"
    i = inicio
    while i < len(paragrafos):
        p = paragrafos[i]
        if detectar_marcador_secao(p) or RE_AULA.match(p):
            break
        cat = detectar_categoria_bncc(p)
        if cat:
            categoria_atual = cat
            por_categoria.setdefault(categoria_atual, [])
            i += 1
            continue
        m = RE_CODIGO_BNCC.match(p)
        if m:
            codigo = m.group(1)
            descricao = p[m.end():].strip()
            por_categoria.setdefault(categoria_atual, []).append({
                "codigo": codigo,
                "descricao": descricao,
            })
        i += 1
    return por_categoria, i


def parse_lista_simples(paragrafos: list[str], inicio: int) -> tuple[list[str], int]:
    """Lê itens consecutivos até o próximo marcador de seção ou AULA. Retorna (lista, próximo_índice)."""
    itens = []
    i = inicio
    while i < len(paragrafos):
        p = paragrafos[i]
        if detectar_marcador_secao(p) or RE_AULA.match(p) or detectar_categoria_bncc(p):
            break
        itens.append(p)
        i += 1
    return itens, i


def parse_aula(paragrafos: list[str], inicio: int, numero_aula: str) -> tuple[dict, int]:
    """Parseia uma aula. Retorna (dict_aula, próximo_índice).

    Estrutura esperada:
        AULA N
        1.Introdução
        ... parágrafos ...
        2.Desenvolvimento
        ... parágrafos ...
        3.Conclusão
        ... parágrafos ...
        4.Tarefa de casa (opcional)
        ...
    """
    aula = {
        "numero": numero_aula,
        "introducao": [],
        "desenvolvimento": [],
        "conclusao": [],
        "tarefa_casa": [],
    }
    subsecao_atual = None
    i = inicio
    while i < len(paragrafos):
        p = paragrafos[i]
        if RE_AULA.match(p):
            break
        if detectar_marcador_secao(p):
            break
        m_sub = RE_SUBSECAO_AULA.match(p)
        if m_sub:
            nome = m_sub.group(2).lower()
            if nome.startswith("introdu"):
                subsecao_atual = "introducao"
            elif nome.startswith("desenvolv"):
                subsecao_atual = "desenvolvimento"
            elif nome.startswith("conclus"):
                subsecao_atual = "conclusao"
            elif nome.startswith("tarefa"):
                subsecao_atual = "tarefa_casa"
            i += 1
            continue
        if subsecao_atual:
            aula[subsecao_atual].append(p)
        i += 1
    return aula, i


def parse_plano_aula(docx_path: Path) -> dict:
    paragrafos = extrair_paragrafos(docx_path)

    plano: dict = {
        "cabecalho": {},
        "objetos_conhecimento": [],
        "habilidades_bncc": {},
        "objetivos_aprendizagem": [],
        "principios_valores": [],
        "interdisciplinaridade": [],
        "materiais_recursos": [],
        "aulas": [],
        "verificacao_aprendizagem": [],
        "autoavaliacao": [],
        "referencias": [],
        "aprofundamento_professor": [],
    }

    i = 0
    while i < len(paragrafos):
        p = paragrafos[i]

        # Cabeçalho
        if any(regex.match(p) for regex in SECOES_CABECALHO.values()):
            i = parse_cabecalho(paragrafos, i, plano["cabecalho"])
            continue

        # AULA N
        m_aula = RE_AULA.match(p)
        if m_aula:
            aula, i_next = parse_aula(paragrafos, i + 1, m_aula.group(1))
            plano["aulas"].append(aula)
            i = i_next
            continue

        # Seções nomeadas
        chave = detectar_marcador_secao(p)
        if chave:
            if chave == "habilidades_bncc":
                bncc, i_next = parse_bncc_section(paragrafos, i + 1)
                plano["habilidades_bncc"] = bncc
            else:
                lista, i_next = parse_lista_simples(paragrafos, i + 1)
                plano[chave] = lista
            i = i_next
            continue

        i += 1

    return plano


def main():
    if len(sys.argv) < 2:
        print("Uso: parse_plano_aula.py <input.docx> [output.json]")
        sys.exit(1)
    docx_path = Path(sys.argv[1])
    if not docx_path.exists():
        print(f"Arquivo não encontrado: {docx_path}")
        sys.exit(1)

    plano = parse_plano_aula(docx_path)
    saida = json.dumps(plano, ensure_ascii=False, indent=2)

    if len(sys.argv) >= 3:
        Path(sys.argv[2]).write_text(saida, encoding="utf-8")
        n_aulas = len(plano["aulas"])
        cab = plano["cabecalho"]
        print(f"Plano parseado: cap.{cab.get('capitulo', '?')} — {n_aulas} aulas")
        print(f"Salvo em {sys.argv[2]}")
    else:
        print(saida)


if __name__ == "__main__":
    main()
