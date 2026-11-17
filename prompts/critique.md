# Prompt — Análise crítica do briefing

Objetivo: encontrar o que está faltando, ambíguo ou contraditório. **Não** propor solução,
**não** preencher lacuna, **não** escrever requisito ainda.

Entrada: `brief.md` do projeto.
Saída: itens em `questions.md` e, no máximo, um resumo de 10 linhas.

## Procure, nesta ordem

1. **Lacuna** — informação necessária para especificar que não está no texto. Em especial:
   quem pode fazer o quê, o que acontece no caso de erro, o que acontece com dado
   existente, qual o volume esperado, quem é o dono da regra.
2. **Ambiguidade** — termo que admite mais de uma leitura. "Rápido", "simples",
   "automático", "integrado", "relatório", "usuário". Cada um precisa de definição.
3. **Contradição** — duas afirmações que não podem ser verdade juntas. Compare o escopo
   com o fora-de-escopo, e os critérios de sucesso com as restrições.
4. **Suposição implícita** — algo tratado como óbvio que não é. "O cliente já tem os
   dados", "é só exibir", "igual ao sistema atual".
5. **Risco** — o que pode inviabilizar o projeto e ainda não foi considerado.
6. **Escopo inflado** — funcionalidade imaginada que não serve nenhum critério de sucesso
   declarado. Aponte; não remova.

## Regras

- Lacuna gera **pergunta**, nunca valor preenchido por você. Nenhuma suposição silenciosa.
- Uma pergunta por lacuna, respondível em uma ou duas frases. Pergunta ampla
  ("como deve funcionar o módulo financeiro?") é inútil — quebre.
- Marque `blocking: true` só quando implementar sem a resposta significaria adivinhar algo
  que depois exigiria retrabalho estrutural.
- Contradição é reportada, nunca resolvida por você.
- Priorize: 10 perguntas certas valem mais que 40. Se passar de 15, você está perguntando
  detalhe de implementação.
