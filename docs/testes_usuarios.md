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

## 3. Registro dos testes (anônimo)
| Participante | Perfil (idade, moradores, mora em casa/apto) | T1 ok? | T2 ok? | T3 ok? | P1 | P2 | P3 | P4 | Comentários (P5) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | |
| 2 | | | | | | | | | |
| 3 | | | | | | | | | |
| 4 | | | | | | | | | |
| 5 | | | | | | | | | |

**Média por pergunta:** P1 = __ · P2 = __ · P3 = __ · P4 = __

## 4. Situações de teste (mínimo recomendado)
| # | Situação | Entrada de exemplo | Resultado esperado | Resultado obtido |
|---|---|---|---|---|
| S1 | Perfil padrão | "quanto gasta meu chuveiro?" | ~110 kWh/mês, R$ 110/mês | |
| S2 | Família grande | "somos 6 pessoas, banho de 15 min" | consumo ~248 kWh/mês; solar com retorno curto (~4 anos) | |
| S3 | Banho já curto | "banho de 5 minutos" | assistente não promete economia maior que a base | |
| S4 | Dado absurdo | "banho de 500 minutos" | recusa o valor e mantém o anterior | |
| S5 | Tarifa própria | "tarifa R$ 0,85/kWh" | recalcula custos com a nova tarifa | |
| S6 | Pergunta fora do escopo | "qual a capital da França?" | diz que não entendeu e lista o que sabe fazer | |

## 5. Ajustes realizados
| Data | Origem do problema | Ajuste feito |
|---|---|---|
| (dev.) | **Teste interno** do desenvolvimento: a pergunta "vale a pena instalar aquecedor *solar*?" caiu no menu de ajuda porque a palavra "ola" foi encontrada dentro de "s**ola**r". | Troca para busca por **palavra inteira** + teste de regressão `test_solar_nao_vira_ajuda`. |
| (dev.) | **Teste interno**: o cenário de hábitos usava 4.400 W fixos, errado para chuveiros de outra potência. | Passou a usar **80% da potência do chuveiro informado** (`A_fator_potencia`). |
| | | *(acrescentar ajustes vindos dos testes com usuários)* |
