"""Citizen Assist AI - módulo de Energia para pequenas empresas em comunidades (energia solar).
Uso:  python src/bot.py          (conversa no terminal)
      python src/bot.py --demo   (roda perguntas de exemplo)
"""
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import energia as en


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def r(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def n1(v):
    return f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def rodape(p):
    return (f"\n\nCondições: estimativa para o exemplo '{p['perfil']}' (consumo {n1(en.consumo_base(p))} kWh/mês, "
            f"tarifa {r(p['tarifa_rs_kwh'])}/kWh, {p['solar']['hsp']} h de sol pleno/dia). "
            "Não é economia garantida: confira sua conta de luz e peça orçamentos. Fontes: digite 'fontes'.")


FONTES = ("Fontes (verifique antes de usar):\n"
          "- ANEEL: tarifas, custo de disponibilidade (REN 1.000/2021) e geração distribuída\n"
          "- Lei 14.300/2022: marco legal da geração distribuída (Fio B e compensação)\n"
          "- INPE/CRESESB: Atlas Brasileiro de Energia Solar (irradiação)\n"
          "- Greener e Solfácil: preço médio de sistemas fotovoltaicos (R$/Wp)\n"
          "- Procel/Inmetro: consumo e eficiência de equipamentos\n"
          "- MCTI: fatores de emissão do Sistema Interligado Nacional\n"
          "- EPE: Balanço Energético Nacional e dados de geração distribuída\n"
          "Detalhes em docs/referencias.md.")


def ajustar(p, texto):
    """Permite: simular consumo=500 tarifa=1,05 hsp=4,8 custo=4000"""
    mudou = []
    for k, v in re.findall(r"(consumo|tarifa|hsp|custo)\s*=\s*([\d.,]+)", texto):
        val = float(v.replace(",", "."))
        if k == "consumo":
            p["consumo_conta_kwh"] = val
        elif k == "tarifa":
            p["tarifa_rs_kwh"] = val
        elif k == "hsp":
            p["solar"]["hsp"] = val
        elif k == "custo":
            p["solar"]["custo_rs_kwp"] = val
        mudou.append(f"{k}={v}")
    return mudou


def responder(texto, p):
    t = norm(texto)
    if t.startswith("simular"):
        mudou = ajustar(p, t)
        b = en.comparar(p)["base"]
        return (f"Ajustei: {', '.join(mudou) or 'nada (use consumo=, tarifa=, hsp=, custo=)'}.\n"
                f"Conta estimada hoje: {n1(b['kwh_consumo'])} kWh/mês = {r(b['custo_mes'])}/mês." + rodape(p))

    res = en.comparar(p)
    base, a, b, c = res["base"], res["A"], res["B"], res["C"]
    s = p["solar"]

    if any(k in t for k in ("fonte", "referencia", "bibliograf")):
        return FONTES

    if any(k in t for k in ("fio b", "lei 14300", "lei 14.300", "taxa do sol", "taxacao", "compensacao")):
        r27 = en.comparar(en._com(p, ["solar", "perda_compensacao"], 0.14))["C"]
        r28 = en.comparar(en._com(p, ["solar", "perda_compensacao"], 0.17))["C"]
        return ("Pela Lei 14.300/2022 (art. 27), quem liga solar depois de 7/1/2023 paga parte do Fio B "
                "(uso da rede) sobre a energia injetada: 60% em 2026, 75% em 2027 e 90% em 2028; de 2029 em "
                "diante a ANEEL define a regra. Energia gerada e usada na hora não passa pela rede. "
                f"No modelo, a perda de crédito é {int(s['perda_compensacao']*100)}% (2026). Se subir para 14% (2027) "
                f"o retorno da opção C vai a ~{n1(r27['payback_meses']/12)} anos; com 17% (2028), "
                f"~{n1(r28['payback_meses']/12)} anos. Ou seja, o Fio B pesa pouco no retorno, mas vale simular." + rodape(p))

    if any(k in t for k in ("limita", "garant", "confiavel", "risco")):
        return ("Limitações: a economia depende dos equipamentos reais, da tarifa, da sombra e da inclinação do "
                "telhado, do clima e da regra de compensação vigente (Fio B). Preços e eficiência são estimados. "
                "Há um mínimo faturável mesmo com solar (custo de disponibilidade) e o imóvel precisa ser seu "
                "ou autorizado pelo proprietário. Resultados são ordens de grandeza, não promessas.")

    if any(k in t for k in ("passo", "como instalar", "como contratar", "homolog", "orcamento", "comecar")):
        return ("Passos para instalar solar no comércio:\n"
                "1) Junte 3 a 12 contas de luz e confira o consumo (kWh) e o tipo de ligação.\n"
                "2) Faça primeiro a eficiência (LED, manutenção da refrigeração): reduz o tamanho do sistema.\n"
                "3) Verifique o telhado: área livre, sombra, estrutura e se o imóvel é seu ou autorizado.\n"
                "4) Peça pelo menos 3 orçamentos de integradores e compare R$/kWp, garantias e inversor.\n"
                "5) O integrador pede a homologação na distribuidora (Lei 14.300) antes de ligar o sistema.\n"
                "6) Acompanhe a geração e a conta nos primeiros meses." + rodape(p))

    if any(k in t for k in ("comunidade", "compartilhada", "cooperativa", "associacao", "coletivo", "vizinho")):
        return ("Opções em comunidade: comerciantes sem telhado adequado podem avaliar a geração compartilhada "
                "(cooperativa ou consórcio que recebe créditos de uma usina), prevista na Lei 14.300/2022. "
                "Também é possível comprar equipamentos juntos para negociar preço. Atenção: as regras e os "
                "descontos variam por distribuidora e contrato; verifique na ANEEL e na sua distribuidora "
                "antes de assinar. Este assistente não calcula essa modalidade." + rodape(p))

    if any(k in t for k in ("equipamento", "mais gasta", "vilao", "quem gasta", "onde gasto")):
        linhas = [f"- {n}: {n1(k)} kWh/mês ({int(pc*100)}%) ≈ {r(k*p['tarifa_rs_kwh'])}"
                  for n, k, pc in en.ranking_equipamentos(p)]
        return "Consumo por equipamento (estimado):\n" + "\n".join(linhas) + rodape(p)

    if any(k in t for k in ("compar", "melhor opcao", "melhor alternativa", "o que fazer")):
        return (f"Comparação mensal (mesma necessidade: conta de luz do comércio):\n"
                f"- Atual: {n1(base['kwh_consumo'])} kWh, {r(base['custo_mes'])}\n"
                f"- A) Eficiência: {n1(a['kwh_consumo'])} kWh, {r(a['custo_mes'])} "
                f"(economia {r(a['economia_mes'])}; investimento {r(a['investimento'])}; retorno {n1(a['payback_meses'])} meses)\n"
                f"- B) Solar {n1(b['kwp'])} kWp: {r(b['custo_mes'])} "
                f"(economia {r(b['economia_mes'])}; investimento {r(b['investimento'])}; retorno {n1(b['payback_meses']/12)} anos)\n"
                f"- C) Eficiência + solar {n1(c['kwp'])} kWp: {r(c['custo_mes'])} "
                f"(economia {r(c['economia_mes'])}; investimento {r(c['investimento'])}; retorno {n1(c['payback_meses']/12)} anos)\n"
                "Recomendação: faça A primeiro (retorno em poucos meses) e dimensione o solar depois (C), "
                "pois um sistema menor custa menos." + rodape(p))

    if any(k in t for k in ("solar", "fotovolt", "painel", "paineis", "vale a pena", "kwp")):
        return (f"Energia solar para o comércio: sistema de ~{n1(b['kwp'])} kWp gera ~{n1(b['geracao_kwh'])} kWh/mês "
                f"(kWp x {s['hsp']} h x 30 dias x {s['desempenho']}). Investimento estimado {r(b['investimento'])}. "
                f"A conta cai de {r(base['custo_mes'])} para {r(b['custo_mes'])} (economia {r(b['economia_mes'])}/mês; "
                f"o mínimo de {p['custo_disponibilidade_kwh']} kWh continua sendo cobrado). "
                f"Retorno ~{n1(b['payback_meses']/12)} anos; em {s['vida_util_anos']} anos o saldo é "
                f"~{r(b['saldo_vida_util'])} (já com troca de inversor, sem reajuste de tarifa). "
                f"CO2 evitado: {n1(b['co2_evitado_mes'])} kg/mês, valor pequeno porque a rede brasileira já é "
                "majoritariamente renovável; o ganho principal é financeiro." + rodape(p))

    if any(k in t for k in ("economiz", "dica", "reduzir", "led", "lampada", "geladeira", "eficiencia")):
        return (f"Eficiência (A): trocar as lâmpadas fluorescentes por LED de {p['eficiencia']['led_w']} W e "
                f"manter a refrigeração (limpar o condensador, trocar borrachas, não encostar na parede) economiza "
                f"~{n1(a['economia_kwh'])} kWh e {r(a['economia_mes'])}/mês, com investimento de "
                f"~{r(a['investimento'])} (retorno em ~{n1(a['payback_meses'])} meses). Também ajuda desligar "
                "ventiladores e luzes sem uso e abrir menos as portas dos expositores." + rodape(p))

    if any(k in t for k in ("consumo", "gasta", "gasto", "conta", "quanto", "custa")):
        return (f"Seu comércio consome ~{n1(base['kwh_consumo'])} kWh/mês, o que custa ~{r(base['custo_mes'])}/mês "
                f"e corresponde a {n1(base['co2_mes'])} kg de CO2. Pergunte 'qual equipamento gasta mais' "
                "para ver onde está o consumo." + rodape(p))

    return ("Sou o módulo de Energia do Citizen Assist AI para pequenos comércios. Posso explicar: consumo e "
            "equipamentos, como economizar (LED e refrigeração), energia solar, comparar opções, passos para "
            "instalar, opções em comunidade, limitações e fontes. Para personalizar: "
            "'simular consumo=500 tarifa=1,05 hsp=4,8 custo=4000'.")


def main():
    p = en.carregar()
    if "--demo" in sys.argv:
        for q in ["Quanto minha loja gasta de luz?", "Qual equipamento gasta mais?", "Como posso economizar?",
                  "Vale a pena energia solar?", "Comparar opções", "Quais os passos para instalar?",
                  "E o Fio B?", "Quais as limitações?", "fontes", "simular consumo=500 tarifa=1,05", "Vale a pena energia solar?"]:
            print(f"\nVocê: {q}\nBot: {responder(q, p)}")
        return
    print("Citizen Assist AI - Energia para pequenos comércios (digite 'sair' para encerrar)")
    while True:
        q = input("\nVocê: ").strip()
        if norm(q) in ("sair", "exit"):
            break
        print("Bot:", responder(q, p))


if __name__ == "__main__":
    main()
