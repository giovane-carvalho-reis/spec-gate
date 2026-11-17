# Briefing

## 1. O problema
Projeto começa a ser implementado antes de o problema estar entendido. O briefing é vago,
o escopo não tem borda, a regra de negócio aparece no meio da implementação e a decisão
técnica é tomada sem contexto. O resultado é retrabalho, suposição virando comportamento,
e requisito contraditório descoberto tarde.

Com agente de IA implementando, a dor piora: o agente não hesita diante de ambiguidade.
Ele escolhe uma interpretação e escreve código convicto. Lacuna de especificação, que com
um humano geraria uma pergunta, com um agente gera código errado — rápido e em volume.

## 2. Quem sofre a dor
O autor, trabalhando sozinho em projetos pessoais, usando Claude Code e OpenCode para
implementar. Hoje contorna especificando dentro da conversa com o agente: o contexto se
perde entre sessões, nada fica rastreável, e a mesma decisão é reexplicada várias vezes.

## 3. Resultado esperado
Antes de a implementação começar, existe uma pasta versionada em que: todo requisito tem
critério de aceitação verificável; toda regra de negócio está ligada ao requisito que a
atende; toda decisão técnica tem contexto e alternativa descartada registrados; e um
comando responde objetivamente se a especificação está pronta ou o que falta.

O agente de implementação recebe essa pasta e não precisa adivinhar nada — nem perguntar
de novo o que já foi decidido.

## 4. Funcionalidades imaginadas
- Criar projeto com trilha proporcional ao porte.
- Criticar o briefing e registrar lacuna como pergunta, não como suposição.
- Entrevistar o autor para fechar as lacunas.
- Gerar os artefatos por etapa a partir de template.
- Validar coerência e rastreabilidade por comando, com exit code.
- Exigir aprovação humana explícita por etapa.
- Revisar coerência de sentido entre artefatos.
- Entregar a pasta aprovada ao projeto de implementação.

## 5. Regras conhecidas
- Saída de IA nunca é fato: entra como proposta e só o humano aprova.
- Lacuna gera pergunta, nunca valor suposto.
- Contradição é reportada, nunca resolvida pela IA.
- Artefato aprovado não é reescrito pela IA.
- ID de artefato é estável e não se reaproveita.
- Nenhum código de aplicação é produzido aqui.

## 6. Integrações
Nenhum serviço externo. Claude Code e OpenCode leem o repositório como arquivo local; git
guarda o histórico; GitHub hospeda e renderiza os diagramas. Nada roda em servidor.

## 7. Restrições
- Uso individual. Sem autenticação, sem colaboração, sem concorrência.
- Sem banco de dados e sem aplicação web.
- Python com `pyyaml` e `jsonschema` — nada além.
- Formato de diagrama único: Mermaid, para renderizar no GitHub sem ferramenta externa.
- Crédito de IA é recurso escasso: o caminho de validação não pode custar chamada de LLM.

## 8. Critérios de sucesso
- `validate.py` detecta rastreabilidade quebrada sem nenhuma chamada de LLM.
- Um projeto real atravessa as 12 skills e sai com os 10 gates verdes.
- O agente de implementação recebe o PSP e não precisa perguntar nada que já foi decidido.
- Especificar um projeto pequeno custa menos crédito que reexplicar o contexto a cada
  sessão de implementação.

## 9. Fora de escopo
- Geração de código de aplicação — permanente, não é só do MVP.
- Aplicação web, banco de dados, servidor, autenticação, multiusuário.
- Execução de agente de programação, integração com IDE, CI/CD, deploy.
- Orquestração multiagente concorrente: um papel por vez.
- Gestão de bug e monitoramento de produção.
- Importação de PDF e DOCX.
