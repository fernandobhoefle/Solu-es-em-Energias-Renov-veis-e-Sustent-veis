# Citizen Assist AI - Energia Solar para Pequenas Empresas em Comunidades
Contribuição da disciplina **Soluções em Energias Renováveis e Sustentáveis** ao Citizen Assist AI.
(Se o repositório for compartilhado com outras disciplinas, esta contribuição está na pasta/arquivos deste módulo.)

**Integrantes:** (nome completo - RM de cada integrante)

## Público e problema
**Pequenas empresas em comunidades** (mercearias, padarias, salões, lanchonetes de bairro). A conta de luz
pesa no caixa de quem tem margem curta, e muitos donos não sabem onde a energia é gasta nem se a **energia solar
fotovoltaica** compensa. O assistente explica, em linguagem simples, quanto o comércio gasta, como economizar
e se vale instalar solar. Caso de estudo: **mercearia de bairro** (premissas em `data/premissas.json`).

## Funcionalidades de energia no assistente
- Consumo e custo mensal, com ranking por equipamento
- Eficiência (A): LED e manutenção da refrigeração
- Energia solar (B): dimensionamento em kWp, geração, conta resultante, retorno e saldo na vida útil
- Combinação (C): eficiência primeiro e depois um sistema solar menor
- Comparação A x B x C, Lei 14.300 (Fio B), passos para instalar, geração compartilhada em comunidade
- Limitações e fontes: toda resposta traz as condições da estimativa
- Personalização: `simular consumo=500 tarifa=1,20 hsp=4,8 custo=3200` (use dados da conta de luz do comércio)

Exemplos de perguntas: "Quanto minha loja gasta de luz?", "Qual equipamento gasta mais?", "Como posso economizar?",
"Vale a pena energia solar?", "Comparar opções", "E o Fio B?", "Quais os passos para instalar?", "fontes".

## Como executar
```
python src/bot.py           # conversa no terminal
python src/bot.py --demo    # perguntas de exemplo (saída em docs/exemplo_conversa.txt)
python tests/test_energia.py
python src/relatorio.py     # regenera docs/calculos.md e docs/comparacao.png
```
Python 3; o bot e os cálculos usam apenas a biblioteca padrão (matplotlib é opcional, só para o gráfico).

## Estrutura
`src/` código | `data/premissas.json` dados e origem | `docs/calculos.md` cálculos completos |
`docs/justificativas.md` | `docs/referencias.md` | `docs/testes_usuarios.md` | `docs/uso_de_ia.md` |
`docs/roteiro_video.md` | `tests/` testes automáticos.

## Dados e premissas
Todos em `data/premissas.json`, com a origem de cada um. Valores ancorados em fontes (consultadas em nov/2026):
fator de emissão (MCTI), regra do Fio B (Lei 14.300), custo de disponibilidade (ANEEL), preço do sistema
(Greener/Solfácil) e tarifa comercial (contas 2026 e reajuste ANEEL). Valores **ESTIMADOS** (potências e fatores de
uso dos equipamentos, horas de sol, desempenho) estão marcados e devem ser trocados pelos dados reais do comércio.

## Resultados (estimativas para 30 dias, tarifa R$ 1,10/kWh)
Consumo-base: **436,6 kWh/mês**, **R$ 480,26/mês** (refrigeração 56%, iluminação 23%).

| Opção | Conta/mês | Economia/mês | Investimento | Retorno |
|---|---|---|---|---|
| Atual | R$ 480,26 | - | - | - |
| A) Eficiência (LED + refrigeração) | R$ 389,62 | R$ 90,64 | R$ 350 | ~3,9 meses |
| B) Solar 3,58 kWp | R$ 118,53 | R$ 361,73 | R$ 10.739 | ~2,5 anos |
| C) A + solar 2,82 kWp (recomendado) | R$ 107,65 | R$ 372,61 | R$ 8.800 | ~2,0 anos |

![Comparação](docs/comparacao.png)

Cálculos passo a passo, sensibilidade (preço do sistema, tarifa e Fio B) e saldo em 25 anos: `docs/calculos.md`.

## Justificativa das recomendações (resumo; detalhes em `docs/justificativas.md`)
- **Custo:** A custa R$ 350 e se paga em meses; B e C economizam ~75% da conta, mas exigem R$ 9 a 11 mil.
- **Viabilidade:** solar exige telhado sem sombra, imóvel próprio ou autorizado, homologação na distribuidora e
  capital ou financiamento. Sem telhado, avaliar geração compartilhada.
- **Impacto ambiental:** ~13,5 kg CO2/mês evitados em C. É pouco porque a matriz elétrica brasileira já é
  majoritariamente renovável; o ganho principal é financeiro.
- **Recomendação:** fazer A primeiro e dimensionar o solar depois (C): sistema menor e retorno mais curto.

## Limitações
Estimativas, não garantias. Dependem dos equipamentos reais, da tarifa, do telhado (sombra, inclinação), do clima e
das regras vigentes (Lei 14.300/Fio B; a partir de 2029 a ANEEL define novas regras). Não modelamos reajuste de
tarifa, degradação dos painéis, financiamento, impostos do negócio nem a simultaneidade real entre geração e consumo.
O saldo em 25 anos é uma simplificação. Peça pelo menos 3 orçamentos antes de decidir.

## Testes com usuários
Protocolo e registros em `docs/testes_usuarios.md`.
