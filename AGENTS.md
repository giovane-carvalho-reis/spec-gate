# AGENTS.md — como conduzir uma especificação neste repo

Este arquivo é a interface do produto. Não há aplicação: você, agente, é quem executa o
processo. Leia `docs/alignment.md` antes de agir — é o escopo que vale.

## O ciclo

```
brief.md  →  prompts/critique.md  →  questions.md  →  prompts/interview.md
   → artefatos (status: proposed)  →  aprovação humana (status: approved)
   → prompts/coherence-review.md   →  validate.py  →  PSP
```

Iterativo. Uma decisão de arquitetura pode reabrir requisito; uma regra descoberta na
modelagem pode mudar caso de uso. Voltar não é retrabalho, é o processo.

## Regras invioláveis

1. **Nada de `approved` por sua conta.** Você escreve `status: proposed`. Só o humano
   promove. Essa é a única garantia do processo — não a contorne nem "por eficiência".
2. **Lacuna gera pergunta, não valor.** Se a informação não está no briefing nem veio do
   usuário, ela vai para `questions.md`. Nunca para o artefato.
3. **Contradição é reportada, não resolvida.** Você não escolhe qual das duas versões vale.
4. **Rastreabilidade na criação.** Preencha `satisfies`, `verified_by` e `source` ao criar
   o artefato. Depois ninguém preenche.
5. **Não reescreva artefato `approved`.** Proponha a mudança, e marque como `stale` todo
   artefato que dependia dele. O validador vai bloquear até o humano revisar.
6. **Nunca gere código de aplicação aqui.** Este repo produz especificação. A
   implementação é outro projeto, e recebe o PSP.

## Ao criar artefato

- Template em `templates/`, um por tipo. Copie e preencha; não invente estrutura.
- Nome do arquivo = o `id`. `FR-003` vive em `requirements/FR-003.md`. O validador checa.
- Numere sequencialmente dentro do tipo, sem reaproveitar número de artefato removido.
- Prefixos: `FR` requisito, `NFR` atributo de qualidade, `BR` regra, `UC` caso de uso,
  `ADR` decisão, `TC` caso de teste, `PR` processo.

## Ao falar com o usuário

Ele pode não ser técnico. Pergunte sobre o negócio — quem faz o quê, o que não pode
acontecer, o que acontece quando dá errado. Nunca sobre schema, endpoint, padrão de
projeto ou framework. Traduzir negócio em técnica é seu trabalho, não dele.

Uma pergunta por vez. Ofereça um default quando houver um razoável: escolher é mais fácil
que inventar.

## Antes de dizer que terminou

```bash
python3 validate.py projects/<slug>
```

Exit 0 ou não terminou. Não relate "pronto" com o validador vermelho, e não desligue um
gate para ele passar — o gate existe porque aquela falha já custou retrabalho.

## O que este repo deliberadamente não tem

Sem banco, sem servidor, sem interface web, sem orquestração multiagente, sem CI. Arquivo
e git bastam para um usuário. Se você sentir falta de algum deles, leia a §9 de
`docs/alignment.md` antes de propor: a ausência é decisão tomada, não lacuna.
