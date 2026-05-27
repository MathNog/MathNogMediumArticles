# [TÍTULO — ex.: Explorando sazonalidade em séries temporais: um roteiro visual]

> **Status:** esqueleto — preencher placeholders; não é o texto final.

| Campo | Placeholder |
|-------|-------------|
| Autor | `[AUTOR]` |
| Data | `[DATA]` |
| Repositório | `[LINK REPO]` |
| Série principal do artigo | Temperatura 2 m — Rio de Janeiro (`temp_rio`) |
| Granularidades | Horária, diária, mensal |
| Período | `[ANO_INÍCIO]`–`[ANO_FIM]` |
| Fonte dos dados | Open-Meteo ERA5 — `[LINK / CITAÇÃO]` |

---

## 1. Introdução

### 1.1 O que é sazonalidade

`[TEXTO: Definição operacional — padrões que se repetem em escalas de tempo conhecidas (hora do dia, dia da semana, mês, estação, ano). Diferenciar sazonalidade determinística vs. ciclo estocástico, se fizer sentido para o público.]`

`[TEXTO: Exemplos intuitivos em 1–2 frases — energia, varejo, clima, tráfego.]`

### 1.2 Por que investigar sazonalidade antes de modelar

`[TEXTO: Motivação — baseline, escolha de granularidade, features de calendário, diagnóstico de resíduos, evitar confundir tendência com ciclo.]`

`[BULLET LIST — 3–5 razões; sem desenvolver cada uma aqui]`

### 1.3 Séries usadas neste artigo

| Série | Variável | Granularidade | Uso no roteiro |
|-------|----------|---------------|----------------|
| `temperature_rio_hourly.csv` | `temperature_2m_c` | Horária | Intraday, heatmaps, boxplots por hora/dia |
| `temperature_rio_daily.csv` | `temperature_2m_c` | Diária | Semanal, anual (dia do ano) |
| `temperature_rio_monthly.csv` | `temperature_2m_c` | Mensal | Boxplot por mês, anual (overlay por ano) |

`[TEXTO: 1 parágrafo — por que temperatura no Rio é um bom exemplo didático (sinal claro, múltiplas escalas).]`

`[TEXTO OPCIONAL: Mencionar que o mesmo pipeline serve para outras séries — trocar CSV e `CONFIG` em `run_seasonality_analysis.py`.]`

---

## 2. Setup e reprodutibilidade

> **Lógica da seção:** o leitor precisa gerar os mesmos 18 gráficos antes de seguir a análise.

### 2.1 Estrutura do projeto

```
SeasonalityGraphs/
├── code/           # leitura CSV, estilo, funções de plot, orquestrador
├── data/           # CSVs (gitignored)
├── imgs/           # figuras exportadas (gitignored)
└── article_skeleton.md
```

### 2.2 Dependências

`[TEXTO: Uma linha — Python 3.x, pandas, matplotlib, seaborn, numpy.]`

```bash
# [PLACEHOLDER — criar venv e instalar]
python -m venv .venv
source .venv/bin/activate
pip install pandas matplotlib seaborn numpy
```

### 2.3 Download dos dados (opcional)

> **Lógica:** só aparece se o artigo incluir aquisição; senão, pular para 2.4.

```bash
# [PLACEHOLDER — comando real]
python code/download_temperature_rio.py
```

`[TEXTO: Descrever saída esperada em data/*.csv — sem narrativa longa.]`

### 2.4 Gerar todas as figuras

```bash
cd SeasonalityGraphs/code
../.venv/bin/python run_seasonality_analysis.py
```

`[TEXTO: Uma frase — figuras salvas em imgs/ com prefixo temp_rio_XX_.]`

---

## 3. Roteiro da investigação (mapa)

> **Lógica global do artigo:** visão geral → médias em 2D → distribuições marginais → perfis sazonais (cenários + agregados) → visão anual → painel resumo → subseries para validar padrões.

| Etapa | Pergunta que o bloco responde | Figuras |
|-------|------------------------------|---------|
| A | A série parece estável? Há tendência ou buracos? | 01–04 |
| B | Onde (hora × mês/dia) a média é alta/baixa? | 05–06 |
| C | A dispersão muda por hora, dia da semana ou mês? | 07–09 |
| D | Como o ciclo se comporta em cada escala (mês, dia, semana)? | 10–12 |
| E | Os anos concordam no ciclo anual? | 13–14 |
| F | Os três ciclos juntos, em um painel | 15 |
| G | O padrão mensal/semanal se mantém dentro de cada estrato? | 16–18 |

`[TEXTO: 1 parágrafo conectando as etapas — sem interpretar os resultados ainda.]`

---

## 4. Etapa A — Visão geral da série

> **Lógica:** estabelecer contexto temporal antes de decompor por calendário.

### 4.1 Série horária

`[TEXTO: 1–2 frases — o que observar no gráfico.]`

![01 — time plot hourly](imgs/temp_rio_01_time_plot_hourly.png)

```python
# [PLACEHOLDER — snippet mínimo: carregar CSV e plot_time_series]
from read_timeseries_csv import load_series_from_csv
from seasonality_graphs import plot_time_series

hourly = load_series_from_csv("data/temperature_rio_hourly.csv", "datetime", "temperature_2m_c")
plot_time_series(hourly, title="...", ylabel="Temperature (°C)")
```

`[INSIGHT: …]`  
`[CAVEAT: …]` — ex.: sazonalidade visualmente misturada com ruído de curto prazo

### 4.2 Série diária

`[TEXTO: placeholder]`

![02 — time plot daily](imgs/temp_rio_02_time_plot_daily.png)

### 4.3 Série mensal

`[TEXTO: placeholder]`

![03 — time plot monthly](imgs/temp_rio_03_time_plot_monthly.png)

### 4.4 Três granularidades lado a lado

> **Lógica:** mostrar que a mesma fenomenologia aparece em escalas diferentes.

`[TEXTO: placeholder]`

![04 — granularities](imgs/temp_rio_04_time_plot_granularities.png)

`[INSIGHT: …]`  
`[TRANSIÇÃO: …]` — ex.: “com a série contextualizada, cruzamos hora com calendário”

---

## 5. Etapa B — Heatmaps (médias em duas dimensões)

> **Lógica:** localizar *quando* (hora) e *em qual contexto de calendário* (mês ou weekday) os valores médios são extremos.

### 5.1 Hora × mês

`[TEXTO: placeholder — como ler eixos e cor]`

![05 — heatmap hour × month](imgs/temp_rio_05_heatmap_hour_x_month.png)

```python
# [PLACEHOLDER]
from seasonality_graphs import plot_heatmap_hour_month
plot_heatmap_hour_month(hourly, colorbar_label="Temperature (°C)")
```

`[INSIGHT: …]` — ex.: blocos quentes/frios, assimetria manhã vs. noite

### 5.2 Hora × dia da semana

`[TEXTO: placeholder]`

![06 — heatmap hour × weekday](imgs/temp_rio_06_heatmap_hour_x_weekday.png)

`[INSIGHT: …]`  
`[TRANSIÇÃO: …]` — ex.: “médias não mostram dispersão; próximo passo: boxplots”

---

## 6. Etapa C — Distribuições por feature de calendário

> **Lógica:** complementar médias com espalhamento e outliers por categoria.

### 6.1 Por hora do dia

`[TEXTO: placeholder]`

![07 — boxplot by hour](imgs/temp_rio_07_boxplot_by_hour.png)

`[INSIGHT: …]`

### 6.2 Por dia da semana

`[TEXTO: placeholder]`

![08 — boxplot by weekday](imgs/temp_rio_08_boxplot_by_weekday.png)

`[INSIGHT: …]`

### 6.3 Por mês (série mensal nativa)

`[TEXTO: placeholder]`

![09 — boxplot by month](imgs/temp_rio_09_boxplot_by_month.png)

`[INSIGHT: …]`  
`[TRANSIÇÃO: …]` — ex.: “agora perfis sazonais com todos os cenários sobrepostos”

---

## 7. Etapa D — Perfis sazonais (cenários + agregados)

> **Lógica:** em cada escala, plotar **uma linha por cenário** (ano / dia / semana) + **média** + **P10/P90** entre cenários no mesmo eixo x.  
> Esta é a seção central do artigo.

### 7.1 Convenção visual (referência rápida)

| Camada | Significado | Figuras |
|--------|-------------|---------|
| Nuvem azul clara | Um cenário por período (ex.: um ano) | 10–12, 15 (painéis 1–2) |
| Linhas tracejadas P10/P90 | Envelope entre cenários | 10–12 |
| Linha vermelha | Média entre cenários | 10–12 |

`[TEXTO: 1 frase — não repetir legenda completa em cada subplot.]`

### 7.2 Padrão mensal (um cenário = um ano)

> **Lógica:** ciclo anual agregado por mês; comparar anos.

`[TEXTO: placeholder]`

![10 — seasonal monthly mean](imgs/temp_rio_10_seasonal_monthly_mean.png)

```python
# [PLACEHOLDER]
from seasonality_graphs import plot_seasonal_monthly_mean
plot_seasonal_monthly_mean(hourly, ylabel="Temperature (°C)")
```

`[INSIGHT: …]`

### 7.3 Padrão intraday (um cenário = um dia)

> **Lógica:** forma típica do dia; dispersão entre dias.

`[TEXTO: placeholder]`

![11 — seasonal intraday](imgs/temp_rio_11_seasonal_intraday.png)

`[INSIGHT: …]`

### 7.4 Padrão semanal (um cenário = uma semana)

> **Lógica:** efeito weekday em médias diárias; comparar semanas.

`[TEXTO: placeholder]`

![12 — seasonal weekly](imgs/temp_rio_12_seasonal_weekly.png)

`[INSIGHT: …]`  
`[TRANSIÇÃO: …]` — ex.: “ciclos intra-semana e intra-dia vistos; falta o ciclo ao longo do ano”

---

## 8. Etapa E — Ciclo anual

> **Lógica:** uma linha por ano no eixo dia-do-ano; avaliar estabilidade interanual.

### 8.1 Série diária (dia do ano)

`[TEXTO: placeholder]`

![13 — seasonal annual daily](imgs/temp_rio_13_seasonal_annual_daily.png)

```python
# [PLACEHOLDER]
from seasonality_graphs import plot_seasonal_annual
plot_seasonal_annual(daily, ylabel="Temperature (°C)")
```

`[INSIGHT: …]`

### 8.2 Série mensal (um ponto por mês, por ano)

`[TEXTO: placeholder]`

![14 — seasonal annual monthly](imgs/temp_rio_14_seasonal_annual_monthly.png)

`[INSIGHT: …]`

---

## 9. Etapa F — Painel multiperíodo

> **Lógica:** síntese visual para o leitor que quer os três ciclos principais numa única figura.

`[TEXTO: placeholder — 2 frases]`

![15 — multiperiod panel](imgs/temp_rio_15_seasonal_multiperiod_panel.png)

`[INSIGHT: …]` — ex.: relação entre picos diários e sazonalidade anual

---

## 10. Etapa G — Subseries (validação dentro do estrato)

> **Lógica:** dentro de cada mês ou weekday, a série ainda varia no tempo; médias por estrato ajudam a confirmar se o padrão dos perfis (seção 7) se mantém.

### 10.1 Subseries mensal (dados diários agregados por mês)

`[TEXTO: placeholder]`

![16 — subseries monthly daily](imgs/temp_rio_16_subseries_monthly_daily.png)

### 10.2 Subseries mensal (série mensal nativa)

`[TEXTO: placeholder]`

![17 — subseries monthly native](imgs/temp_rio_17_subseries_monthly_native.png)

### 10.3 Subseries por weekday

`[TEXTO: placeholder]`

![18 — subseries weekday](imgs/temp_rio_18_subseries_weekday.png)

`[INSIGHT: …]`  
`[CAVEAT: …]` — ex.: meses com poucos pontos, anos bissextos, etc.

---

## 11. Síntese e próximos passos

> **Lógica:** fechar o roteiro sem reescrever cada figura — tabela ou checklist.

### 11.1 Checklist do que o EDA respondeu

| Pergunta | Respondida em | Resposta (preencher) |
|----------|---------------|----------------------|
| Há sazonalidade intraday? | 07, 11 | `[…]` |
| Há efeito de weekday? | 06, 08, 12, 18 | `[…]` |
| Há ciclo anual estável? | 09, 10, 13, 14 | `[…]` |
| Anos são homogêneos? | 10, 13, 14 | `[…]` |

### 11.2 Próximos passos (fora do escopo do artigo)

`[BULLET LIST — placeholder]`

- Decomposição STL / MSTL  
- Modelos com regressores de calendário  
- Outra série de exemplo (`[NOME]`) com o mesmo pipeline  

### 11.3 Referências e código

`[LINK REPO]` · `[LINK NOTEBOOK OPCIONAL]` · `[CITAÇÕES DADOS / BIBLIOGRAFIA]`

---

## Apêndice A — Índice de figuras

| # | Arquivo | Função |
|---|---------|--------|
| 01 | `temp_rio_01_time_plot_hourly.png` | Série horária |
| 02 | `temp_rio_02_time_plot_daily.png` | Série diária |
| 03 | `temp_rio_03_time_plot_monthly.png` | Série mensal |
| 04 | `temp_rio_04_time_plot_granularities.png` | Comparação de granularidades |
| 05 | `temp_rio_05_heatmap_hour_x_month.png` | Média hora × mês |
| 06 | `temp_rio_06_heatmap_hour_x_weekday.png` | Média hora × weekday |
| 07 | `temp_rio_07_boxplot_by_hour.png` | Distribuição por hora |
| 08 | `temp_rio_08_boxplot_by_weekday.png` | Distribuição por weekday |
| 09 | `temp_rio_09_boxplot_by_month.png` | Distribuição por mês |
| 10 | `temp_rio_10_seasonal_monthly_mean.png` | Perfil mensal (cenários + P10/P90 + média) |
| 11 | `temp_rio_11_seasonal_intraday.png` | Perfil intraday |
| 12 | `temp_rio_12_seasonal_weekly.png` | Perfil semanal |
| 13 | `temp_rio_13_seasonal_annual_daily.png` | Anual (diário, por ano) |
| 14 | `temp_rio_14_seasonal_annual_monthly.png` | Anual (mensal, por ano) |
| 15 | `temp_rio_15_seasonal_multiperiod_panel.png` | Painel 3 períodos |
| 16 | `temp_rio_16_subseries_monthly_daily.png` | Subseries mês (daily) |
| 17 | `temp_rio_17_subseries_monthly_native.png` | Subseries mês (monthly) |
| 18 | `temp_rio_18_subseries_weekday.png` | Subseries weekday |

---

## Apêndice B — Notas de redação (não publicar)

- `[INSIGHT]` = interpretação após a figura (1–3 frases).  
- `[CAVEAT]` = limitação metodológica ou de dados.  
- `[TRANSIÇÃO]` = frase-ponte para a próxima seção.  
- Manter código **executável** ou colapsável; evitar blocos longos sem figura adjacente.  
- Ordem das seções 4→10 é a narrativa recomendada; heatmaps antes de perfis evita spoiler da dispersão.
