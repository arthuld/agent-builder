#!/usr/bin/env bash
# Coloca no workspace uma auditoria fraca, escrita de proposito para reprovar.
set -e
here="$(cd "$(dirname "$0")" && pwd)"
cp "$here/resposta.md" ./resposta.md
