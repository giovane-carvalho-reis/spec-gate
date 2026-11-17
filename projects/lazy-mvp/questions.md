# Perguntas abertas

Lacuna identificada que ainda não tem resposta. `blocking: true` impede a aprovação do
PSP (gate G5).

<!-- questions -->
```yaml
- id: Q-001
  question: Qual projeto real sera o primeiro a atravessar as 12 skills? Define se os templates aguentam um caso de verdade.
  blocking: false
  raised_by: critique
  answer:
- id: Q-002
  question: Propagacao de stale e manual. Automatizar exige grafo de dependencia — vale antes de doer?
  blocking: false
  raised_by: critique
  answer: Nao. Fica manual ate que o esquecimento cause um PSP aprovado incoerente.
- id: Q-003
  question: spec-traceability sobrepoe parte do validate.py. Mantem os quatro subagentes ou corta?
  blocking: false
  raised_by: critique
  answer: Mantem escopado para cobertura semantica. Corta se na pratica so repetir o script.
```
