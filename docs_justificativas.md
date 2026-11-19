# Justificativas das recomendações

## Por que este público e este problema
Pequenos comércios de comunidade têm margem curta e usam muita refrigeração (ligada 24 h). A conta de luz é um
custo fixo relevante e previsível de reduzir. Um assistente em linguagem simples ajuda quem não tem acesso a
consultoria energética.

## Critérios usados para comparar (mesma necessidade, mesmo período de 30 dias)
| Critério | A) Eficiência | B) Solar | C) A + Solar |
|---|---|---|---|
| Custo inicial | R$ 350 | ~R$ 10,7 mil | ~R$ 8,8 mil |
| Economia mensal | ~R$ 91 | ~R$ 362 | ~R$ 373 |
| Retorno | ~4 meses | ~2,5 anos | ~2,0 anos |
| Viabilidade | Qualquer comerciante, inclusive inquilino | Exige telhado, sol, autorização do proprietário, homologação | Igual a B, com sistema menor |
| Risco | Muito baixo | Regulatório (Fio B), preço, sombreamento | Menor que B |
| Impacto ambiental | -3 kg CO2/mês | -13 kg CO2/mês | -13,5 kg CO2/mês |
| Fonte renovável | Não | Sim (solar) | Sim (solar) |

## Por que recomendar C
1. A eficiência reduz o consumo, então o sistema solar necessário é menor (2,82 contra 3,58 kWp) e mais barato.
2. A economia total é maior e o retorno mais curto.
3. A parte de eficiência pode ser feita imediatamente, mesmo que o solar dependa de capital ou do proprietário.

## Por que o ganho ambiental parece pequeno
O fator de emissão da rede brasileira é baixo (0,0385 kg CO2/kWh, média de 2023 segundo o MCTI). Evitar 350 kWh/mês
evita só ~13 kg de CO2. O argumento principal para o comerciante é financeiro e de previsibilidade da conta;
o assistente é transparente sobre isso em vez de exagerar o benefício ambiental.

## Quando NÃO recomendar solar
- Imóvel alugado sem autorização do proprietário ou contrato curto.
- Telhado sombreado, frágil ou com pouca área.
- Consumo muito baixo (perto do mínimo faturável de 30/50/100 kWh).
- Sem capital e sem acesso a crédito com juros compatíveis: priorizar A e avaliar geração compartilhada.

## Decisões de modelagem
- **Custo de disponibilidade:** a conta nunca zera (mínimo faturável de 50 kWh, bifásico).
- **Fio B:** perda de crédito de 12% (2026) por simplificação conservadora; sensibilidade até 17% (2028).
- **Sem reajuste de tarifa:** conservador para o retorno, mas o saldo de 25 anos é indicativo.
- **Consumo da conta:** o usuário pode informar o consumo real (`simular consumo=...`), substituindo a soma de equipamentos.
