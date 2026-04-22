#!/usr/bin/env python3
"""
Gerenciador do banco de competências.
Permite adicionar, listar, consultar competências armazenadas e buscar no banco RAI.

Uso:
    python manage_competencias.py list [--materia MATERIA]
    python manage_competencias.py get --materia MATERIA --bimestre N --capitulo N
    python manage_competencias.py add --materia MATERIA --bimestre N --capitulo N --titulo TITULO --input competencias.json
    python manage_competencias.py rai --materia MATERIA [--categoria CATEGORIA] [--busca TERMO]
    python manage_competencias.py rai --materia MATERIA --codigo CODIGO
    python manage_competencias.py rai-stats
"""

import json
import sys
import argparse
from pathlib import Path


def get_db_path():
    """Find the competencias.json file (per-chapter bank)."""
    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "references" / "competencias.json"
    return db_path


def get_rai_path():
    """Find the competencias_rai_3ano.json file (master RAI bank)."""
    script_dir = Path(__file__).parent
    rai_path = script_dir.parent / "references" / "competencias_rai_3ano.json"
    return rai_path


def load_db():
    db_path = get_db_path()
    if db_path.exists():
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"versao": "1.0", "materias": {}}


def load_rai():
    """Load the RAI master competency database."""
    rai_path = get_rai_path()
    if rai_path.exists():
        with open(rai_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_db(db):
    db_path = get_db_path()
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"Banco salvo em: {db_path}")


def cmd_list(args):
    """List all stored competencies."""
    db = load_db()
    materias = db.get("materias", {})

    if args.materia:
        materias = {k: v for k, v in materias.items() if k == args.materia}

    if not materias:
        print("Nenhuma competência armazenada.")
        return

    for materia, bimestres in materias.items():
        print(f"\n{'='*60}")
        print(f"  {materia}")
        print(f"{'='*60}")
        for bim_key, capitulos in bimestres.items():
            for cap_key, cap_data in capitulos.items():
                titulo = cap_data.get("titulo", "")
                categorias = cap_data.get("categorias", {})
                total = sum(len(comps) for comps in categorias.values())
                print(f"  {bim_key} / {cap_key}: {titulo} ({total} competências)")
                for cat, comps in categorias.items():
                    print(f"    {cat}: {len(comps)} competência(s)")
                    for c in comps:
                        code = c.get("codigo_bncc", "")
                        desc = c.get("descricao", "")[:60]
                        print(f"      - ({code}) {desc}...")


def cmd_get(args):
    """Get competencies for a specific subject/chapter."""
    db = load_db()
    materias = db.get("materias", {})

    materia = materias.get(args.materia, {})
    bimestre = materia.get(f"bimestre_{args.bimestre}", {})
    capitulo = bimestre.get(f"capitulo_{args.capitulo}", {})

    if not capitulo:
        print(f"Nenhuma competência encontrada para {args.materia} bimestre {args.bimestre} capítulo {args.capitulo}")
        return

    # Output as JSON for piping
    print(json.dumps(capitulo, ensure_ascii=False, indent=2))


def cmd_add(args):
    """Add competencies from a JSON file."""
    db = load_db()

    with open(args.input, "r", encoding="utf-8") as f:
        new_data = json.load(f)

    materia_key = args.materia
    bim_key = f"bimestre_{args.bimestre}"
    cap_key = f"capitulo_{args.capitulo}"

    if materia_key not in db["materias"]:
        db["materias"][materia_key] = {}
    if bim_key not in db["materias"][materia_key]:
        db["materias"][materia_key][bim_key] = {}

    db["materias"][materia_key][bim_key][cap_key] = {
        "titulo": args.titulo or "",
        "categorias": new_data.get("categorias", new_data)
    }

    save_db(db)
    print(f"Competências adicionadas: {materia_key} {bim_key} {cap_key}")


MATERIA_ALIASES = {
    "lp": "lingua_portuguesa",
    "lingua_portuguesa": "lingua_portuguesa",
    "ling. port.": "lingua_portuguesa",
    "portugues": "lingua_portuguesa",
    "português": "lingua_portuguesa",
    "mat": "matematica",
    "matematica": "matematica",
    "matemática": "matematica",
    "cie": "ciencias",
    "ciencias": "ciencias",
    "ciências": "ciencias",
    "geo": "geografia",
    "geografia": "geografia",
    "his": "historia",
    "historia": "historia",
    "história": "historia",
    "er": "ensino_religioso",
    "ensino_religioso": "ensino_religioso",
    "ensino rel.": "ensino_religioso",
    "ensino religioso": "ensino_religioso",
}


def resolve_materia(name):
    """Resolve a matéria alias to its canonical key."""
    return MATERIA_ALIASES.get(name.lower().strip(), name.lower().strip())


def cmd_rai(args):
    """Search the RAI master competency database."""
    rai = load_rai()
    if not rai:
        print("ERRO: Banco RAI não encontrado. Verifique se competencias_rai_3ano.json existe.")
        return

    materia_key = resolve_materia(args.materia)
    materia_data = rai.get("materias", {}).get(materia_key)

    if not materia_data:
        available = list(rai.get("materias", {}).keys())
        print(f"Matéria '{args.materia}' não encontrada. Disponíveis: {', '.join(available)}")
        return

    # Search by code
    if args.codigo:
        codigo_upper = args.codigo.upper()
        for cat in materia_data.get("categorias", []):
            for obj in cat.get("objetos_conhecimento", []):
                for comp in obj.get("competencias", []):
                    if comp["codigo"].upper() == codigo_upper:
                        print(json.dumps({
                            "categoria": cat["nome"],
                            "objeto_conhecimento": obj["nome"],
                            "competencia": comp
                        }, ensure_ascii=False, indent=2))
                        return
        print(f"Código '{args.codigo}' não encontrado em {materia_key}.")
        return

    # Filter by category and/or search term
    results = []
    for cat in materia_data.get("categorias", []):
        if args.categoria and args.categoria.lower() not in cat["nome"].lower():
            continue

        for obj in cat.get("objetos_conhecimento", []):
            for comp in obj.get("competencias", []):
                if args.busca:
                    search_lower = args.busca.lower()
                    if (search_lower not in comp["descricao"].lower()
                            and search_lower not in obj["nome"].lower()
                            and search_lower not in comp["codigo"].lower()):
                        continue
                results.append({
                    "categoria": cat["nome"],
                    "objeto_conhecimento": obj["nome"],
                    "codigo": comp["codigo"],
                    "tipo": comp["tipo"],
                    "descricao": comp["descricao"],
                    "campos_atuacao": comp.get("campos_atuacao", [])
                })

    if not results:
        print("Nenhuma competência encontrada com os filtros informados.")
        return

    print(f"\n{'='*60}")
    print(f"  {materia_data['nome_display']} — {len(results)} competência(s)")
    print(f"{'='*60}")

    current_cat = ""
    for r in results:
        if r["categoria"] != current_cat:
            current_cat = r["categoria"]
            print(f"\n  [{current_cat}]")
        campos = f" [{', '.join(r['campos_atuacao'])}]" if r['campos_atuacao'] else ""
        print(f"    ({r['codigo']}) {r['descricao'][:100]}...{campos}")


def cmd_rai_stats(args):
    """Show statistics of the RAI database."""
    rai = load_rai()
    if not rai:
        print("ERRO: Banco RAI não encontrado.")
        return

    print(f"\n{'='*60}")
    print(f"  Banco RAI — {rai['ano']}")
    print(f"  Fonte: {rai['fonte']}")
    print(f"  Atualização: {rai['ultima_atualizacao']}")
    print(f"{'='*60}\n")

    total = 0
    for key, materia in rai.get("materias", {}).items():
        count = 0
        cats = []
        for cat in materia.get("categorias", []):
            cat_count = sum(len(obj.get("competencias", [])) for obj in cat.get("objetos_conhecimento", []))
            cats.append((cat["nome"], cat_count))
            count += cat_count
        total += count
        print(f"  {materia['nome_display']}: {count} competências")
        for cat_name, cat_count in cats:
            print(f"    - {cat_name}: {cat_count}")
        print()

    print(f"  TOTAL: {total} competências")


def main():
    parser = argparse.ArgumentParser(description="Gerenciador de competências")
    subparsers = parser.add_subparsers(dest="command")

    # list (per-chapter bank)
    p_list = subparsers.add_parser("list", help="Listar competências do banco por capítulo")
    p_list.add_argument("--materia", help="Filtrar por matéria")

    # get (per-chapter bank)
    p_get = subparsers.add_parser("get", help="Buscar competências por matéria/bimestre/capítulo")
    p_get.add_argument("--materia", required=True)
    p_get.add_argument("--bimestre", type=int, required=True)
    p_get.add_argument("--capitulo", type=int, required=True)

    # add (per-chapter bank)
    p_add = subparsers.add_parser("add", help="Adicionar competências ao banco por capítulo")
    p_add.add_argument("--materia", required=True)
    p_add.add_argument("--bimestre", type=int, required=True)
    p_add.add_argument("--capitulo", type=int, required=True)
    p_add.add_argument("--titulo", default="")
    p_add.add_argument("--input", required=True, help="Arquivo JSON com competências")

    # rai (master RAI bank)
    p_rai = subparsers.add_parser("rai", help="Buscar no banco RAI completo do 3º ano")
    p_rai.add_argument("--materia", required=True, help="Matéria (aceita aliases: lp, mat, cie, geo, his, er)")
    p_rai.add_argument("--categoria", help="Filtrar por categoria (ex: Oralidade, Números)")
    p_rai.add_argument("--busca", help="Buscar termo na descrição ou objeto do conhecimento")
    p_rai.add_argument("--codigo", help="Buscar competência por código exato (ex: EF03LP01)")

    # rai-stats
    p_rai_stats = subparsers.add_parser("rai-stats", help="Estatísticas do banco RAI")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "get":
        cmd_get(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "rai":
        cmd_rai(args)
    elif args.command == "rai-stats":
        cmd_rai_stats(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
