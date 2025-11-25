#  Agente de IA para Lógica Proposicional (CPC)

Trabalho da disciplina **Lógica para Computação – 2º Bimestre**  
Aluno: *BRUNO ALVES (26193)*

---

##  Objetivo

Este projeto implementa um **Agente de IA para Web** capaz de:

1. **Modo NL → CPC**  
   Receber frases simples em português e traduzi-las para **fórmulas do Cálculo Proposicional Clássico (CPC)**.

2. **Modo CPC → NL**  
   Receber uma fórmula lógica e traduzi-la para uma **frase coerente em português**, utilizando significados definidos pelo usuário para as proposições `P`, `Q` e `R`.

Dessa forma, o agente auxilia na compreensão dos fundamentos da **lógica formal** e suas aplicações em IA.

---

##  Arquitetura do Sistema

A aplicação é composta por um único serviço web desenvolvido em **Python** com **Streamlit**.

- **Frontend + Backend integrados** via Streamlit  
- Interface dividida em **duas abas**:
  - “Português → Lógica (NL → CPC)”
  - “Lógica → Português (CPC → NL)”
- **Barra lateral** permite que o usuário defina os significados de:
  - `P`
  - `Q`
  - `R`

### Desenho simplificado

```text
Usuário (navegador)
   ↓
Interface Web (Streamlit)
   ├── Modo NL → CPC
   │     └── Regras baseadas em padrões de linguagem natural
   └── Modo CPC → NL
         └── Parser recursivo de fórmulas proposicionais
