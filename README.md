#  Agente de IA para Lógica Proposicional (CPC)
  
Aluno: *BRUNO ALVES (26193)*

---

##  Objetivo

Implementar um **Agente de IA para Web** que:

1. **Modo NL → CPC**  
   Receber frases simples em português e traduzi-las para **fórmulas do Cálculo Proposicional Clássico (CPC)**.

2. **Modo CPC → NL**  
   Receber uma fórmula lógica e traduzi-la para uma **frase coerente em português**, utilizando significados definidos pelo usuário para as proposições `P`, `Q` e `R`.

---

##  Arquitetura do Sistema

- **Frontend + Backend integrados** via Streamlit  
- Interface dividida em **duas abas**:
  - “Português → Lógica (NL → CPC)”
  - “Lógica → Português (CPC → NL)”
- **Barra lateral** permite que a pessoa defina os significados de:
  - `P`
  - `Q`
  - `R`

---

##  Site Online

link: https://agentedeia-zqdqdnmjgnb88mwynjpsch.streamlit.app

---

### Desenho simplificado

```text
Usuário (navegador)
   ↓
Interface Web (Streamlit)
   ├── Modo NL → CPC
   │     └── Regras baseadas em padrões de linguagem natural
   └── Modo CPC → NL
         └── Parser recursivo de fórmulas proposicionais
