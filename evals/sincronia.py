# -*- coding: utf-8 -*-
"""Teste de sincronia entre as skills: as regras que existem em mais de uma cópia não podem divergir.

Uso: python evals/sincronia.py   (da raiz do repositório). Sai com código 1 se algo divergir.

Não exige texto idêntico — as skills redigem cada regra no seu contexto. Exige que cada arquivo contenha as
frases que carregam a regra, e que não contenha as que ela revogou. Ao mudar uma regra, atualize esta tabela.
"""
import hashlib
import io
import os
import sys

CRIACAO = ["skills/agv-novo-dinamico/SKILL.md", "skills/agv-novo-estatico/SKILL.md"]
TODAS = CRIACAO + ["skills/agv-auditoria/SKILL.md", "skills/agv-fix/SKILL.md", "skills/agv-novo-clinux/SKILL.md"]
MODELO = CRIACAO + ["skills/agv-auditoria/SKILL.md", "skills/agv-novo-clinux/invariantes-clinux.md"]

EXIGE = [
    (MODELO, "gpt-5.4-nano", "modelo alvo declarado"),
    (MODELO, "01/04/2027", "data de saída do nano"),
    (MODELO, "vale o default", "reasoning_effort é o default do modelo, fora do controle"),
    (CRIACAO + ["skills/agv-auditoria/SKILL.md"], "Condições de Execução", "contrato do runtime: §2 é campo da plataforma"),
    (CRIACAO, "**antes** de o", "definição de \"Não coletado\""),
    (CRIACAO, "**deliberadamente não p", "definição de \"Não se aplica\""),
    (CRIACAO, "__CONTATO__", "telefone do contato vem da plataforma"),
    (CRIACAO, "Uma variável de observações, breve, definida uma única vez", "observações padrão"),
    (CRIACAO, "Teto de escopo", "teto de escopo"),
    (TODAS, "verificar.py", "verificador único"),
    (CRIACAO + ["skills/agv-novo-clinux/SKILL.md"], "destino.pasta ...", "linha destino.pasta na ficha"),
]
PROIBE = [
    (TODAS, "default da família", "premissa antiga de reasoning_effort"),
    (TODAS, "Não declare variável de observações", "regra de observações revogada em 11/2026"),
    (TODAS, "Campos condicionais são string livre", "template antigo do manual de transbordo"),
    (TODAS, "FUNÇÃO: nome_da_funcao ====", "cabeçalho no template da §2, pago em todo turno"),
    (TODAS, "pode indicar ausência na base", "leitura antiga do retorno vazio"),
]

falhas = []
ler = lambda p: " ".join(io.open(p, encoding="utf-8").read().split())  # quebra de linha não conta
for arquivos, frase, o_que in EXIGE:
    for p in arquivos:
        if frase not in ler(p):
            falhas.append("FALTA   %-45s %s" % (p, o_que))
for arquivos, frase, o_que in PROIBE:
    for p in arquivos:
        if frase in ler(p):
            falhas.append("SOBROU  %-45s %s" % (p, o_que))

copias = sorted(os.path.join("skills", s, "verificar.py") for s in os.listdir("skills")
                if os.path.isfile(os.path.join("skills", s, "verificar.py")))
hashes = {p: hashlib.md5(open(p, "rb").read().replace(b"\r\n", b"\n")).hexdigest() for p in copias}
if len(set(hashes.values())) > 1:
    falhas.append("DIVERGE verificar.py: " + ", ".join("%s=%s" % (p, h[:8]) for p, h in hashes.items()))
if len(copias) < 5:
    falhas.append("FALTA   verificar.py em %d de 5 skills" % len(copias))

for f in falhas:
    print(f)
print("sincronia: %s" % ("%d divergência(s)" % len(falhas) if falhas else "ok"))
sys.exit(1 if falhas else 0)
