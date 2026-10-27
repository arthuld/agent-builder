#!/usr/bin/env bash
# A rodada começa num workspace vazio e não enxerga a pasta do caso.
# O script se localiza pelo próprio caminho e copia o cliente fictício para o workspace.
set -e
here="$(cd "$(dirname "$0")" && pwd)"
cp -r "$here/fixture/ClinicaAurora" ./ClinicaAurora
