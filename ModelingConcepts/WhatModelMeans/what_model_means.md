# O que significa modelar uma série temporal?

## Motivação

O mundo é complicado e a gente pode tentar interpretar a realidade de diversas maneiras.

Uma maneira possível é tentar encaixar parte da realidade em um conjunto de premissas que podemos expressas em linguagem matemática.

Pense, por exmeplo, que queremos tentar entender como a temperatura média diária de uma cidade evolui. Podemos supor que a temperatura de um dia não deveria, normalmente, mudar muito em relação à temperatura do dia anterior. Dias próximos deveriam carregar informação sobre a temperatura diária futura. Por outro lado, sabemos que as temperaturas médias mudam junto com as estações, então, para saber a temeperatura média do dia seguinte, deveria ser informativo olhar a temperatura típida de um dia da estação corrente e, para isso, precisamos voltar pelo menos 1 ano no passado.

Esse tipo de raciocínio pode ser traduzido para uma linguagem matemática. Temos um dado que queremos entender e prever. Para isso, vamos assumir hipóteses sobre o comportamento desse dado e desenvolver um **modelo** que carregue essas hipóteses sobre nossos dados. Depois de escrever e "descobrir" o modelo, devemos avaliar se ele é adequado, pois podemos ter errado em nossas hipóteses. 

Vamos entrar um pouco mais na matemática por detrás desse raciocício usando séries temporais como exemplo.

## O que significa modelar uma série temporal?

Primeiro de tudo: o que é uma série temporal? 

Gostaria de dar duas respostas. A primeira, intuitiva. A segunda, um pouco mais precisa.

 1. É uma informação numérica (temperatura, preço, velocidade, ...) medida em intervalos constantes de tempo (1 minuto, 1 hora, 1 semana, 1 mês, ...) que costuma ter algum grau de aleatoriedade.
 2. É a realização de um processo estocástico de variável contínua em tempo discreto. Vish! Vamos simplificar. **continuar**

Modelar uma série temporal significa obter uma função que, dado os valores passados da série (além de outros parâmetros), conseguimos obter uma "aproximação" do valor atual/corrente da série temporal.

Nosso objetivo é descrever, por meio de uma equação (ou várias!), o comportamento da série temporal, dado o seu passado.

$$ y_t = f(y_{t-1}, y_{t-2},...,y_2, y_1; \mathbf{\theta})$$

No entanto, seria arrogância presumir que um modelo poderia explicar perfeitamente a realidade. Por isso, costumamos somar um termo $\varepsilon_t$ que é a representação de um erro aleatório que o modelo não vai (ou não deveria) explicar. 

$$ y_t = f(y_{t-1}, y_{t-2},...,y_2, y_1; \mathbf{\theta}) +  \varepsilon_t $$

A adição desse termo é extremamente importante. Funções sem ele podem ser vistas como simples métodos de previsão. Mas, se quisermos falar de um **modelo** (estatístico, de ML, DL), precisamos definir esse termo aleatório. Dado que ele está representando a parte da realidade que o modelo não irá explicar, é comum definirmos hipóteses sobre esse termo. A mais importante é ele ser uma variável aleatória de média 0, pois não queremos que o modelo seja viesado, isto é, que o modelo erre consistentemente para cima ou para baixo. Outras hipóteses podem ser feitas (ausência de autocorrelação, homocedasticidade) mas vou me contentar apenas com a ausência de viés. Para manter as coisas simples, podemos pensar que esse termo, por ser, por hipótese, aleatório, não deve apresentar nenhum tipo de estrutura temporal ou padrão perceptível. 

Vamos pensar em algumas dinâmicas simples.

Meu modelo pode ser tão simples quanto dizer que o valor corrente da série temporal ($y_t$) será igual ao valor imediatamente anterior ($y_{t-1}$). É modelo é bem famoso! É o modelo de *Random Walk* ou de Passeio Aleatório.

$$y_t = y_{t-1} +  \varepsilon_t$$

Podemos pensar em algo mais elaborado. E se nosso modelo for a média dos últimos 3 valores?

$$y_t = \frac{y_{t-1} + y_{t-2} +y_{t-3}}{3} +  \varepsilon_t$$

Podemos pensar em algo ainda mais elaborado. Que tal a combinação linear do últimos $p$ valores passados? Esse é um dos modelos mais famosos de séries temporais! É o chamado modelo *AR(p)*, ou Autoregressivo de ordem *p*.

$$y_t = \beta_0 + \sum_{i=1}^{p}\beta_i\cdot y_{t-i} + \varepsilon_t$$

Esse modelo é mais elaborado porque precisamos descobrir, ou estimar, os valores desconhecidos dos parâmetros $\beta_0,...,\beta_p$. Isso é o que o linguajar de ML e DL chama de "treinar o modelo". Significa aprender ou descobrir os valores desconhecidos dos parâmetros do modelo.

Note que estamos, a cada tentativa, impondo uma forma funcional específica, isto é, uma "regra de evolução" daquele dado ao longo do tempo.

**Moral da história:**

Modelar a série temporal é, portanto, escolher a forma funcional de $f$ e, além disso, estimar possíveis parâmetros desconhecidos. Ao fazer isso, estamos tentando representar uma parte da realidade 

É importante dizer que existem caminhos não paramétricos, onde não precisamos impor hipóteses ou formas funcionais específicas para especificar o modelo. Esse caminho nos leva aos modelos de Machine e Deep Learning. Este artigo, por ser bem introdutório, se atém a modelos estatísticos clássicos de séries temporais.

Temos inúmeros modelos disponíveis para escolher!

- Modelos Estatísticos Clássicos:
  - Família SARIMA
    - Modelos de Média Móvel (MA)
    - Modelos Autorregressivos (AR)
    - Modelos Autorregressivos de Média Móvel (ARMA)
    - Modelos Autorregressivos Integrados de Média Móvel (ARIMA)
    - Modelos Sazonais Autorregressivos Integrados de Média Móvel (SARIMA)
  - Modelos de Componentes Não Observáveis
    - Modelos de Suavização Exponencial (ETS)
    - Modelos Estruturais

- Modelos de Machine Learning:
    - Modelos de Regressão (sim, a primeira aula de ML sempre é Regressão Linear):
        - Regressão Linear
        - Regressão Ridge
        - Regressão Lasso
        - Regressão de Vetores de Suporte (SVR)
    - Modelos Baseados em Árvore:
        - Florestas Aleatórias (Random Forest)
        - Gradient Boosting Machines (GBM)
        - XGBoost
        - LightGBM
        - CatBoost

- Modelos de Deep Learning - baseados em Redes Neurais:
      - Redes Neurais Artificiais (ANN)
      - Redes Neurais Recorrentes (RNN)
      - Long Short-Term Memory (LSTM)
      - Gated Recurrent Units (GRU)
      - Redes Neurais Convolucionais (CNN)
      - Redes Neurais Convolucionais Recorrentes (RCNN)
      - Transformers


## Problema! Como escolher um modelo de série temporal?

Essa escolha depende, principalmente, de dois fatores:
1. O comportamento da série temporal,
2. O contexto do problema.

O comportamento da série temporal é descoberto via EDA. Podemos observar o gráfico da série, estudar a presença de sazonalidade, existencia de tendencia, estacionariedade, autocorrelacao e afins. Para se aprofundar mais nesse assunto super importante, dique ligado nos próximos artigos que sairão!

O contexto do problema dita, em grande parte, a complexidade e interpretabilidade do modelo. Se você precisa de re-estimações recorrentes em pouco tempo computacional, precisará de modelos mais simples, como os clássicos. Se necessita de interpretabilidade, também. Se pode assumir um *black-box* não interpretável pois sua aplicação só se importa com a qualidade da previsão, por exemplo, modelos de ML e DL podem ser boas opções, contando que existem dados suficientes para treino.

Vou trazer duas famílias de modelos apenas como exemplos, sem entrar nos detalhes de cada um. Para estudar esses modelos em profundidade, fique ligado em novos artigos que virão no futuro.

## Trazer um exemplo de série temporal (AirLine)

(Colocar e explicar brevemente a série airline e dizer que ela é uma série clássica de qualquer aula de séries temporais)

## Família ETS - Error, Trend, Seasonality

A família de modelos ETS nasceu dos métodos de previsão de armotecimento exponencial (exponential smoothing) que almeja decompor a série em componentes de Erro, Tendência e Sazonalidade, combinando tais componentes tanto de forma aditiva quanto multiplicativa.

A partir de diferentes combinações, podemos gerar modelos sem tendência e sazonalidade (amortecimento exponencial simples), modelos com tendência e sem sazonalidae (equivalente ao método de Holt), com tendência e sazonalidade (Holt Winters), e mais. A imagem abaixo dá todas as combinações possíveis dessas componentes, gerando a família de modelos ETS, onde A significa combinação aditiva, M multiplicativa e N ausência de componentes. Por exemplo, o ETS(A, A, A) é equivalente ao método de Holt Winters, enquanto o ETS(A, N, N) é um amortecimento exponencial simples.

**A equação do modelo ETS**

![ETS Model Equation](imgs/ets_taxonomy.png)

**Por que um ETS pode ser adequado?**

Essa família de modelos é um excelente primeiro exemplo por suas equações serem intuitivas e flexíveis. Se vemos, por exemplo, que a série airline possui tendência e sazonalidade, faz sentido testarmos o ETS(A, A, A), enquanto um ETS(A, N, N) parece inadequado.

Façamos exatamente isso! 

*Estimando dois modelos ETS*

Vamos estimar dois modelos ETS distintos. Ao visualizar a série temporal, fica claro que ela possui tendência e sazonalidade. Portanto, um dos modelos será o ETS(A, A, A), que significa que o erro, a tendência e a sazonalidade são aditivas. Vamos estimar um segundo ETS, claramente menos adequado, ETS(A, N, N), que é um modelo sem tendência nem sazonalidade. 

Para estimar esses modelos, vamos usar a biblioteca statsforecast (colocar referencia) de Python e usar todo o período disponível da série para estimar o modelo.

(Adicionar código python para estimar os modelos usando toda a série)

## Como avaliar um modelo estimado?

Maravilha, conversamos longamente sobre o que é um modelo, como escolher uma família de modelos e até vimos exemplos rápidos de famílias clássicas de modelos de séries temporais.

Mas como podemos investigar se escolhemos bem? Se o modelo escolhido foi bem especificado?

É aqui que voltamos a olhar para o $\varepsilon_t$. Uma vez estimado um modelo, podemos observar a série de resíduos do modelo, $\hat{\varepsilon}_t$, que nada mais é do que a realização da variável aleatória $\varepsilon_t$. Ele é o erro do modelo em relação aos dados que foram usados para sua estimação.

$$ \hat{\varepsilon}_t = y_t - f(y_{t-1}, y_{t-2},...,y_2, y_1; \mathbf{\hat{\theta}}) $$

E é aqui que as hipóteses que fizemos sobre o termo de erro aleatório se tornam importantes. Se nós, ao definirmos o modelo, assumimos que esse erro deveria ter média zero, então os resíduos do modelo devem ter a média (estatisticamente) igual a zero. Toda hipótese feita sobre a natureza do termo de erro aleatório pode (e deve!) ser investigada nos resíduos.

Como nosso objetivo não é falar profundamente de diagnóstico de resíduos, vamos nos contentear e observar a média deles e o plot temporal, para tentar visualizar se as hipóteses que fizemos valem. Se valerem, podemos concluir que o modelo foi bem especificado. Se não, o modelo não está adequado e devemos tentar melhorá-lo.