# Análise de consumo e comparação de alternativas

> Todos os números abaixo são **reproduzíveis**: vêm de `src/calculos.py` + `data/premissas.json`
> (rode `python -m unittest discover -s tests -v` para conferir). Itens **estimados** estão marcados.

## 1. Necessidade analisada (mesma para todas as alternativas)
**Água quente para o banho de uma família de 4 pessoas em São Paulo (SP)**, período de referência de
**1 mês / 1 ano** (e 15 anos para o investimento).

## 2. Dados e premissas (resumo)
| Item | Valor | Tipo | Origem |
|---|---|---|---|
| Moradores | 4 | estimado | perfil-exemplo (alterável no assistente) |
| Banhos | 1 por pessoa/dia, 30 dias | estimado | premissa |
| Potência do chuveiro | 5.500 W (posição inverno) | dado de mercado | R4, R5 |
| Duração do banho | 10 min | estimado | R3 (Procel 2007: ~48% dos banhos quentes < 10 min) |
| Tarifa | R$ 1,00/kWh | estimado | derivada de faturas B1 Enel SP (2026) + reajuste de 9,02% (R2) |
| Bandeira (nov/2026) | verde (sem custo extra) | dado público | R1 |
| Fator de emissão | 0,0385 kgCO₂/kWh | dado público | R8 (MCTI, SIN 2023) |
| Fração solar | 70% | estimado | R6 (guias citam 70–80%; usamos o menor) |
| Investimento solar | R$ 8.000 instalado | estimado | R7 (kits R$ 4,6–6,9 mil + instalação R$ 1,5–3 mil) |
| Manutenção solar | R$ 150/ano | estimado | premissa |
| Vida útil solar | 15 anos | estimado | premissa conservadora |

## 3. Fórmulas
```
energia (kWh)  = potência (kW) × tempo (h)
consumo/mês    = energia por banho × pessoas × banhos/dia × dias
custo (R$)     = kWh × tarifa
CO₂ (kg)       = kWh × fator de emissão
retorno (anos) = investimento ÷ (economia/ano − manutenção/ano)
```
Verificação: 5.500 W × 0,25 h = **1,375 kWh** por banho de 15 min — valor também citado por Procel/Copel/imprensa (R4).

## 4. Consumo atual (linha de base)
5,5 kW × (10/60 h) × 4 pessoas × 30 dias = **110 kWh/mês** → **R$ 110,00/mês** → **R$ 1.320/ano** → **≈ 51 kgCO₂/ano**.

## 5. Alternativas
- **A) Eficiência (hábitos), sem investimento:** banho de 7 min + posição morna (80% da potência = 4.400 W).
  4,4 kW × (7/60) × 4 × 30 = **61,6 kWh/mês**.
- **B) Aquecedor solar (fonte renovável)**, com apoio elétrico: cobre 70% da energia do banho.
  110 × (1 − 0,70) = **33 kWh/mês** restantes (apoio elétrico).
- **A+B)** hábitos + solar: 61,6 × 0,30 = **18,5 kWh/mês**.

### Resultados (mesma necessidade, mesmo período)
| Cenário | kWh/mês | Custo/mês | Custo/ano | Economia/ano | CO₂ evitado/ano | Investimento | Retorno (tarifa fixa) | Retorno (tarifa +5% a.a.) |
|---|---|---|---|---|---|---|---|---|
| Atual | 110,0 | R$ 110,00 | R$ 1.320 | — | — | — | — | — |
| **A) Hábitos** | 61,6 | R$ 61,60 | R$ 739 | **R$ 581** | 22 kg | R$ 0 | imediato | imediato |
| **B) Solar** | 33,0 | R$ 33,00 | R$ 396 | **R$ 924** | 36 kg | R$ 8.000 | **≈ 10,3 anos** | ≈ 8,3 anos |
| A+B | 18,5 | R$ 18,48 | R$ 222 | R$ 1.098 | 42 kg | R$ 8.000 | ≈ 8,4 anos | ≈ 7,1 anos |
| Solar *depois* de A | 18,5 | — | — | R$ 517 (ganho extra) | 20 kg | R$ 8.000 | ≈ 21,8 anos | ≈ 14,0 anos |

Saldo líquido do solar B em 15 anos (economia − manutenção − investimento): **+R$ 3.610** (tarifa fixa) a **+R$ 9.689** (tarifa +5% a.a.).

## 6. Sensibilidade do aquecedor solar (retorno simples, em anos, 4 pessoas / 10 min)
| Investimento \ Fração solar | 50% | 70% | 80% |
|---|---|---|---|
| R$ 6.000 | 11,8 | 7,8 | 6,6 |
| R$ 8.000 | 15,7 | **10,3** | 8,8 |
| R$ 12.000 | 23,5 | 15,5 | 13,2 |

**Outro perfil (6 pessoas, banho de 15 min):** consumo-base 247,5 kWh/mês e retorno do solar de **≈ 4,1 anos**
— o resultado depende muito do perfil, e por isso o assistente recalcula tudo com os dados do usuário.

## 7. Justificativa das recomendações
**Custos.** Hábitos não custam nada e já entregam R$ 581/ano (63% da economia do solar). O solar economiza mais
(R$ 924/ano), mas exige R$ 8 mil e, neste perfil, retorna em ~10 anos (dentro dos 15 de vida útil estimada, porém longo).

**Viabilidade.** O solar depende de telhado com insolação, espaço/estrutura para o boiler (reservatório cheio é pesado),
instalação profissional e manutenção. Estudo acadêmico com família de baixa renda e tarifa social encontrou retorno de ~11 anos (R9),
coerente com o nosso resultado de ~10 anos — e mostra que o retorno melhora com mais moradores, banhos longos e tarifa alta.

**Impacto ambiental.** A matriz elétrica brasileira é muito limpa (≈ 38,5 kgCO₂/MWh), então o CO₂ evitado é pequeno
(22–42 kg/ano por família). Os ganhos reais são **economia**, **menos demanda no horário de pico** e **independência parcial da rede**.
Não contabilizamos a pegada de fabricação dos equipamentos (limitação).

**Recomendação do assistente (coerente com a análise):** 1º adotar os hábitos (A); 2º considerar o solar (B) apenas se o retorno
calculado para o perfil do usuário for razoável (≤ metade da vida útil: "tende a compensar"; até a vida útil: "longo, decida com orçamento";
acima: "não compensa financeiramente").

## 8. Bandeiras tarifárias (efeito sobre o chuveiro de 110 kWh/mês)
| Bandeira | Adicional | Custo extra/mês |
|---|---|---|
| Verde (nov/2026) | — | R$ 0,00 |
| Amarela | R$ 1,885 / 100 kWh | R$ 2,07 |
| Vermelha 1 | R$ 4,463 / 100 kWh | R$ 4,91 |
| Vermelha 2 | R$ 7,877 / 100 kWh | R$ 8,66 |

## 9. Limitações
Tarifa, preços, fração solar, vida útil e manutenção são **estimativas**; potência constante no banho; sem financiamento,
tarifa social/branca ou pegada de fabricação; fontes de 2007 (Procel) e guias de mercado são secundárias. Resultados **não são garantias**.
