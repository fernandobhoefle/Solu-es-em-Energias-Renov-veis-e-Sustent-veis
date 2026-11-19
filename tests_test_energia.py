import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import energia as en
import bot


def test_consumo_base():
    p = en.carregar()
    assert abs(en.consumo_base(p) - 436.6) < 1e-6          # 144 + 108 + 104 + 41,6 + 39


def test_custo_base():
    res = en.comparar(en.carregar())
    assert abs(res["base"]["custo_mes"] - 436.6 * 1.10) < 1e-6


def test_eficiencia():
    kwh, inv = en.economia_eficiencia(en.carregar())
    assert abs(kwh - 82.4) < 1e-6                           # 57,2 (LED) + 25,2 (refrigeração)
    assert abs(inv - 350) < 1e-6


def test_solar_dimensionamento_e_conta_minima():
    p = en.carregar()
    res = en.comparar(p)
    assert abs(res["B"]["kwp"] - (436.6 - 50) / (4.5 * 30 * 0.8)) < 1e-6
    assert res["B"]["kwh_faturado"] >= p["custo_disponibilidade_kwh"]   # nunca zera a conta
    assert res["B"]["payback_meses"] > 0


def test_combinado_menor_investimento_solar():
    res = en.comparar(en.carregar())
    assert res["C"]["kwp"] < res["B"]["kwp"]
    assert res["C"]["investimento"] < res["B"]["investimento"]


def test_bot_condicoes_e_valores():
    p = en.carregar()
    assert "Não é economia garantida" in bot.responder("vale a pena energia solar", p)
    assert "R$" in bot.responder("comparar opções", p)
    assert "kWh/mês" in bot.responder("qual equipamento gasta mais", p)


if __name__ == "__main__":
    for nome, fn in list(globals().items()):
        if nome.startswith("test_"):
            fn(); print("OK", nome)
