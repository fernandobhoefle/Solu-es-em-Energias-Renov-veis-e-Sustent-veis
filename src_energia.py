"""Cálculos do módulo 'Energia e Sustentabilidade' do Citizen Assist AI.

Público: pequenas empresas (comércios) em comunidades.
Necessidade: reduzir a conta de luz com eficiência energética e energia solar fotovoltaica.
Período de referência comum a todas as alternativas: 1 mês (30 dias); retorno e saldo na vida útil.
"""
import copy
import json
from pathlib import Path

DADOS = Path(__file__).resolve().parent.parent / "data" / "premissas.json"
DIAS = 30


def carregar(caminho=DADOS):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def consumo_equip(e):
    """E (kWh/mês) = qtd x P (kW) x horas/dia x fator de uso x dias."""
    return e["qtd"] * e["potencia_w"] / 1000 * e["horas_dia"] * e["fator_uso"] * e["dias_mes"]


def consumo_base(p):
    """Usa o consumo da conta de luz, se informado; senão, soma dos equipamentos."""
    if p.get("consumo_conta_kwh"):
        return float(p["consumo_conta_kwh"])
    return sum(consumo_equip(e) for e in p["equipamentos"])


def ranking_equipamentos(p):
    itens = [(e["nome"], consumo_equip(e)) for e in p["equipamentos"]]
    total = sum(k for _, k in itens)
    return sorted([(n, k, k / total) for n, k in itens], key=lambda x: -x[1])


def economia_eficiencia(p):
    """Retorna (kWh/mês economizados, investimento em R$) com LED + manutenção da refrigeração."""
    ef = p["eficiencia"]
    kwh, inv = 0.0, 0.0
    for e in p["equipamentos"]:
        if e["tipo"] == "iluminacao" and e["potencia_w"] > ef["led_w"]:
            kwh += e["qtd"] * (e["potencia_w"] - ef["led_w"]) / 1000 * e["horas_dia"] * e["fator_uso"] * e["dias_mes"]
            inv += e["qtd"] * ef["custo_led_un_rs"]
        elif e["tipo"] == "refrigeracao":
            kwh += consumo_equip(e) * ef["reducao_refrigeracao"]
            inv += ef["custo_manutencao_refrigeracao_rs"] / 2  # custo por equipamento (2 refrigeradores no exemplo)
    return min(kwh, 0.9 * consumo_base(p)), inv


def dimensionar_kwp(kwh_consumo, p):
    """kWp para gerar (consumo - custo de disponibilidade) por mês: kWp = E / (HSP x dias x desempenho)."""
    s = p["solar"]
    alvo = max(kwh_consumo - p["custo_disponibilidade_kwh"], 0)
    return alvo / (s["hsp"] * DIAS * s["desempenho"])


def avaliar(nome, kwh_consumo, p, investimento=0.0, kwp=0.0):
    s = p["solar"]
    disp = p["custo_disponibilidade_kwh"]
    geracao = kwp * s["hsp"] * DIAS * s["desempenho"]
    compensado = min(geracao * (1 - s["perda_compensacao"]), max(kwh_consumo - disp, 0))
    faturado = max(kwh_consumo - compensado, disp)
    manut = s["manutencao_anual_rs"] / 12 if kwp > 0 else 0.0
    rede = kwh_consumo - compensado
    return {
        "nome": nome, "kwh_consumo": kwh_consumo, "kwp": kwp, "geracao_kwh": geracao,
        "kwh_rede": rede, "kwh_faturado": faturado,
        "custo_mes": faturado * p["tarifa_rs_kwh"] + manut,
        "co2_mes": rede * p["fator_emissao_kgco2_kwh"],
        "investimento": investimento + kwp * s["custo_rs_kwp"],
    }


def comparar(p):
    s = p["solar"]
    base_kwh = consumo_base(p)
    base = avaliar("Situação atual", base_kwh, p)

    kwh_ef, inv_ef = economia_eficiencia(p)
    a = avaliar("A) Eficiência energética (LED + refrigeração)", base_kwh - kwh_ef, p, inv_ef)
    b = avaliar("B) Energia solar fotovoltaica", base_kwh, p, 0.0, dimensionar_kwp(base_kwh, p))
    kwh_c = base_kwh - kwh_ef
    c = avaliar("C) Eficiência + solar (recomendado)", kwh_c, p, inv_ef, dimensionar_kwp(kwh_c, p))

    for alt in (a, b, c):
        alt["economia_mes"] = base["custo_mes"] - alt["custo_mes"]
        alt["economia_kwh"] = base["kwh_rede"] - alt["kwh_rede"]
        alt["co2_evitado_mes"] = base["co2_mes"] - alt["co2_mes"]
        alt["payback_meses"] = alt["investimento"] / alt["economia_mes"] if alt["economia_mes"] > 0 else float("inf")
        if alt["kwp"] > 0:
            anos = s["vida_util_anos"]
            troca = s["troca_inversor_rs"] if anos > s["ano_troca_inversor"] else 0
            alt["saldo_vida_util"] = alt["economia_mes"] * 12 * anos - alt["investimento"] - troca
        else:
            alt["saldo_vida_util"] = None
    return {"base": base, "A": a, "B": b, "C": c}


def _com(p, caminho, valor):
    q = copy.deepcopy(p)
    alvo = q
    for k in caminho[:-1]:
        alvo = alvo[k]
    alvo[caminho[-1]] = valor
    return q


def sensibilidade(p):
    """Retorno (anos) das opções B e C variando as maiores incertezas."""
    casos = [
        ("Preço do sistema", "R$ 2.500/kWp", ["solar", "custo_rs_kwp"], 2500),
        ("Preço do sistema", "R$ 3.000/kWp (base)", ["solar", "custo_rs_kwp"], 3000),
        ("Preço do sistema", "R$ 3.500/kWp", ["solar", "custo_rs_kwp"], 3500),
        ("Tarifa", "R$ 0,90/kWh", ["tarifa_rs_kwh"], 0.90),
        ("Tarifa", "R$ 1,10/kWh (base)", ["tarifa_rs_kwh"], 1.10),
        ("Tarifa", "R$ 1,30/kWh", ["tarifa_rs_kwh"], 1.30),
        ("Fio B", "2026 (60%): perda 12% (base)", ["solar", "perda_compensacao"], 0.12),
        ("Fio B", "2027 (75%): perda 14%", ["solar", "perda_compensacao"], 0.14),
        ("Fio B", "2028 (90%): perda 17%", ["solar", "perda_compensacao"], 0.17),
    ]
    linhas = []
    for grupo, rotulo, caminho, valor in casos:
        res = comparar(_com(p, caminho, valor))
        linhas.append({"grupo": grupo, "rotulo": rotulo,
                       "economia_B": res["B"]["economia_mes"], "payback_B": res["B"]["payback_meses"] / 12,
                       "economia_C": res["C"]["economia_mes"], "payback_C": res["C"]["payback_meses"] / 12})
    return linhas
