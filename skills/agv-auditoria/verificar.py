# -*- coding: utf-8 -*-
"""Verificação mecânica de um agente virtual (agent-builder).

Uso:   python verificar.py <pasta do cliente>
Saída: uma linha por checagem — FALHA, OK ou INFO — e a medição do sempre-ativo.
Sai com código 1 se houver alguma FALHA.

Só biblioteca padrão. A medição de tokens usa `tiktoken` (o200k_base) se estiver instalado; sem ele,
imprime "não medido" — nunca uma estimativa.

O mesmo arquivo existe nas skills de criação, de auditoria e de correção. Ao alterar um, copie para os
outros: o teste de sincronia do repositório falha se divergirem.
"""
import io
import json
import os
import re
import sys

SECOES_MANUAL = ("1. Objetivo da Função", "2. Condições de Execução")
ROTULOS_ANTIGOS = ("Descrição da Função", "Diretrizes de Prompt", "Exemplos Práticos")
DESPEDIDA = re.compile(
    r"(vou|irei) (te |lhe )?(transferir|encaminhar)|estou (te |lhe )?encaminhando|transferindo (você|voce)"
    r"|vou encerrar|até logo|ate logo|tenha um (ótimo|bom) dia", re.I)
FRASE_EXECUCAO = "Executar a função é uma ação"
TETO_SECAO1 = 950

resultados = []


def reg(nivel, texto):
    resultados.append((nivel, texto))


def ler(p):
    return io.open(p, encoding="utf-8", errors="replace").read()


def secoes(texto):
    """{título: corpo} das seções `## ` de um markdown, fora de blocos de código."""
    out, atual, buf, cerca = {}, None, [], False
    for linha in texto.split("\n"):
        if linha.strip().startswith("```"):
            cerca = not cerca
        if not cerca and linha.startswith("## "):
            if atual is not None:
                out[atual] = "\n".join(buf)
            atual, buf = linha[3:].strip(), []
        elif atual is not None:
            buf.append(linha)
    if atual is not None:
        out[atual] = "\n".join(buf)
    return out


def tokens(texto):
    try:
        import tiktoken
    except ImportError:
        return None
    return len(tiktoken.get_encoding("o200k_base").encode(" ".join(texto.split())))


def main(cli):
    agente_p = os.path.join(cli, "config", "agente.md")
    if not os.path.isfile(agente_p):
        print("FALHA  não achei config/agente.md em %s" % cli)
        return 1
    agente = ler(agente_p)
    corpo = agente[agente.find("## 1."):] if "## 1." in agente else agente
    dados = sorted(f for f in os.listdir(os.path.join(cli, "ferramentas", "dados"))
                   if f.endswith(".json")) if os.path.isdir(os.path.join(cli, "ferramentas", "dados")) else []
    base = bool(dados)
    print("Categoria: %s" % ("Base de conhecimento" if base else "Integrado"))

    # --- prompt
    sec = secoes(agente)
    n = len([s for s in sec if re.match(r"\d\.", s)])
    reg("OK" if n == 4 else "FALHA", "agente.md tem %d seções numeradas `##` (esperado 4)" % n)
    inicio = agente[:agente.find(corpo)].count("\n")
    linhas = [(inicio + i + 1, l) for i, l in enumerate(corpo.split("\n")) if "**" in l]
    # instrução que ENSINA o `**` (ex.: "destaque com **negrito**"), não o `**` usado na própria redação
    instrui = [n for n, l in linhas if re.search(r"`\*\*[^`]*\*\*`|\*\*(negrito|texto|destaque)\*\*", l, re.I) and not re.search(r"\bnunca\b|\bjamais\b|\bnão use\b", l, re.I)]
    if instrui:
        reg("FALHA", "instrução de destaque com `**` (WhatsApp mostra literal), linhas %s" % instrui[:10])
    elif linhas:
        reg("INFO", "%d linha(s) do prompt usam `**` como ênfase do próprio texto" % len(linhas))
    m = DESPEDIDA.search(corpo)
    reg(("FALHA" if base else "INFO") if m else "OK", "despedida ou aviso de transferência no prompt" + (": \"%s\"" % m.group(0) if m else ""))
    m = re.search(r"config/|ferramentas/|§\s?\d", corpo)
    reg("FALHA" if m else "OK", "caminho de arquivo ou número de seção no prompt" + (": \"%s\"" % m.group(0) if m else ""))
    m = re.search(r"</?[a-zA-Z_][a-zA-Z0-9_-]*>", corpo)
    reg("FALHA" if m else "OK", "tag XML estruturando o prompt" + (": %s" % m.group(0) if m else ""))

    if base:
        diretrizes = next((v for k, v in sec.items() if k.startswith("2.")), "")
        primeiro = re.search(r"^###\s*(.+)$", diretrizes, re.M)
        if primeiro and "Regras Críticas" in primeiro.group(1):
            bloco = re.split(r"^###", diretrizes[primeiro.end():], flags=re.M)[0]
            itens = len(re.findall(r"^\s*(?:[-*]|\d+\.)\s", bloco, re.M))
            reg("OK" if 3 <= itens <= 5 else "FALHA", "Regras Críticas abre as Diretrizes com %d itens (esperado 3 a 5)" % itens)
        else:
            reg("FALHA", "Regras Críticas não é o primeiro bloco das Diretrizes de Atendimento")
        reg("OK" if FRASE_EXECUCAO in corpo else "FALHA", "formulação literal de execução do transbordo")
        reg("OK" if re.search(r"^###.*Bordas", corpo, re.M) else "FALHA", "bloco Bordas")
        reg("OK" if "Formato da Resposta" in corpo else "FALHA", "bloco Formato da Resposta")
        obs = corpo.count("__IA_OBSERVACOES__")
        reg("OK" if obs == 1 else "FALHA", "__IA_OBSERVACOES__ citada %d vez(es) no prompt (esperado 1)" % obs)

    # --- variáveis e card
    var_p, card_p = os.path.join(cli, "config", "variaveis.md"), os.path.join(cli, "config", "clienteinfo.json")
    declaradas = set()
    if os.path.isfile(var_p):
        variaveis = ler(var_p)
        declaradas, na_tabela = set(), False
        for l in variaveis.split("\n"):
            if l.startswith("|") and "Variável" in l:
                na_tabela = True
            elif not l.startswith("|"):
                na_tabela = False
            m = na_tabela and re.match(r"^\|\s*`(_{0,2}[A-Z][A-Z0-9_]+_{0,2})`", l)
            if m:
                declaradas.add(re.sub(r"^_+|_+$", "", m.group(1)))
        tel = [l.strip()[:90] for l in (corpo + "\n" + variaveis).split("\n") if re.search(r"telefone|celular", l, re.I) and not re.search(r"\bnunca\b|\bjamais\b|\bnão use\b", l, re.I)]
        if tel:
            reg("INFO", "menção a telefone — o do contato vem em __CONTATO__; confira se é outro: %s" % tel[:3])
    else:
        reg("FALHA", "config/variaveis.md não existe")
    if os.path.isfile(card_p):
        try:
            card = json.load(io.open(card_p, encoding="utf-8"))
            reg("OK", "clienteinfo.json é JSON válido")
            bruto = ler(card_p)
            no_card = {re.sub(r"^_+|_+$", "", t) for t in re.findall(r"__([A-Z][A-Z0-9_]+)__", bruto)}
            for bloco in (b for item in card for b in item.get("informacoes", [])):
                pares = bloco.get("informacoes", [])
                if len(pares) == 2 and len(pares[0]) != len(pares[1]):
                    reg("FALHA", "card desalinhado em \"%s\": %d rótulos para %d tokens" % (bloco.get("titulo"), len(pares[0]), len(pares[1])))
            sem_decl = sorted(no_card - declaradas - {"CONTATO"})
            reg("FALHA" if sem_decl else "OK", "token do card sem variável declarada" + (": %s" % sem_decl if sem_decl else ""))
            fora = sorted(declaradas - no_card)
            if fora:
                reg("FALHA" if base else "INFO", "variável declarada e ausente do card: %s" % fora)
        except ValueError as e:
            reg("FALHA", "clienteinfo.json inválido: %s" % e)

    # --- manuais
    man_dir = os.path.join(cli, "ferramentas", "manuais")
    manuais = sorted(f for f in os.listdir(man_dir) if f.endswith(".md")) if os.path.isdir(man_dir) else []
    sempre_ativo = [corpo]
    for f in manuais:
        t = ler(os.path.join(man_dir, f))
        s = secoes(t)
        titulos = list(s)
        normal = [re.sub(r"^\d\.\s*", "", x).lower() for x in titulos]
        if normal != [re.sub(r"^\d\.\s*", "", x).lower() for x in SECOES_MANUAL]:
            antigo = any(r in " ".join(titulos) for r in ROTULOS_ANTIGOS)
            reg("FALHA", "%s: seções %s (esperado as 2 com o nome do campo)%s" % (f, titulos, " — rótulo antigo, migrar" if antigo else ""))
        if re.search(r"FUNÇÃO:", t):
            reg("FALHA", "%s: cabeçalho `FUNÇÃO:` na §2, pago em todo turno" % f)
        if "Tool Specification" in t:
            reg("FALHA", "%s: seção de JSON Schema não deveria existir" % f)
        s1 = next((v for k, v in s.items() if k.startswith("1.")), "")
        s1 = re.sub(r"^-{3,}\s*$", "", s1, flags=re.M).strip()
        if len(s1) > TETO_SECAO1:
            reg("FALHA", "%s: Objetivo da Função com %d caracteres (teto %d)" % (f, len(s1), TETO_SECAO1))
        if re.search(r"</?[a-zA-Z_][a-zA-Z0-9_-]*>", t):
            reg("FALHA", "%s: tag XML" % f)
        if re.search(r"config/|ferramentas/|§\s?\d", t):
            reg("FALHA", "%s: caminho de arquivo ou número de seção" % f)
        sempre_ativo.append("\n".join(s.values()))

    # --- dados
    for f in dados:
        p = os.path.join(cli, "ferramentas", "dados", f)
        try:
            json.load(io.open(p, encoding="utf-8"))
        except ValueError as e:
            reg("FALHA", "%s inválido: %s" % (f, e))
            continue
        t = ler(p)
        if re.search(r"\[\s*\]|\bnull\b", t):
            reg("FALHA", "%s: `[]` ou `null` — lido como \"nenhum\", use sentinela explícita" % f)

    neg = re.findall(r"[^\n]*n[ãa]o (realiza|atende|oferece)[^\n]*", corpo, re.I)
    if neg:
        reg("INFO", "%d negativa(s) no prompt — cada uma precisa de lista de exclusão do cliente" % len(neg))

    for nivel, texto in resultados:
        print("%-5s  %s" % (nivel, texto))
    n = tokens("\n".join(sempre_ativo))
    print("Sempre-ativo (4 campos + 2 seções de %d manual(is), sem o schema): %s"
          % (len(manuais), "%d tokens o200k_base" % n if n is not None else "não medido (tiktoken ausente)"))
    return 1 if any(n == "FALHA" for n, _ in resultados) else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
