#!/usr/bin/env bash
# Uso: ./new-project.sh <slug> "<Nome>" [light|full]
set -euo pipefail
cd "$(dirname "$0")"
slug=${1:?slug obrigatorio}; name=${2:?nome obrigatorio}; track=${3:-light}
[[ $slug =~ ^[a-z0-9-]+$ ]] || { echo "slug: so minuscula, numero e hifen"; exit 1; }
[[ $track == light || $track == full ]] || { echo "track: light ou full"; exit 1; }
dir=projects/$slug
[[ -e $dir ]] && { echo "$dir ja existe"; exit 1; }

# Documentos por trilha — espelha TRACK_STAGES/TRACK_DOCS em validate.py
light_docs=(brief.md questions.md domain-model.md architecture.md plan.md)
full_docs=("${light_docs[@]}" product.md data-model.md interfaces.md test-strategy.md)
extra_stages=(product use-cases processes data interfaces tests)

mkdir -p "$dir"/{requirements,rules,use-cases,decisions,tests,processes}
docs=("${light_docs[@]}"); [[ $track == full ]] && docs=("${full_docs[@]}")
for f in "${docs[@]}"; do cp "templates/$f" "$dir/$f"; done

sed -e "s/^slug: .*/slug: $slug/" -e "s/^name: .*/name: $name/" \
    -e "s/^track: .*/track: $track/" -e "s/YYYY-MM-DD/$(date +%F)/" \
    templates/project.yaml > "$dir/project.yaml"
if [[ $track == full ]]; then
  for s in "${extra_stages[@]}"; do sed -i "/^stages:/a\\  $s: pending" "$dir/project.yaml"; done
fi

echo "criado $dir (trilha $track, ${#docs[@]} documentos)"
echo "1. preencha $dir/brief.md"
echo "2. /spec-critique $slug"
echo "3. python3 validate.py $dir"
