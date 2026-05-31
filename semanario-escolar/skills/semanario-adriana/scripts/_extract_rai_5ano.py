#!/usr/bin/env python3
"""
Extrator único do RAI ebook → competencias_rai_5ano.json.

Rodar apenas uma vez para popular o banco. Resultado pode ser refinado manualmente.

Uso:
    uv run --with pypdf python _extract_rai_5ano.py <pdf_path> <output_json>
"""

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

# Páginas (índice pypdf 0-based) onde 5º ano aparece, por matéria
SECOES = {
    "lingua_portuguesa": {
        "nome_display": "LING. PORT.",
        "paginas": list(range(124, 133)),
        "categorias_conhecidas": [
            "Oralidade",
            "Leitura",
            "Análise linguística e semiótica",
            "Análise linguística",
            "Produção de textos",
        ],
    },
    "matematica": {
        "nome_display": "MATEMÁTICA",
        "paginas": [215, 216, 217],
        "categorias_conhecidas": [
            "Números",
            "Álgebra",
            "Geometria",
            "Grandezas e medidas",
            "Probabilidade e estatística",
        ],
    },
    "ciencias": {
        "nome_display": "CIÊNCIAS",
        "paginas": [231],
        "categorias_conhecidas": [
            "Matéria e energia",
            "Vida e evolução",
            "Terra e Universo",
        ],
    },
    "geografia": {
        "nome_display": "GEOGRAFIA",
        "paginas": [242],
        "categorias_conhecidas": [
            "O sujeito e seu lugar no mundo",
            "Conexões e escalas",
            "Mundo do trabalho",
            "Formas de representação",
            "Natureza, ambientes e qualidade de vida",
        ],
    },
    "historia": {
        "nome_display": "HISTÓRIA",
        "paginas": [257],
        "categorias_conhecidas": [
            "Povos e culturas",
            "Registros da história",
            "As questões históricas relativas às migrações",
        ],
    },
    "ensino_religioso": {
        "nome_display": "ENSINO REL.",
        "paginas": [278, 279],
        "categorias_conhecidas": [
            "Deus e eu",
            "Deus, você e eu",
            "Deus, todos nós e o outro",
            "Discipulado",
        ],
    },
}

# Padrão de código de competência: (EF05LP01), (EF05MA12), (EF35LP15), (EF15LP09), (EF05CI06-EA), etc.
RE_CODIGO = re.compile(r"\((EF\d{2,3}[A-Z]{2}\d{1,3}(?:[-.]?\w*)?)\)")


def extrair_competencias_da_pagina(reader, pagina_idx, matéria_key):
    """Extrai pares (código, descrição, categoria_inferida) de uma página."""
    text = reader.pages[pagina_idx].extract_text()

    # Junta hifenização de quebra de linha: "linguís-\ntica" → "linguística"
    text = re.sub(r"-\n\s*", "", text)

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    full_text = "\n".join(lines)

    # Encontra categoria atual percorrendo o texto
    categorias_conhecidas = SECOES[matéria_key]["categorias_conhecidas"]

    competencias = []
    # Split por código: cada competência começa com (EFxxx)
    matches = list(RE_CODIGO.finditer(full_text))

    for i, m in enumerate(matches):
        codigo = m.group(1)
        # Filtra apenas competências do 5º ano (EF05*) e gerais (EF35* / EF15*)
        if not (codigo.startswith("EF05") or codigo.startswith("EF35") or codigo.startswith("EF15") or codigo.startswith("EF12")):
            continue

        # Descrição: texto entre este código e o próximo código (ou fim)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        descricao = full_text[start:end].strip()
        descricao = re.sub(r"\s+", " ", descricao).strip()
        descricao = re.sub(r"\d+\s*\|\s*$", "", descricao).strip()
        # Remove sequências de "x" das colunas Campos de atuação (ex: "x x x x x")
        descricao = re.sub(r"\b(?:x\s+){2,}x?\b", "", descricao).strip()
        # Remove tailing texto que parece ser próximo objeto de conhecimento (heurística:
        # corta no primeiro ponto final seguido de palavra começando com maiúscula
        # que parece título, ou cortar no ponto final + descrição muito curta)
        # Vou apenas truncar no primeiro ponto final + 1 frase suspeita
        # Por enquanto: deixa como está e usuário revisa.

        # Encontra categoria: texto antes do código atual (na mesma página)
        contexto_antes = full_text[:m.start()]
        categoria_inferida = "Geral"
        for cat in categorias_conhecidas:
            # Tolerante a quebras de linha no nome da categoria
            cat_normalizado = re.sub(r"\s+", " ", cat).strip()
            ultima_pos = contexto_antes.rfind(cat_normalizado)
            if ultima_pos < 0:
                # Tenta sem espaços e com possíveis hifens
                cat_partido = cat_normalizado.replace(" ", r"[\s\-]*")
                m_cat = list(re.finditer(cat_partido, contexto_antes, re.IGNORECASE))
                if m_cat:
                    ultima_pos = m_cat[-1].start()
            if ultima_pos >= 0:
                # Categoria encontrada — escolhe a mais próxima (maior posição)
                if categoria_inferida == "Geral":
                    categoria_inferida = cat
                else:
                    pos_atual = contexto_antes.rfind(categoria_inferida)
                    if ultima_pos > pos_atual:
                        categoria_inferida = cat

        # Tipo
        tipo = "BNCC"
        if "-EA" in codigo:
            tipo = "EA"

        competencias.append({
            "codigo": codigo,
            "tipo": tipo,
            "descricao": descricao,
            "categoria": categoria_inferida,
        })

    return competencias


def construir_banco(pdf_path: Path) -> dict:
    reader = PdfReader(str(pdf_path))
    materias = {}
    for key, conf in SECOES.items():
        todas_comps = []
        vistos = set()
        for pagina in conf["paginas"]:
            comps = extrair_competencias_da_pagina(reader, pagina, key)
            for c in comps:
                if c["codigo"] not in vistos:
                    todas_comps.append(c)
                    vistos.add(c["codigo"])

        # Agrupa por categoria
        por_categoria = {}
        for c in todas_comps:
            por_categoria.setdefault(c["categoria"], []).append({
                "codigo": c["codigo"],
                "tipo": c["tipo"],
                "descricao": c["descricao"],
            })

        categorias_list = [
            {"nome": cat, "competencias": comps}
            for cat, comps in por_categoria.items()
        ]

        materias[key] = {
            "nome_display": conf["nome_display"],
            "categorias": categorias_list,
        }

    return {
        "fonte": "Referenciais Curriculares da Rede Adventista (RAI 2024), Divisão Sul-Americana da IASD",
        "ano": "5º",
        "ultima_atualizacao": "2026-05-30",
        "observacao": "Banco extraído automaticamente do PDF RAI 2024. Algumas categorias podem estar mal inferidas — corrigir manualmente quando detectado.",
        "materias": materias,
    }


def main():
    if len(sys.argv) < 3:
        print("Uso: _extract_rai_5ano.py <pdf_path> <output_json>")
        sys.exit(1)
    pdf_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    banco = construir_banco(pdf_path)
    out_path.write_text(json.dumps(banco, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(
        len(cat["competencias"])
        for m in banco["materias"].values()
        for cat in m["categorias"]
    )
    print(f"Banco salvo em {out_path}")
    print(f"Total: {total} competências")
    for k, m in banco["materias"].items():
        n = sum(len(cat["competencias"]) for cat in m["categorias"])
        cats = ", ".join(cat["nome"] for cat in m["categorias"])
        print(f"  {k}: {n} ({cats})")


if __name__ == "__main__":
    main()
