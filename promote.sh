#!/usr/bin/env bash
# Promove a trilha de um projeto de light para full. Nunca rebaixa (BR-003).
# Uso: ./promote.sh <slug>
set -euo pipefail
cd "$(dirname "$0")"
slug=${1:?slug obrigatorio}
dir=projects/$slug
y=$dir/project.yaml
[[ -f $y ]] || { echo "$y nao existe"; exit 1; }

track=$(sed -n 's/^track: *//p' "$y")
case $track in
  full) echo "$slug ja esta em full. Rebaixar e proibido (BR-003)."; exit 1 ;;
  light) ;;
  *) echo "track invalida em $y: ${track:-ausente}"; exit 1 ;;
esac

# Etapas exclusivas da full, e os Documentos de etapa que elas exigem.
extra_stages=(product use-cases processes data interfaces tests)
full_docs=(product.md data-model.md interfaces.md test-strategy.md)

sed -i 's/^track: .*/track: full/' "$y"
for s in "${extra_stages[@]}"; do
  # Etapa ja aprovada nao e tocada — promover acrescenta exigencia, nao remove.
  grep -qE "^  $s:" "$y" || sed -i "/^stages:/a\\  $s: pending" "$y"
done
for f in "${full_docs[@]}"; do
  [[ -e $dir/$f ]] || cp "templates/$f" "$dir/$f"
done
mkdir -p "$dir"/{use-cases,processes,tests}

echo "$slug promovido para full"
echo "  etapas novas: ${extra_stages[*]}"
echo "  python3 validate.py $dir"
