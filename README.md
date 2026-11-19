# Citizen Assist AI — Módulo de Energia e Sustentabilidade
**Global Solution 2026.2 · Soluções em Energias Renováveis e Sustentáveis · Ciência da Computação (1CCPW)**

## 1. Integrantes
1. Nicolas Andrade Rodrigues - RM 572782
2. Lucas Caram Bueno - RM 570158

## 2. Público e problema
**Público:** famílias de 3 a 5 pessoas, moradoras de casas ou apartamentos na região de São Paulo, que **aquecem a água do banho com chuveiro elétrico**
e querem **reduzir a conta de luz** sem linguagem técnica.

**Necessidade energética:** o chuveiro elétrico tem alta potência (4.500 a 7.800 W) e, segundo o Procel, responde em média por ~24% do consumo residencial.
Muitas famílias não sabem **quanto gastam**, **como reduzir** nem **se vale a pena** uma alternativa renovável, como o aquecedor solar.

**Como o assistente ajuda:** converte o hábito da família (moradores, minutos de banho, potência do chuveiro, tarifa) em kWh e reais,
**compara alternativas** para a mesma necessidade e recomenda o que fazer, informando fontes e limitações.

## 3. Funcionalidades de energia
| Pergunta do usuário (exemplos) | O que o assistente faz |
|---|---|
| "Somos 5 pessoas, banho de 15 min, chuveiro de 6500 W, tarifa R$ 0,95/kWh" | Extrai os dados do texto, valida limites e recalcula tudo |
| "Quanto gasta meu chuveiro?" | kWh/banho, kWh/mês, R$/mês e R$/ano |
| "Compare as alternativas" | Tabela: atual × **A) hábitos** × **B) solar (renovável)** × A+B (kWh, R$, investimento, retorno, CO₂) |
| "Vale a pena instalar aquecedor solar?" | Recomendação em 2 passos, coerente com a análise e com o perfil |
| "Dicas de economia" / "Impacto ambiental" / "Bandeira tarifária" | Dicas quantificadas, CO₂ (MCTI) e efeito das bandeiras (ANEEL) |
| "Fontes" / "Limitações" | Mostra origem e tipo (público/estimado) de cada dado e as condições das estimativas |

Toda resposta com números termina avisando que são **estimativas** (não garantias).

## 4. Como executar e testar
Requisitos: **Python 3.8+** (sem bibliotecas externas).
```bash
python src/assistente_energia.py          # conversa interativa
python src/assistente_energia.py --demo   # diálogo de demonstração
python -m unittest discover -s tests -v   # 19 testes automatizados
```
**Integração com o assistente principal:**
```python
import sys; sys.path.append("energia/src")          # ajuste o caminho
from assistente_energia import AssistenteEnergia, ferramenta_energia

energia = AssistenteEnergia()
print(energia.responder("Moramos em 5 pessoas. Vale a pena aquecedor solar?"))

dados = ferramenta_energia(pessoas=5, minutos=15)   # JSON estruturado (function calling)
```

## 5. Estrutura do repositório
```
src/calculos.py            fórmulas (energia, custo, retorno, CO2) e comparação de cenários
src/assistente_energia.py  assistente (intenções, extração de dados, respostas, API de integração)
data/premissas.json        TODOS os dados e premissas, com valor, unidade, tipo, fonte e observação
tests/test_calculos.py     testes automatizados (cálculos e assistente)
docs/analise_alternativas.md  cálculos, comparação, sensibilidade e justificativas
docs/referencias.md        referências verificáveis
docs/testes_usuarios.md    protocolo, registro dos testes e ajustes
docs/roteiro_video.md      roteiro do vídeo (3 min)
```

## 6. Resultado resumido (perfil padrão: 4 pessoas, banho de 10 min, 5.500 W, R$ 1,00/kWh)
| Cenário | kWh/mês | Economia/ano | Investimento | Retorno |
|---|---|---|---|---|
| Atual | 110 | — | — | — |
| A) Hábitos (7 min, posição morna) | 61,6 | R$ 581 | R$ 0 | imediato |
| B) Aquecedor solar (renovável) | 33 | R$ 924 | R$ 8.000 (est.) | ≈ 10,3 anos |
Detalhes, sensibilidade e justificativas em [`docs/analise_alternativas.md`](docs/analise_alternativas.md).

**Recomendação:** adotar os hábitos primeiro; considerar o solar se o retorno calculado para o perfil do usuário for aceitável.
**Impacto ambiental:** CO₂ evitado é pequeno (22–42 kg/ano) porque a matriz elétrica brasileira já é limpa; o ganho principal é financeiro.

## 7. Dados, referências e limitações
- Dados e premissas: [`data/premissas.json`](data/premissas.json) (itens **estimados** identificados como tal).
- Referências: [`docs/referencias.md`](docs/referencias.md).
- **Limitações:** tarifa, preços, fração solar, vida útil e manutenção são estimativas; potência constante no banho; sem financiamento, tarifa social/branca
  ou pegada de fabricação. Economia, geração e custos **não são garantidos**.

## 8. Testes com usuários
Protocolo, registro e ajustes em [`docs/testes_usuarios.md`](docs/testes_usuarios.md).

## 9. Uso de IA generativa e verificação
Ferramentas de IA generativa foram usadas como apoio na estrutura do projeto e no rascunho do código. A equipe verificou os dados fornecidos.
