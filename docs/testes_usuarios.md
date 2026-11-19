# Testes com usuários — registro e ajustes

## 1. Protocolo (15 min por pessoa)
1. Peça autorização para registrar as respostas **de forma anônima**.
2. Explique em 1 frase: "É um assistente que ajuda a entender o gasto de energia do banho."
3. Deixe a pessoa usar sozinha o assistente (`python src/assistente_energia.py`) com 3 tarefas:
  - **T1:** descobrir quanto gasta o chuveiro da casa dela (informando moradores e tempo de banho).
  - **T2:** perguntar se vale a pena instalar aquecedor solar.
  - **T3:** descobrir de onde vêm os números / quais as limitações.
4. Faça as 4 perguntas do questionário e anote comentários espontâneos.

## 2. Questionário (nota de 1 a 5)
| Pergunta | Escala |
|---|---|
| P1. Entendi a resposta sobre o consumo do chuveiro? | 1 = nada … 5 = totalmente |
| P2. Entendi a comparação entre as alternativas? | 1–5 |
| P3. A recomendação foi útil para decidir o que fazer? | 1–5 |
| P4. Ficou claro que os valores são estimativas e de onde vêm? | 1–5 |
| P5 (aberta). O que foi difícil de entender? O que você mudaria? | texto |

## 3. Registro dos testes
| Participante | Perfil (idade, moradores, mora em casa/apto) | T1 ok? | T2 ok? | T3 ok? | P1 | P2 | P3 | P4 | Comentários (P5) |
|---|---|---|---|---|---|---|---|---|---|
| Daphne Andrade | 19 anos, 3 moradores, casa | Sim | Sim | Sim | 5 | 4 | 5 | 4 | "Entendi bem como usar, só fiquei na dúvida de como escrever o tempo de banho logo na primeira tentativa." |
| Irene Rodrigues | 61 anos, 4 moradores, casa | Parcial | Sim | Não | 3 | 3 | 4 | 3 | "Entendi menos em alguns pontos; não sabia a potência do chuveiro em Watts e não achei fácil de onde saíam os números." |
| Marcio Francisco | 50 anos, 5 moradores, casa | Sim | Sim | Sim | 5 | 5 | 5 | 5 | "Entendeu bem e achou direto ao ponto; sugeriu mostrar exemplos prontos na tela inicial." |

**Média por pergunta:** P1 = 4,3 · P2 = 4,0 · P3 = 4,7 · P4 = 4,0

## 4. Situações de teste (mínimo recomendado)
| # | Situação | Entrada de exemplo | Resultado esperado | Resultado obtido |
|---|---|---|---|---|
| S1 | Perfil padrão | "quanto gasta meu chuveiro?" | ~110 kWh/mês, R$ 110/mês | OK — exibiu 110,0 kWh/mês e R$ 110,00/mês usando valores padrão (3 pessoas, 10 min, 5.500 W, R$ 1,00/kWh). |
| S2 | Família grande | "somos 6 pessoas, banho de 15 min" | consumo ~248 kWh/mês; solar com retorno curto (~4 anos) | OK — calculou 247,5 kWh/mês (R$ 247,50/mês) e estimou retorno do aquecedor solar em ~3,8 anos. |
| S3 | Banho já curto | "banho de 5 minutos" | assistente não promete economia maior que a base | OK — informou gasto base de 55,0 kWh/mês e indicou que reduzir o tempo já está no limite recomendado. |
| S4 | Dado absurdo | "banho de 500 minutos" | recusa o valor e mantém o anterior | OK — exibiu aviso de valor inválido (fora da faixa aceita) e manteve o tempo anterior. |
| S5 | Tarifa própria | "tarifa R$ 0,85/kWh" | recalcula custos com a nova tarifa | OK — atualizou a tarifa para R$ 0,85/kWh e recalculou o custo mensal corretamente. |
| S6 | Pergunta fora do escopo | "qual a capital da França?" | diz que não entendeu e lista o que sabe fazer | OK — respondeu que não entendeu a solicitação e listou os comandos/perguntas suportados. |

## 5. Ajustes realizados
| Data | Origem do problema | Ajuste feito |
|---|---|---|
| (dev.) | **Teste interno** do desenvolvimento: a pergunta "vale a pena instalar aquecedor *solar*?" caiu no menu de ajuda porque a palavra "ola" foi encontrada dentro de "s**ola**r". | Troca para busca por **palavra inteira** + teste de regressão `test_solar_nao_vira_ajuda`. |
| (dev.) | **Teste interno**: o cenário de hábitos usava 4.400 W fixos, errado para chuveiros de outra potência. | Passou a usar **80% da potência do chuveiro informado** (`A_fator_potencia`). |
| 19/11/2026 | **Teste com usuários (Daphne Andrade, Marcio Francisco)**: dúvida inicial sobre o formato de escrita do tempo de banho e pedido de exemplos prontos na abertura. | Inclusão de exemplos de frases na mensagem inicial e exibição explícita da potência padrão (5.500 W) e da tarifa (R$ 1,00/kWh). |
| 19/11/2026 | **Teste com usuários (Irene Rodrigues)**: dificuldade em identificar a origem dos números (T3) e insegurança por não saber a potência do chuveiro. | Adição de resumo das premissas ao final do cálculo e explicação simplificada de como encontrar ou estimar os dados do chuveiro. |
