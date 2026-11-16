#!/usr/bin/env bash
# Copia o cliente fictício da suíte de auditoria para o workspace.
set -e
here="$(cd "$(dirname "$0")" && pwd)"
cp -r "$here/../auditoria-fixture/fixture/ClinicaAurora" ./ClinicaAurora
mkdir -p ClinicaAurora/relatorios
cp "$here/plano-correcao.md" ClinicaAurora/relatorios/plano-correcao.md
