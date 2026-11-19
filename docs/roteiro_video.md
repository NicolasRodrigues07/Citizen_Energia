# Roteiro do vídeo técnico (máx. 3 min) — YouTube **não listado**

**Dica:** grave a tela com o terminal grande (fonte 18+). Ensaie uma vez; use `python src/assistente_energia.py`.

| Tempo | Tela | Fala (adapte com suas palavras) |
|---|---|---|
| 0:00–0:20 | Slide ou README | "Somos o grupo [nome]. Este é o módulo de **Energia** do Citizen Assist AI, para **famílias de São Paulo que usam chuveiro elétrico**. O chuveiro é um dos maiores gastos de energia da casa (Procel: cerca de 24% do consumo residencial em média)." |
| 0:20–0:55 | `docs/analise_alternativas.md` (tabelas) | "Analisamos uma família de 4 pessoas, banho de 10 min, chuveiro de 5.500 W: **110 kWh/mês, R$ 110**. Fórmula: potência × tempo × banhos × dias. Comparamos **A) hábitos** (7 min e posição morna) e **B) aquecedor solar**, a fonte renovável. A economia é de R$ 581/ano em A e R$ 924/ano em B." |
| 0:55–1:25 | Tabela de resultados e sensibilidade | "O solar custa cerca de R$ 8 mil e retorna em ~10 anos nesse perfil; já para 6 pessoas com banho de 15 min, em ~4 anos. O CO₂ evitado é pequeno porque a matriz elétrica brasileira já é limpa — o ganho principal é financeiro. Os dados de tarifa, preço e fração solar são **estimativas**, indicadas no arquivo de premissas." |
| 1:25–2:30 | **Demonstração no terminal** | Rode: `quanto gasta meu chuveiro?` → `Somos 5 pessoas, banho de 15 minutos e chuveiro de 6500 W` → `compare as alternativas` → `vale a pena instalar aquecedor solar?` → `qual o impacto ambiental?` → `quais as fontes?`. Narre: "O assistente recalcula com os dados do usuário e a recomendação muda conforme o perfil." |
| 2:30–3:00 | `limitacoes` + testes unitários + `docs/testes_usuarios.md` | "Principais recomendações: primeiro hábitos, depois avaliar o solar com orçamentos. Limitações: valores estimados, sem garantia de economia. Testamos com [N] usuários e ajustamos [o que mudaram]. Obrigado!" |

**Checklist antes de publicar:** duração ≤ 3:00 · mostra público e necessidade · mostra análise e comparação com fonte renovável ·
mostra demonstração no assistente · cita recomendações **e** limitações · visibilidade "Não listado".
