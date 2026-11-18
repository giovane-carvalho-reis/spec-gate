#!/usr/bin/env bash
# Marca o PSP: valida, exige arvore limpa, e cria a tag do instantaneo (ADR-007).
# Uso: ./deliver.sh <slug>
set -euo pipefail
cd "$(dirname "$0")"
slug=${1:?slug obrigatorio}
dir=projects/$slug
[[ -d $dir ]] || { echo "$dir nao existe"; exit 1; }

# O PSP e um instantaneo que passou os gates. Sem gate verde nao ha entrega.
python3 validate.py "$dir" || { echo; echo "Entrega bloqueada. Corrija e rode de novo."; exit 1; }

# Instantaneo precisa ser identificavel: arvore suja nao e um commit.
if [[ -n $(git status --porcelain "$dir") ]]; then
  echo "erro: ha mudanca nao commitada em $dir. Commite antes de entregar."
  exit 1
fi

last=$(git tag --list "psp/$slug/v*" | sed "s|psp/$slug/v||" | sort -n | tail -1)
next=$(( ${last:-0} + 1 ))
tag="psp/$slug/v$next"
commit=$(git rev-parse --short HEAD)

git tag -a "$tag" -m "PSP $slug v$next — todos os gates verdes"
echo
echo "PSP marcado: $tag  (commit $commit)"
echo "  entregue assim:  git archive $tag -- $dir"
echo "  push da tag:     git push origin $tag"
