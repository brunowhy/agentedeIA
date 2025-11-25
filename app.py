import re
import streamlit as st
from dataclasses import dataclass


@dataclass
class Node:
    type: str           
    value: str = None   
    left: 'Node' = None
    right: 'Node' = None


def tokenize(formula: str):
    """
    Transforma a fórmula em uma lista de tokens.
    Aceita conectivos em diferentes formas, por exemplo:
    - ∧, ^, &
    - ∨, v, |
    - ¬, ~, !
    - →, ->, ⇒
    - ↔, <-> 
    """
    s = formula.replace(" ", "")
    tokens = []
    i = 0
    while i < len(s):
        c = s[i]
        
        if s.startswith("<->", i):
            tokens.append("<->")
            i += 3
        elif s.startswith("->", i):
            tokens.append("->")
            i += 2
        elif c in "PQR":
            tokens.append(c)
            i += 1
        elif c in "()":
            tokens.append(c)
            i += 1
        elif c in "¬~!":
            tokens.append("NOT")
            i += 1
        elif c in "∧^&":
            tokens.append("AND")
            i += 1
        elif c in "∨v|":
            tokens.append("OR")
            i += 1
        elif c in "→⇒":
            tokens.append("->")
            i += 1
        elif c in "↔":
            tokens.append("<->")
            i += 1
        else:
            raise ValueError(f"Caractere inesperado na fórmula: {c}")
    return tokens


def parse_formula(formula: str) -> Node:
    """
    Parser recursivo simples para fórmulas proposicionais
    com conectivos: ¬, ∧, ∨, →, ↔ e parênteses.
    """
    tokens = tokenize(formula)
    i = 0  

    def parse_expr():
        return parse_equiv()

    def parse_equiv():
        nonlocal i
        node = parse_imp()
        while i < len(tokens) and tokens[i] == "<->":
            i += 1
            right = parse_imp()
            node = Node("iff", left=node, right=right)
        return node

    def parse_imp():
        nonlocal i
        node = parse_or()
        while i < len(tokens) and tokens[i] == "->":
            i += 1
            right = parse_or()
            node = Node("imp", left=node, right=right)
        return node

    def parse_or():
        nonlocal i
        node = parse_and()
        while i < len(tokens) and tokens[i] == "OR":
            i += 1
            right = parse_and()
            node = Node("or", left=node, right=right)
        return node

    def parse_and():
        nonlocal i
        node = parse_not()
        while i < len(tokens) and tokens[i] == "AND":
            i += 1
            right = parse_not()
            node = Node("and", left=node, right=right)
        return node

    def parse_not():
        nonlocal i
        if i < len(tokens) and tokens[i] == "NOT":
            i += 1
            child = parse_not()
            return Node("not", left=child)
        else:
            return parse_atom()

    def parse_atom():
        nonlocal i
        if i >= len(tokens):
            raise ValueError("Fim inesperado da fórmula.")
        tok = tokens[i]
        if tok == "(":
            i += 1
            node = parse_expr()
            if i >= len(tokens) or tokens[i] != ")":
                raise ValueError("Parêntese ')' esperado.")
            i += 1
            return node
        elif tok in ("P", "Q", "R"):
            i += 1
            return Node("var", value=tok)
        else:
            raise ValueError(f"Token inesperado: {tok}")

    root = parse_expr()
    if i != len(tokens):
        raise ValueError("Tokens extras após o fim da fórmula.")
    return root


def node_to_portuguese(node: Node, mapping: dict) -> str:
    """Converte a árvore sintática em uma frase em português."""
    if node.type == "var":
        return mapping.get(node.value, node.value)
    if node.type == "not":
        inner = node_to_portuguese(node.left, mapping)
        return f"não {inner}"
    if node.type == "and":
        left = node_to_portuguese(node.left, mapping)
        right = node_to_portuguese(node.right, mapping)
        return f"{left} e {right}"
    if node.type == "or":
        left = node_to_portuguese(node.left, mapping)
        right = node_to_portuguese(node.right, mapping)
        return f"{left} ou {right}"
    if node.type == "imp":
        left = node_to_portuguese(node.left, mapping)
        right = node_to_portuguese(node.right, mapping)
        return f"Se {left}, então {right}"
    if node.type == "iff":
        left = node_to_portuguese(node.left, mapping)
        right = node_to_portuguese(node.right, mapping)
        return f"{left} se e somente se {right}"
    raise ValueError("Tipo de nó desconhecido.")



def clean_phrase(p: str) -> str:
    return p.strip(" ,")


def nl_to_cpc(sentence: str):
    """
    Converte frases simples em português para fórmulas do CPC.
    Suporta padrões como:
    - Se X, então Y.
    - Se X e Y, então Z.
    - Se X ou Y, então Z.
    - X se e somente se Y.
    - não X.
    - X e Y.
    - X ou Y.
    Retorna (fórmula, mapping_proposicoes)
    """
    s = sentence.strip().lower()
    s = s.rstrip(".!?")

    
    m = re.match(r"se (.+) ent[aã]o (.+)", s)
    if m:
        antecedent = clean_phrase(m.group(1))
        consequent = clean_phrase(m.group(2))

        if " e " in antecedent:
            parts = [clean_phrase(p) for p in antecedent.split(" e ", 1)]
            mapping = {"P": parts[0], "Q": parts[1], "R": consequent}
            formula = "(P ∧ Q) → R"
        elif " ou " in antecedent:
            parts = [clean_phrase(p) for p in antecedent.split(" ou ", 1)]
            mapping = {"P": parts[0], "Q": parts[1], "R": consequent}
            formula = "(P ∨ Q) → R"
        else:
            mapping = {"P": antecedent, "Q": consequent}
            formula = "P → Q"
        return formula, mapping

    
    m = re.match(r"(.+) se e somente se (.+)", s)
    if m:
        mapping = {"P": clean_phrase(m.group(1)), "Q": clean_phrase(m.group(2))}
        return "P ↔ Q", mapping

    m = re.match(r"n[aã]o (.+)", s)
    if m:
        mapping = {"P": clean_phrase(m.group(1))}
        return "¬P", mapping

    if " e " in s:
        parts = [clean_phrase(p) for p in s.split(" e ", 1)]
        mapping = {"P": parts[0], "Q": parts[1]}
        return "P ∧ Q", mapping

    if " ou " in s:
        parts = [clean_phrase(p) for p in s.split(" ou ", 1)]
        mapping = {"P": parts[0], "Q": parts[1]}
        return "P ∨ Q", mapping

    return None, {}


def formula_to_latex(formula: str) -> str:
    """Converte a fórmula em uma string LaTeX bonitinha para exibir no Streamlit."""
    latex = (
        formula.replace("¬", r"\lnot ")
        .replace("∧", r"\land ")
        .replace("∨", r"\lor ")
        .replace("→", r"\rightarrow ")
        .replace("↔", r"\leftrightarrow ")
    )
    return latex




st.set_page_config(page_title="Agente de IA – Lógica Proposicional", layout="centered")

st.title("Agente de IA para Lógica Proposicional (CPC)")
st.write(
    """
Este agente traduz entre **Linguagem Natural (português)** e **Cálculo Proposicional Clássico (CPC)**.  
Use as abas abaixo para escolher o sentido da tradução.
"""
)

st.sidebar.header("Significados das proposições")
p_mean = st.sidebar.text_input("P significa:", "chover")
q_mean = st.sidebar.text_input("Q significa:", "a grama ficará molhada")
r_mean = st.sidebar.text_input("R significa:", "a aula será cancelada")
sidebar_mapping = {
    "P": p_mean if p_mean.strip() else "P",
    "Q": q_mean if q_mean.strip() else "Q",
    "R": r_mean if r_mean.strip() else "R",
}

tab1, tab2 = st.tabs(["Português → Lógica (NL → CPC)", "Lógica → Português (CPC → NL)"])


with tab1:
    st.subheader("Modo 1: Frase em português para fórmula lógica")

    example_sentence = "Se chover, então a grama ficará molhada."
    sentence = st.text_area(
        "Digite uma frase simples em português:",
        value=example_sentence,
        height=100,
    )

    if st.button("Traduzir para fórmula lógica", key="btn_nl2cpc"):
        if not sentence.strip():
            st.warning("Por favor, digite uma frase.")
        else:
            formula, mapping = nl_to_cpc(sentence)
            if formula is None:
                st.error(
                    "Não consegui reconhecer a estrutura dessa frase. "
                    "Tente usar modelos como: 'Se X, então Y', 'X e Y', 'X ou Y', 'não X', "
                    "'X se e somente se Y'."
                )
            else:
                st.success("Tradução realizada com sucesso!")
                st.write("**Fórmula em CPC:**")
                st.code(formula, language="text")

                try:
                    st.latex(formula_to_latex(formula))
                except Exception:
                    pass

                if mapping:
                    st.write("**Significados sugeridos das proposições:**")
                    for prop, meaning in mapping.items():
                        st.write(f"- **{prop}** = {meaning}")

                st.info(
                    "Obs.: você pode ajustar os significados de P, Q e R na barra lateral "
                    "para usar depois no modo CPC → Português."
                )


with tab2:
    st.subheader("Modo 2: Fórmula lógica para frase em português")

    example_formula = "(P ∧ Q) → R"
    formula_input = st.text_input(
        "Digite uma fórmula lógica (usando P, Q, R):",
        value=example_formula,
    )

    st.caption(
        "Dicas: você pode usar conectivos como: ¬, ∧, ∨, →, ↔ ou suas versões ->, <->, v, ^, etc."
    )

    if st.button("Traduzir para português", key="btn_cpc2nl"):
        if not formula_input.strip():
            st.warning("Por favor, digite uma fórmula lógica.")
        else:
            try:
                tree = parse_formula(formula_input)
                sentence_pt = node_to_portuguese(tree, sidebar_mapping)
                sentence_pt = sentence_pt[0].upper() + sentence_pt[1:]
                if not sentence_pt.endswith("."):
                    sentence_pt += "."
                st.success("Tradução realizada com sucesso!")
                st.write("**Frase em português:**")
                st.write(sentence_pt)
            except Exception as e:
                st.error(f"Erro ao interpretar a fórmula: {e}")
                st.info(
                    "Verifique se você usou apenas P, Q, R, parênteses e os conectivos válidos."
                )
