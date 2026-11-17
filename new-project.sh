#!/usr/bin/env bash
# Uso: ./new-project.sh <slug> "<Nome>" [light|full]
set -euo pipefail
cd "$(dirname "$0")"
slug=${1:?slug obrigatorio}; name=${2:?nome obrigatorio}; track=${3:-light}
[[ $slug =~ ^[a-z0-9-]+$ ]] || { echo "slug: so minuscula, numero e hifen"; exit 1; }
[[ $track == light || $track == full ]] || { echo "track: light ou full"; exit 1; }
dir=projects/$slug
[[ -e $dir ]] && { echo "$dir ja existe"; exit 1; }

mkdir -p "$dir"/{requirements,rules,use-cases,decisions,tests,processes}
cp templates/brief.md templates/questions.md "$dir/"
cp templates/domain-model.md "$dir/domain-model.md"
cp templates/architecture.md templates/plan.md "$dir/"
sed -e "s/^slug: .*/slug: $slug/" -e "s/^name: .*/name: $name/" \
    -e "s/^track: .*/track: $track/" -e "s/YYYY-MM-DD/$(date +%F)/" \
    templates/project.yaml > "$dir/project.yaml"
[[ $track == full ]] && sed -i '/^stages:/a\  product: pending\n  use-cases: pending\n  processes: pending\n  data: pending\n  interfaces: pending\n  tests: pending' "$dir/project.yaml"

echo "criado $dir (trilha $track)"
echo "1. preencha $dir/brief.md"
echo "2. rode o prompt prompts/critique.md sobre ele"
echo "3. python3 validate.py $dir"
