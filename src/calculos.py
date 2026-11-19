"""
Citizen Assist AI - Modulo de Energia
Funcoes de calculo (energia, custo, payback e CO2) para a necessidade:
"agua quente para banho em uma residencia" (chuveiro eletrico x alternativas).

Todas as formulas sao simples e rastreaveis:
    energia (kWh) = potencia (kW) x tempo (h)
    custo (R$)    = energia (kWh) x tarifa (R$/kWh)
    CO2 (kg)      = energia (kWh) x fator de emissao (kgCO2/kWh)
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQ_PREMISSAS = RAIZ / "data" / "premissas.json"


# ----------------------------------------------------------------- dados
def carregar_premissas(caminho=ARQ_PREMISSAS):
    """Retorna (valores, metadados): dict id->valor e dict id->info completa."""
    with open(caminho, encoding="utf-8") as f:
        bruto = json.load(f)["premissas"]
    valores = {k: v["valor"] for k, v in bruto.items()}
    return valores, bruto


def perfil_padrao():
    return carregar_premissas()[0]


# --------------------------------------------------------------- formulas
def energia_kwh(potencia_w, minutos):
    """Energia de um uso: potencia (W) durante 'minutos'."""
    return (potencia_w / 1000.0) * (minutos / 60.0)


def consumo_mensal_kwh(potencia_w, minutos, pessoas, banhos_por_pessoa_dia=1.0, dias=30):
    return energia_kwh(potencia_w, minutos) * pessoas * banhos_por_pessoa_dia * dias


def custo_reais(kwh, tarifa):
    return kwh * tarifa


def emissao_kg(kwh, fator):
    return kwh * fator


def payback_anos(investimento, economia_ano, manutencao_ano=0.0, reajuste=0.0, max_anos=50):
    """
    Anos ate a economia liquida acumulada (economia - manutencao) cobrir o investimento.
    'reajuste' = aumento anual da tarifa (0.05 = 5% a.a.). Interpola dentro do ano.
    Retorna None se nao se paga em 'max_anos'.
    """
    if investimento <= 0:
        return 0.0
    acumulado = 0.0
    for ano in range(1, max_anos + 1):
        ganho = economia_ano * ((1.0 + reajuste) ** (ano - 1)) - manutencao_ano
        if ganho > 0 and acumulado + ganho >= investimento:
            return (ano - 1) + (investimento - acumulado) / ganho
        acumulado += ganho
    return None


def saldo_liquido(investimento, economia_ano, manutencao_ano, reajuste, anos):
    """Economia acumulada em 'anos' menos o investimento (pode ser negativa)."""
    total = 0.0
    for k in range(int(anos)):
        total += economia_ano * ((1.0 + reajuste) ** k) - manutencao_ano
    return total - investimento


# --------------------------------------------------------------- analise
def _cenario(nome, kwh_mes, base_kwh_mes, p, investimento=0.0, manutencao=0.0, ref_kwh_mes=None):
    """Monta um cenario. 'ref_kwh_mes' e o consumo de referencia da comparacao."""
    ref = base_kwh_mes if ref_kwh_mes is None else ref_kwh_mes
    tarifa = p["tarifa_kwh"]
    eco_kwh_mes = ref - kwh_mes
    eco_ano_reais = eco_kwh_mes * 12 * tarifa
    reaj = p["reajuste_tarifa_ano"]
    vida = p["vida_util_anos"]
    return {
        "nome": nome,
        "kwh_mes": kwh_mes,
        "custo_mes": custo_reais(kwh_mes, tarifa),
        "custo_ano": custo_reais(kwh_mes * 12, tarifa),
        "economia_kwh_mes": eco_kwh_mes,
        "economia_ano_reais": eco_ano_reais,
        "co2_evitado_ano_kg": emissao_kg(eco_kwh_mes * 12, p["fator_emissao_kg_kwh"]),
        "co2_emitido_ano_kg": emissao_kg(kwh_mes * 12, p["fator_emissao_kg_kwh"]),
        "investimento": investimento,
        "manutencao_ano": manutencao,
        "payback_simples": payback_anos(investimento, eco_ano_reais, manutencao, 0.0),
        "payback_reaj5": payback_anos(investimento, eco_ano_reais, manutencao, 0.05),
        "saldo_vida_util": saldo_liquido(investimento, eco_ano_reais, manutencao, reaj, vida),
        "saldo_vida_util_reaj5": saldo_liquido(investimento, eco_ano_reais, manutencao, 0.05, vida),
    }


def analisar(p):
    """
    Compara, para a MESMA necessidade (banho quente da familia) e o MESMO periodo,
    4 cenarios. 'p' e o dicionario de premissas/perfil.
      base : chuveiro eletrico, habitos atuais
      A    : eficiencia (banho mais curto + posicao morna) - sem investimento
      B    : aquecedor solar (fonte RENOVAVEL) com apoio eletrico
      AB   : habitos + aquecedor solar
      B_apos_A : ganho EXTRA de instalar o solar para quem ja adotou os habitos
    """
    base = consumo_mensal_kwh(p["potencia_w"], p["minutos"], p["pessoas"],
                              p["banhos_por_pessoa_dia"], p["dias_mes"])
    a = consumo_mensal_kwh(p["potencia_w"] * p["A_fator_potencia"],
                           min(p["A_minutos"], p["minutos"]), p["pessoas"],
                           p["banhos_por_pessoa_dia"], p["dias_mes"])
    b = base * (1.0 - p["fracao_solar"])
    ab = a * (1.0 - p["fracao_solar"])
    inv = p["investimento_solar"]
    man = p["manutencao_solar_ano"]
    return {
        "base": _cenario("Chuveiro eletrico (atual)", base, base, p),
        "A": _cenario("A) Eficiencia: habitos", a, base, p),
        "B": _cenario("B) Aquecedor solar", b, base, p, inv, man),
        "AB": _cenario("A+B) Habitos + solar", ab, base, p, inv, man),
        "B_apos_A": _cenario("Solar apos adotar habitos", ab, base, p, inv, man, ref_kwh_mes=a),
    }


def custo_bandeira(kwh_mes, adicional_por_100kwh):
    """Custo extra mensal de uma bandeira tarifaria sobre 'kwh_mes'."""
    return kwh_mes / 100.0 * adicional_por_100kwh


def sensibilidade_solar(p, investimentos=(6000, 8000, 12000), fracoes=(0.5, 0.7, 0.8)):
    """Payback simples do solar (B) variando investimento e fracao solar."""
    linhas = []
    for inv in investimentos:
        linha = []
        for fr in fracoes:
            q = dict(p, investimento_solar=inv, fracao_solar=fr)
            r = analisar(q)["B"]
            linha.append(r["payback_simples"])
        linhas.append((inv, linha))
    return linhas
