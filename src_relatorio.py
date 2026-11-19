"""Gera docs/calculos.md (tabelas completas) e docs/comparacao.png (gráfico, se matplotlib existir)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import energia as en
from bot import r, n1

RAIZ = Path(__file__).resolve().parent.parent


def main():
    p = en.carregar()
    res = en.comparar(p)
    b = res["base"]
    L = ["# Cálculos e comparação das alternativas", "",
         f"Caso de estudo: **{p['perfil']}**. Período de referência: 1 mês (30 dias). Todos os valores são estimativas.", "",
         "## 1. Consumo por equipamento", "",
         "Fórmula: E (kWh/mês) = quantidade x P (kW) x horas/dia x fator de uso x dias/mês.", "",
         "| Equipamento | Qtd | P (W) | h/dia | Fator de uso | Dias | kWh/mês | % | R$/mês |", "|---|---|---|---|---|---|---|---|---|"]
    tot = en.consumo_base(p)
    for e in p["equipamentos"]:
        k = en.consumo_equip(e)
        L.append(f"| {e['nome']} | {e['qtd']} | {e['potencia_w']} | {e['horas_dia']} | {e['fator_uso']} | {e['dias_mes']} | "
                 f"{n1(k)} | {int(k/tot*100)}% | {r(k*p['tarifa_rs_kwh'])} |")
    L += [f"| **Total** | | | | | | **{n1(tot)}** | 100% | **{r(tot*p['tarifa_rs_kwh'])}** |", "",
          f"Emissão: {n1(tot)} kWh x {p['fator_emissao_kgco2_kwh']} kg/kWh = {n1(b['co2_mes'])} kg CO2/mês.", "",
          "## 2. Alternativas", "",
          "- **A) Eficiência:** LED de 18 W no lugar de 40 W e manutenção da refrigeração (-10%).",
          "- **B) Solar fotovoltaico (renovável):** kWp = (consumo - custo de disponibilidade) / (HSP x 30 x desempenho).",
          "- **C) A + B:** eficiência primeiro e solar dimensionado para o consumo já reduzido.", "",
          "Conta com solar = max(consumo - energia compensada, custo de disponibilidade) x tarifa + manutenção.", "",
          "| Opção | kWp | Consumo (kWh) | Geração (kWh) | Faturado (kWh) | Conta/mês | Economia/mês | Investimento | Retorno | CO2 evitado/mês |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    L.append(f"| Atual | - | {n1(b['kwh_consumo'])} | - | {n1(b['kwh_faturado'])} | {r(b['custo_mes'])} | - | - | - | - |")
    for k in ("A", "B", "C"):
        a = res[k]
        ret = f"{n1(a['payback_meses'])} meses" if a["kwp"] == 0 else f"{n1(a['payback_meses']/12)} anos"
        kwp = "-" if a["kwp"] == 0 else n1(a["kwp"])
        ger = "-" if a["kwp"] == 0 else n1(a["geracao_kwh"])
        L.append(f"| {a['nome']} | {kwp} | {n1(a['kwh_consumo'])} | {ger} | {n1(a['kwh_faturado'])} | "
                 f"{r(a['custo_mes'])} | {r(a['economia_mes'])} | {r(a['investimento'])} | {ret} | {n1(a['co2_evitado_mes'])} kg |")
    s = p["solar"]
    L += ["", f"Saldo em {s['vida_util_anos']} anos (economia mensal x 12 x anos - investimento - troca de inversor de "
          f"{r(s['troca_inversor_rs'])}): B = {r(res['B']['saldo_vida_util'])}; C = {r(res['C']['saldo_vida_util'])}. "
          "Sem reajuste de tarifa, sem degradação dos painéis e sem financiamento (simplificação).", "",
          "## 3. Sensibilidade do retorno (anos)", "",
          "| Fator | Caso | Retorno B | Retorno C |", "|---|---|---|---|"]
    for x in en.sensibilidade(p):
        L.append(f"| {x['grupo']} | {x['rotulo']} | {n1(x['payback_B'])} | {n1(x['payback_C'])} |")
    L += ["", "## 4. Leitura dos resultados", "",
          "- A eficiência tem o retorno mais rápido e o menor risco; deve vir primeiro.",
          "- O solar reduz a conta em ~75%, mas não a zera (custo de disponibilidade).",
          "- O retorno é mais sensível ao preço do sistema e à tarifa do que ao Fio B.",
          "- O CO2 evitado é pequeno porque a matriz elétrica brasileira já é majoritariamente renovável; o benefício principal é financeiro.", ""]
    (RAIZ / "docs" / "calculos.md").write_text("\n".join(L), encoding="utf-8")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        nomes = ["Atual", "A) Eficiência", "B) Solar", "C) A + Solar"]
        contas = [b["custo_mes"]] + [res[k]["custo_mes"] for k in "ABC"]
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.bar(nomes, contas, color=["#999", "#4c9", "#f90", "#27a"])
        for bar, v in zip(bars, contas):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 5, f"R$ {v:,.0f}".replace(",", "."), ha="center")
        ax.set_ylabel("Conta de luz (R$/mês)")
        ax.set_title("Mercearia de bairro: conta mensal estimada por alternativa")
        fig.tight_layout()
        fig.savefig(RAIZ / "docs" / "comparacao.png", dpi=150)
        print("gráfico gerado")
    except Exception as exc:
        print("gráfico não gerado:", exc)


if __name__ == "__main__":
    main()
