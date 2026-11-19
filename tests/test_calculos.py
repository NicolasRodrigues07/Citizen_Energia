"""Testes automatizados do modulo de Energia. Execute: python -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from calculos import (analisar, consumo_mensal_kwh, energia_kwh, payback_anos,  # noqa: E402
                      perfil_padrao, saldo_liquido)
from assistente_energia import AssistenteEnergia, ferramenta_energia  # noqa: E402


class TestFormulas(unittest.TestCase):
    def test_energia_de_um_banho(self):
        # 5.500 W por 15 min = 1,375 kWh (valor citado por Procel/Copel/imprensa)
        self.assertAlmostEqual(energia_kwh(5500, 15), 1.375, places=3)

    def test_consumo_mensal_perfil_padrao(self):
        self.assertAlmostEqual(consumo_mensal_kwh(5500, 10, 4, 1, 30), 110.0, places=2)

    def test_payback_simples(self):
        self.assertAlmostEqual(payback_anos(8000, 924, 150), 8000 / 774, places=2)

    def test_payback_nunca(self):
        self.assertIsNone(payback_anos(8000, 100, 150))  # manutencao maior que a economia

    def test_payback_sem_investimento(self):
        self.assertEqual(payback_anos(0, 500), 0.0)

    def test_saldo_liquido(self):
        self.assertAlmostEqual(saldo_liquido(1000, 600, 100, 0.0, 4), 1000.0, places=2)


class TestCenarios(unittest.TestCase):
    def setUp(self):
        self.r = analisar(perfil_padrao())

    def test_base(self):
        self.assertAlmostEqual(self.r["base"]["kwh_mes"], 110.0, places=2)
        self.assertAlmostEqual(self.r["base"]["custo_ano"], 1320.0, places=2)

    def test_alternativa_a_habitos(self):
        self.assertAlmostEqual(self.r["A"]["kwh_mes"], 61.6, places=2)
        self.assertAlmostEqual(self.r["A"]["economia_ano_reais"], 580.8, places=2)

    def test_alternativa_b_solar(self):
        b = self.r["B"]
        self.assertAlmostEqual(b["economia_kwh_mes"], 77.0, places=2)
        self.assertAlmostEqual(b["economia_ano_reais"], 924.0, places=2)
        self.assertAlmostEqual(b["payback_simples"], 10.34, places=1)

    def test_solar_depois_dos_habitos_rende_menos(self):
        self.assertLess(self.r["B_apos_A"]["economia_ano_reais"], self.r["B"]["economia_ano_reais"])

    def test_habito_nunca_piora_consumo(self):
        p = dict(perfil_padrao(), minutos=5)  # ja toma banho curto
        self.assertLessEqual(analisar(p)["A"]["kwh_mes"], analisar(p)["base"]["kwh_mes"])

    def test_mais_moradores_encurta_retorno(self):
        p6 = dict(perfil_padrao(), pessoas=6, minutos=15)
        self.assertLess(analisar(p6)["B"]["payback_simples"], self.r["B"]["payback_simples"])

    def test_co2_pequeno_e_positivo(self):
        self.assertGreater(self.r["B"]["co2_evitado_ano_kg"], 0)
        self.assertLess(self.r["B"]["co2_evitado_ano_kg"], 100)


class TestAssistente(unittest.TestCase):
    def test_extrai_dados_do_usuario(self):
        a = AssistenteEnergia()
        a.responder("Somos 5 pessoas, banho de 12 minutos, chuveiro de 6500 W, tarifa R$ 0,95/kWh")
        self.assertEqual(a.perfil["pessoas"], 5)
        self.assertEqual(a.perfil["minutos"], 12)
        self.assertEqual(a.perfil["potencia_w"], 6500)
        self.assertAlmostEqual(a.perfil["tarifa_kwh"], 0.95)

    def test_rejeita_valor_absurdo(self):
        a = AssistenteEnergia()
        r = a.responder("banho de 500 minutos")
        self.assertEqual(a.perfil["minutos"], 10)
        self.assertIn("Nao consegui usar", r)

    def test_solar_nao_vira_ajuda(self):  # regressao: 'ola' dentro de 'solar'
        a = AssistenteEnergia()
        self.assertEqual(a.detectar("aquecedor solar vale a pena"), "recomendar")
        self.assertEqual(a.detectar("como funciona o aquecedor solar"), "solar")

    def test_resposta_traz_aviso_de_estimativa(self):
        self.assertIn("nao e garantia", AssistenteEnergia().responder("quanto gasta meu chuveiro"))

    def test_resposta_recomendacao_coerente_com_analise(self):
        r = AssistenteEnergia().responder("vale a pena aquecedor solar?")
        self.assertIn("HABITOS", r)
        self.assertIn("retorno", r)

    def test_ferramenta_estruturada(self):
        d = ferramenta_energia(pessoas=3, minutos=8)
        self.assertEqual(d["perfil"]["pessoas"], 3)
        self.assertIn("B", d["cenarios"])


if __name__ == "__main__":
    unittest.main()
