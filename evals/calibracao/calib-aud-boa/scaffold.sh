#!/usr/bin/env bash
# Coloca no workspace uma auditoria real da v3.2.0, que deve aprovar.
set -e
here="$(cd "$(dirname "$0")" && pwd)"
cp "$here/resposta.md" ./resposta.md
