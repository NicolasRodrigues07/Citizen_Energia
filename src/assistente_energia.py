"""
Citizen Assist AI - Modulo de Energia e Sustentabilidade
Assistente que orienta familias sobre o consumo de ENERGIA DO BANHO (chuveiro eletrico)
e compara alternativas: (A) eficiencia/habitos e (B) aquecedor solar (fonte renovavel).

Como usar:
    python src/assistente_energia.py          # conversa no terminal
    python src/assistente_energia.py --demo   # dialogo de demonstracao (para o video/testes)

Integracao com o assistente principal (outras disciplinas):
    from assistente_energia import AssistenteEnergia
    energia = AssistenteEnergia()
    resposta = energia.responder("Moramos em 5 pessoas, banho de 15 min. Vale a pena solar?")

    # ou como 'ferramenta' (function calling) que devolve dados estruturados:
    from assistente_energia import ferramenta_energia
    dados = ferramenta_energia(pessoas=5, minutos=15)
"""
import re
import sys
import unicodedata

from calculos import (analisar, carregar_premissas, consumo_mensal_kwh, custo_bandeira,
                      custo_reais, energia_kwh, perfil_padrao)

# limites aceitos para dados informados pelo usuario (evita resultados absurdos)
LIMITES = {
    "pessoas": (1, 12),
    "minutos": (2, 60),
    "potencia_w": (2000, 8000),
    "tarifa_kwh": (0.30, 3.00),
}

AVISO = ("(Estimativa baseada em premissas declaradas; nao e garantia de economia. "
         "Digite 'limitacoes' ou 'fontes'.)")


# ------------------------------------------------------------- utilitarios
def normalizar(txt):
    txt = unicodedata.normalize("NFKD", txt.lower())
    return "".join(c for c in txt if not unicodedata.combining(c))


def num(x, casas=1):
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def brl(x):
    return "R$ " + num(x, 2)


def anos_txt(a):
    if a is None:
        return "nao se paga no periodo analisado"
    if a == 0:
        return "sem investimento"
    return f"~{num(a, 1)} anos"


# --------------------------------------------------------------- assistente
class AssistenteEnergia:
    def __init__(self):
        self.perfil = perfil_padrao()
        self.meta = carregar_premissas()[1]

    # ---------------------------------------------------- entrada do usuario
    def atualizar_perfil(self, texto_norm):
        """Extrai pessoas, minutos, potencia e tarifa de uma frase livre."""
        mudancas, recusados = [], []

        def aplicar(chave, valor, rotulo):
            lo, hi = LIMITES[chave]
            if lo <= valor <= hi:
                self.perfil[chave] = valor
                mudancas.append(rotulo)
            else:
                recusados.append(f"{rotulo} (valor fora do intervalo {lo} a {hi})")

        m = re.search(r"(\d+)\s*(pessoas|moradores|habitantes)", texto_norm) or \
            re.search(r"somos\s+(\d+)", texto_norm)
        if m:
            aplicar("pessoas", int(m.group(1)), f"{m.group(1)} pessoas")
        m = re.search(r"(\d+)\s*(min|minutos)", texto_norm)
        if m:
            aplicar("minutos", int(m.group(1)), f"banho de {m.group(1)} min")
        m = re.search(r"(\d[\d\.]*)\s*w\b", texto_norm)
        if m:
            w = int(m.group(1).replace(".", ""))
            aplicar("potencia_w", w, f"chuveiro de {w} W")
        m = re.search(r"r\$\s*(\d+(?:[.,]\d+)?)\s*(?:/|por)\s*kwh", texto_norm) or \
            re.search(r"tarifa[^\d]{0,20}(\d+(?:[.,]\d+)?)", texto_norm)
        if m:
            aplicar("tarifa_kwh", float(m.group(1).replace(",", ".")), f"tarifa de R$ {m.group(1)}/kWh")
        return mudancas, recusados

    def detectar(self, t):
        def tem(*palavras):
            return any(p in t for p in palavras)

        def palavra(*palavras):
            """Casa palavras inteiras (evita 'ola' dentro de 'solar')."""
            return any(re.search(r"\b" + p + r"\b", t) for p in palavras)

        if tem("sair", "tchau", "encerrar") and len(t.split()) <= 3:
            return "sair"
        if tem("limita", "garantia", "certeza", "margem de erro", "confiav"):
            return "limitacoes"
        if tem("fonte", "referencia", "de onde", "origem dos dados"):
            return "referencias"
        if palavra("ajuda", "menu", "help", "oi", "ola") or tem("o que voce faz"):
            return "ajuda"
        if tem("co2", "carbono", "ambient", "emiss", "sustent", "poluic"):
            return "ambiente"
        if tem("bandeira", "amarela", "vermelha"):
            return "bandeira"
        if tem("vale a pena", "recomend", "devo ", "o que fazer", "qual o melhor", "qual melhor"):
            return "recomendar"
        if tem("compar", "alternativa", "opcoes", "opcao", "diferenca"):
            return "comparar"
        if tem("solar", "renovavel", "boiler", "painel"):
            return "solar"
        if tem("dica", "economizar", "economia", "reduzir", "diminuir", "habito"):
            return "habitos"
        if tem("consum", "gasta", "gasto", "quanto custa", "conta", "chuveiro", "kwh", "banho"):
            return "consumo"
        return "desconhecida"

    # ------------------------------------------------------------ respostas
    def responder(self, texto):
        t = normalizar(texto)
        mudancas, recusados = self.atualizar_perfil(t)
        intencao = self.detectar(t)
        partes = []

        if mudancas:
            partes.append("Anotei seus dados: " + ", ".join(mudancas) + ".")
        if recusados:
            partes.append("Nao consegui usar: " + "; ".join(recusados) + ". Mantive o valor anterior.")

        if intencao == "sair":
            return "Ate logo! Lembre-se: os valores sao estimativas. Consulte sua conta de luz."
        if intencao == "desconhecida":
            if mudancas:
                intencao = "consumo"   # usuario so informou dados: mostra o impacto
            else:
                return ("Nao entendi bem. Posso ajudar com: consumo do chuveiro, comparar alternativas, "
                        "recomendacao, dicas de economia, aquecedor solar, impacto ambiental, bandeiras "
                        "tarifarias, fontes e limitacoes. Digite 'ajuda'.")

        corpo = getattr(self, "_r_" + intencao)()
        partes.append(corpo)
        if intencao not in ("ajuda", "limitacoes", "referencias"):
            partes.append(AVISO)
        return "\n".join(partes)

    def _r_ajuda(self):
        return ("Sou o modulo de Energia do Citizen Assist AI. Ajudo familias a entender e reduzir "
                "o gasto de energia com o BANHO quente.\n"
                "- Conte seu caso: 'Somos 5 pessoas, banho de 12 min, chuveiro de 6500 W, tarifa R$ 0,95/kWh'\n"
                "- Pergunte: 'quanto gasta meu chuveiro?', 'comparar alternativas', 'vale a pena solar?',\n"
                "  'dicas de economia', 'impacto ambiental', 'bandeira tarifaria', 'fontes', 'limitacoes'.")

    def _r_consumo(self):
        p = self.perfil
        kwh_banho = energia_kwh(p["potencia_w"], p["minutos"])
        kwh_mes = consumo_mensal_kwh(p["potencia_w"], p["minutos"], p["pessoas"],
                                     p["banhos_por_pessoa_dia"], p["dias_mes"])
        c_mes = custo_reais(kwh_mes, p["tarifa_kwh"])
        return (f"Com {p['pessoas']} pessoas, 1 banho por dia de {p['minutos']} min e chuveiro de "
                f"{p['potencia_w']} W:\n"
                f"- Cada banho usa ~{num(kwh_banho, 2)} kWh (potencia em kW x tempo em horas).\n"
                f"- No mes: ~{num(kwh_mes, 0)} kWh = {brl(c_mes)} por mes ({brl(c_mes * 12)} por ano), "
                f"com tarifa de {brl(p['tarifa_kwh'])}/kWh.\n"
                f"- Cada minuto a menos de banho, para todos, poupa ~"
                f"{num(energia_kwh(p['potencia_w'], 1) * p['pessoas'] * p['dias_mes'], 1)} kWh/mes.\n"
                "O chuveiro eletrico esta entre os maiores consumidores da casa (Procel: ~24% do consumo "
                "residencial em media, dado de 2007).")

    def _r_comparar(self):
        r = analisar(self.perfil)
        linhas = ["Comparacao para a mesma necessidade (banho quente da familia), por mes/ano:"]
        for k in ("base", "A", "B", "AB"):
            c = r[k]
            linhas.append(
                f"- {c['nome']}: {num(c['kwh_mes'], 0)} kWh/mes, {brl(c['custo_mes'])}/mes | "
                f"economia {brl(c['economia_ano_reais'])}/ano | investimento {brl(c['investimento'])} | "
                f"retorno: {anos_txt(c['payback_simples'])}")
        b = r["B"]
        linhas.append(f"- CO2 evitado por ano: A = {num(r['A']['co2_evitado_ano_kg'], 0)} kg; "
                      f"B = {num(b['co2_evitado_ano_kg'], 0)} kg (a rede eletrica brasileira ja e bastante limpa).")
        linhas.append("Fonte renovavel analisada: aquecedor solar (calor do sol aquece a agua; o apoio eletrico cobre "
                      f"os ~{num((1 - self.perfil['fracao_solar']) * 100, 0)}% restantes).")
        return "\n".join(linhas)

    def _r_recomendar(self):
        r = analisar(self.perfil)
        a, b, bA = r["A"], r["B"], r["B_apos_A"]
        vida = self.perfil["vida_util_anos"]
        pb = b["payback_simples"]
        linhas = ["Minha recomendacao, em 2 passos (para o seu perfil):",
                  f"1) Comece pelos HABITOS (custo zero): banho de {self.perfil['A_minutos']} min e chuveiro na "
                  f"posicao morna economizam ~{num(a['economia_kwh_mes'], 0)} kWh/mes "
                  f"(~{brl(a['economia_ano_reais'])}/ano)."]
        if pb is None:
            juizo = "O aquecedor solar nao se paga com estes dados."
        elif pb <= vida * 0.5:
            juizo = (f"O aquecedor solar tende a compensar: retorno de {anos_txt(pb)} "
                     f"(vida util estimada de {vida} anos).")
        elif pb <= vida:
            juizo = (f"O aquecedor solar e possivel, mas o retorno e longo ({anos_txt(pb)}; vida util estimada "
                     f"de {vida} anos). Decida pelo orcamento real e tambem por motivos ambientais e de conforto.")
        else:
            juizo = (f"O retorno ({anos_txt(pb)}) passa da vida util estimada ({vida} anos): "
                     "financeiramente nao compensa no seu perfil.")
        linhas.append(f"2) AQUECEDOR SOLAR (renovavel): economiza ~{num(b['economia_kwh_mes'], 0)} kWh/mes "
                      f"(~{brl(b['economia_ano_reais'])}/ano). {juizo}")
        linhas.append(f"   Se voce JA adotar os habitos, o ganho extra do solar cai para "
                      f"~{brl(bA['economia_ano_reais'])}/ano (retorno: {anos_txt(bA['payback_simples'])}).")
        linhas.append("   O solar compensa mais com: mais moradores, banhos mais longos, tarifa mais alta ou "
                      "orcamento menor. Peca pelo menos 3 orcamentos e confira a etiqueta ENCE/Inmetro do coletor.")
        return "\n".join(linhas)

    def _r_solar(self):
        b = analisar(self.perfil)["B"]
        return ("Aquecedor solar: coletores no telhado aquecem a agua, que fica guardada num reservatorio "
                "(boiler). E uma fonte renovavel e nao emite CO2 na operacao.\n"
                f"- Estimativa usada: cobre ~{num(self.perfil['fracao_solar'] * 100, 0)}% da energia do banho; "
                "em dias nublados o apoio eletrico complementa.\n"
                f"- Custo estimado do sistema para familia de 3 a 4 pessoas: ~{brl(self.perfil['investimento_solar'])} "
                "instalado (faixa observada: R$ 6 mil a R$ 20 mil).\n"
                f"- Economia estimada neste perfil: {brl(b['economia_ano_reais'])}/ano; retorno {anos_txt(b['payback_simples'])}.\n"
                "Condicoes: telhado com boa insolacao, espaco e estrutura para o boiler, instalacao por profissional "
                "e manutencao periodica.")

    def _r_habitos(self):
        p = self.perfil
        um_min = energia_kwh(p["potencia_w"], 1) * p["pessoas"] * p["dias_mes"]
        a = analisar(p)["A"]
        return ("Dicas que funcionam (todas sem custo):\n"
                f"- Reduza o banho: cada minuto a menos poupa ~{num(um_min, 1)} kWh/mes "
                f"(~{brl(um_min * p['tarifa_kwh'])}/mes) para a sua familia.\n"
                "- Use a posicao morna/verao sempre que o tempo permitir: menor potencia, menor gasto.\n"
                "- Feche o registro ao ensaboar.\n"
                f"- Meta sugerida ({p['A_minutos']} min na posicao morna): economia de ~{num(a['economia_kwh_mes'], 0)} kWh/mes "
                f"(~{brl(a['economia_ano_reais'])}/ano).\n"
                "- Se for trocar o chuveiro, procure a etiqueta Procel e pergunte pelo controle de temperatura.")

    def _r_ambiente(self):
        r = analisar(self.perfil)
        fator = self.perfil["fator_emissao_kg_kwh"]
        return (f"Impacto ambiental (fator medio do SIN, MCTI: ~{num(fator * 1000, 1)} kgCO2/MWh):\n"
                f"- Seu chuveiro hoje emite ~{num(r['base']['co2_emitido_ano_kg'], 0)} kgCO2/ano.\n"
                f"- Habitos evitam ~{num(r['A']['co2_evitado_ano_kg'], 0)} kg/ano; solar evita ~"
                f"{num(r['B']['co2_evitado_ano_kg'], 0)} kg/ano.\n"
                "Como a energia eletrica brasileira ja e majoritariamente renovavel, o ganho de CO2 e pequeno. "
                "Os beneficios principais sao economia, menor pico de demanda e menor dependencia da rede. "
                "Nao incluimos a pegada de fabricacao dos equipamentos (limitacao).")

    def _r_bandeira(self):
        p = self.perfil
        kwh = consumo_mensal_kwh(p["potencia_w"], p["minutos"], p["pessoas"],
                                 p["banhos_por_pessoa_dia"], p["dias_mes"])
        am = custo_bandeira(kwh, p["bandeira_amarela_100kwh"])
        v1 = custo_bandeira(kwh, p["bandeira_vermelha1_100kwh"])
        v2 = custo_bandeira(kwh, p["bandeira_vermelha2_100kwh"])
        return (f"Bandeira tarifaria vigente (nov/2026): {p['bandeira_vigente']} - sem cobranca extra.\n"
                f"Se mudar, o chuveiro da sua casa (~{num(kwh, 0)} kWh/mes) custaria a mais por mes: "
                f"amarela {brl(am)}, vermelha 1 {brl(v1)}, vermelha 2 {brl(v2)}.\n"
                "A bandeira muda todo mes: confira no site da ANEEL.")

    def _r_limitacoes(self):
        return ("Limitacoes das estimativas:\n"
                "- Tarifa, precos e fracao solar sao ESTIMADOS (veja data/premissas.json); sua conta e seu telhado podem diferir.\n"
                "- O calculo usa potencia constante no banho; chuveiros reais variam com a posicao e a temperatura da agua.\n"
                "- Economia e retorno nao sao garantidos: dependem do clima, do uso e dos precos no futuro.\n"
                "- Nao consideramos financiamento, tarifa social/branca, nem pegada de fabricacao dos equipamentos.\n"
                "- Algumas fontes sao antigas (Procel 2007) ou secundarias (guias de mercado).\n"
                "Use como orientacao inicial e confirme com orcamentos e com a sua distribuidora.")

    def _r_referencias(self):
        linhas = ["Fontes e premissas (detalhes em docs/referencias.md e data/premissas.json):"]
        for chave in ("tarifa_kwh", "potencia_w", "minutos", "fracao_solar", "investimento_solar",
                      "fator_emissao_kg_kwh", "bandeira_vigente"):
            m = self.meta[chave]
            linhas.append(f"- {chave} = {m['valor']} {m['unidade']} [{m['tipo']}]: {m['fonte']}")
        return "\n".join(linhas)


# ------------------------------------------------- API para integracao
def ferramenta_energia(**perfil):
    """
    Versao 'ferramenta' (function calling): recebe campos do perfil e devolve dados
    estruturados para o assistente principal formatar a resposta.
    Campos aceitos: pessoas, minutos, potencia_w, tarifa_kwh.
    """
    ass = AssistenteEnergia()
    for chave, valor in perfil.items():
        if chave in LIMITES and LIMITES[chave][0] <= valor <= LIMITES[chave][1]:
            ass.perfil[chave] = valor
    return {"perfil": ass.perfil, "cenarios": analisar(ass.perfil),
            "aviso": "Estimativas baseadas em premissas; ver data/premissas.json"}


# ------------------------------------------------------------------- CLI
DEMO = [
    "oi",
    "Quanto gasta meu chuveiro?",
    "Somos 5 pessoas, banho de 15 minutos e chuveiro de 6500 W",
    "Compare as alternativas",
    "Vale a pena instalar aquecedor solar?",
    "Qual o impacto ambiental?",
    "Tarifa R$ 0,95/kWh, e se a bandeira ficar vermelha?",
    "Quais sao as limitacoes?",
    "sair",
]


def main():
    ass = AssistenteEnergia()
    print("=== Citizen Assist AI - Modulo Energia ===  (digite 'ajuda' ou 'sair')\n")
    if "--demo" in sys.argv:
        for fala in DEMO:
            print(f"Voce: {fala}")
            print(f"Assistente: {ass.responder(fala)}\n")
        return
    while True:
        try:
            fala = input("Voce: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not fala:
            continue
        resp = ass.responder(fala)
        print(f"Assistente: {resp}\n")
        if ass.detectar(normalizar(fala)) == "sair":
            break


if __name__ == "__main__":
    main()
