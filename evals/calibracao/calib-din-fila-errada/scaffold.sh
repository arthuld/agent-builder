#!/usr/bin/env bash
# Coloca no workspace um agente.md conhecido, certo ou estragado de proposito.
set -e
here="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$(dirname "Clientes/ClinicaBoaVista/config/agente.md")"
cp "$here/agente.md" "Clientes/ClinicaBoaVista/config/agente.md"
