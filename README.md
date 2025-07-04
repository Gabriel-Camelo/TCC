# TCC - PROPOSTA DE SISTEMA VESTÍVEL COM INTELIGÊNCIA ARTIFICIAL PARA SUPORTE A INDIVÍDUOS COM TRANSTORNO DO ESPECTRO AUTISTA

**Autor:** [Gabriel Camelo]
**Orientador:** [Almir Moura]

---

#### **1. Introdução**

O avanço das tecnologias de Informação e Comunicação (TIC) e a ampla adoção de dispositivos eletrônicos de consumo, como pulseiras e relógios inteligentes, apresentam uma oportunidade sem precedentes para o monitoramento da saúde e do bem-estar do usuário em seu cotidiano. [cite_start]A capacidade de obter feedback em tempo real sobre mudanças fisiológicas, monitorar o estresse e até detectar emoções está se tornando uma realidade tecnológica[cite: 1]. [cite_start]Sendo facilmente portáteis e discretos, estes dispositivos podem seguir o usuário em suas atividades diárias de forma não intrusiva[cite: 2].

[cite_start]O Transtorno do Espectro Autista (TEA) representa um desafio formidável para o diagnóstico e classificação devido à sua natureza complexa e heterogênea[cite: 3]. [cite_start]Indivíduos com TEA frequentemente enfrentam desafios significativos na comunicação e no gerenciamento da desregulação emocional, o que pode levar a uma redução na qualidade de vida[cite: 1]. [cite_start]A ansiedade, em particular, é uma comorbidade psiquiátrica prevalente, com taxas que variam de 11% a 84% nesta população[cite: 1]. [cite_start]Para muitos, especialmente aqueles com maiores necessidades de suporte e com dificuldade em identificar e descrever seus próprios estados emocionais (Alexitimia)[cite: 1], a comunicação do sofrimento torna-se uma barreira expressiva.

[cite_start]A aplicação de Machine Learning (ML) na classificação de TEA é promissora, mas enfrenta desafios como a alta dimensionalidade dos dados[cite: 3]. Neste contexto, o presente trabalho propõe a concepção de um sistema de tecnologia assistiva vestível (*wearable*) para indivíduos com TEA. [cite_start]O sistema integra sensores fisiológicos e Inteligência Artificial (IA), sendo que algoritmos de IA podem apoiar o processo de gerenciamento de estresse e ansiedade[cite: 2]. [cite_start]O objetivo é detectar precocemente os sinais de desregulação emocional que precedem crises comportamentais, utilizando uma abordagem metodológica que otimiza os dados de entrada para aumentar a precisão da classificação[cite: 3]. [cite_start]A literatura aponta a necessidade de mais estudos que empreguem IA e computação afetiva para apoiar intervenções terapêuticas[cite: 2]. Ao identificar esses padrões, o sistema visa fornecer um suporte proativo, tanto alertando cuidadores quanto possibilitando intervenções ambientais automatizadas.

#### **2. Fundamentação Teórica**

##### **2.1 Transtorno do Espectro Autista e a Necessidade de Suporte Emocional**

[cite_start]O Transtorno do Espectro Autista (TEA) é uma deficiência do neurodesenvolvimento caracterizada principalmente por comprometimento no comportamento social e na comunicação[cite: 2]. [cite_start]A dificuldade em gerenciar o estresse e a ansiedade pode culminar em comportamentos desafiadores, que representam uma barreira para a participação social[cite: 1]. [cite_start]Tecnologias vestíveis surgem como uma solução potencial que pode complementar as intervenções comportamentais existentes [cite: 1][cite_start], oferecendo aos cuidadores uma janela para os estados internos de indivíduos incapazes de comunicar seus sentimentos[cite: 2].

##### **2.2 Respostas Fisiológicas e Biomarcadores de Estresse no TEA**

A detecção de estados emocionais como o estresse pode ser realizada através do monitoramento de sinais fisiológicos. [cite_start]Sensores vestíveis são capazes de medir diversas variáveis, como frequência cardíaca (HR), eletromiograma (EMG), eletrocardiograma (ECG), atividade eletrodérmica (EDA), temperatura corporal, saturação de oxigênio (SpO2) e taxa de respiração (RR)[cite: 2]. [cite_start]Pessoas com TEA podem exibir padrões de resposta fisiológica diferentes dos seus pares neurotípicos [cite: 1][cite_start], o que justifica a necessidade de sistemas que aprendam os padrões individuais de cada usuário, demandando soluções altamente personalizáveis[cite: 2]. Com base em consulta com clínicos, o artigo de Taj-Eldin et al. [cite_start](2018) sugere que os parâmetros-chave em qualquer dispositivo com esta finalidade são, no mínimo, a **frequência cardíaca (HR) e a atividade eletrodérmica (EDA)**[cite: 1].

##### **2.3 Otimização de Dados com Análise Fatorial**

[cite_start]Devido à complexidade dos dados em estudos sobre TEA, que frequentemente possuem alta dimensionalidade, a seleção de características relevantes para a classificação por Machine Learning é um desafio significativo[cite: 3]. [cite_start]Uma abordagem para lidar com essa complexidade é a **Análise Fatorial**, um método estatístico que visa descobrir a estrutura latente ou as dimensões que explicam as correlações observadas entre as variáveis[cite: 3]. [cite_start]Ao identificar esses componentes latentes, é possível capturar a variância compartilhada entre as variáveis e reduzir a dimensionalidade do espaço de características original[cite: 3]. O estudo de Nayak et al. [cite_start](2025) demonstra que a aplicação da análise fatorial para reduzir a dimensionalidade antes da classificação melhora notavelmente o desempenho dos modelos de Machine Learning, como Regressão Logística e SVM, para a classificação de TEA em crianças[cite: 3].

##### **2.4 Tecnologias Assistivas Vestíveis e Inteligência Artificial**

[cite_start]A revisão da literatura indica que o mercado de wearables para monitoramento fisiológico é abundante, porém, a maioria dos dispositivos (88%) é projetada para a população geral[cite: 1]. Um ponto fundamental para este projeto é o uso de IA. [cite_start]Embora a Computação Afetiva ocupe uma posição proeminente [cite: 2][cite_start], a **Inteligência Artificial (IA) foi implementada em pouquíssimos estudos revisados, principalmente para detectar comportamentos estereotipados**[cite: 2]. Isso revela uma lacuna significativa e uma oportunidade para trabalhos que explorem IA de forma mais robusta para predição de crises.

##### **2.5 Fatores de Usabilidade e Design para a População com TEA**

Para que uma tecnologia assistiva seja adotada por indivíduos com TEA, o design e a usabilidade são fatores críticos. [cite_start]O conforto é frequentemente o fator mais importante[cite: 1]. [cite_start]Há uma preferência por dispositivos feitos de materiais flexíveis e macios [cite: 1][cite_start], uma vez que muitas crianças podem apresentar hipersensibilidade a roupas e outros materiais[cite: 2]. [cite_start]O design deve ser discreto e assemelhar-se a produtos de consumo geral para evitar estigma[cite: 1]. [cite_start]Nesse sentido, **smartwatches e pulseiras parecem ser uma solução mais ideal do que outros sensores mais obstrusivos**[cite: 2].

##### **2.6 Desafios e Limitações na Pesquisa Atual**

A literatura aponta diversos desafios que dificultam o avanço da área. Os principais problemas identificados nos estudos existentes incluem:
* [cite_start]Amostras pequenas (a maioria com menos de 11 participantes)[cite: 2].
* [cite_start]Resultados não generalizáveis[cite: 2].
* [cite_start]Falta de grupos de controle na maioria das pesquisas[cite: 2].
* [cite_start]Subjetividade na avaliação, com uso predominante de questionários customizados e não validados[cite: 2].
* [cite_start]Considerações tecnológicas como custo, tamanho e vida útil da bateria[cite: 2].
* [cite_start]Foco excessivo em ambientes de laboratório controlados, com necessidade de mais testes em condições reais[cite: 2].

#### **3. Proposta do Sistema**

##### **3.1 Objetivo Geral**

Propor a arquitetura de um sistema vestível integrado com Inteligência Artificial, projetado para monitorar sinais fisiológicos, detectar padrões precursores de crises de desregulação emocional em indivíduos com TEA de alto nível de suporte e acionar um mecanismo de suporte proativo, utilizando Análise Fatorial para otimizar a precisão da classificação.

##### **3.2 Objetivos Específicos**
* Definir os biomarcadores fisiológicos mais relevantes para a detecção de estresse e ansiedade.
* Especificar a arquitetura de hardware do dispositivo vestível, considerando os fatores de usabilidade.
* Descrever a arquitetura de software, detalhando o pipeline de processamento de dados, incluindo o uso de Análise Fatorial para redução de dimensionalidade e um modelo de Machine Learning para classificação personalizada.
* Propor um mecanismo de intervenção em "ciclo fechado" (*closed-loop*).
* Delinear um protocolo de validação que busque superar limitações de estudos anteriores.

##### **3.3 Arquitetura do Sistema**

O sistema proposto será composto por três módulos principais:
1.  [cite_start]**Módulo de Detecção (Hardware)**: Um dispositivo vestível em formato de pulseira, contendo, no mínimo, sensores para medição de Frequência Cardíaca (HR), Variabilidade da Frequência Cardíaca (HRV), Atividade Eletrodérmica (EDA/GSR) e Temperatura da Pele (ST)[cite: 1].
2.  **Módulo de Processamento (Software/IA)**: Os dados brutos do wearable serão processados em um pipeline:
    * **a. Extração de Características**: Extração de características estatísticas e de domínio de tempo/frequência dos sinais fisiológicos.
    * **b. [cite_start]Redução de Dimensionalidade com Análise Fatorial**: As características extraídas serão submetidas à Análise Fatorial para identificar componentes latentes e reduzir a dimensionalidade, visando melhorar a performance da classificação[cite: 3].
    * **c. [cite_start]Classificação Personalizada**: Os fatores resultantes alimentarão um modelo de Machine Learning (e.g., SVM ou Regressão Logística [cite: 3][cite_start]) que será treinado para aprender os padrões fisiológicos basais de cada usuário, em linha com a necessidade de alta personalização[cite: 2].
3.  **Módulo de Ação (Intervenção)**: Ao detectar um risco elevado, o sistema acionará ações de suporte:
    * **Alerta ao Cuidador**: Notificação detalhada enviada ao smartphone do cuidador.
    * **Intervenção Ambiental**: Comunicação com dispositivos de casa inteligente (IoT) para modular o ambiente (luz, som).
    * **Feedback ao Usuário**: Emissão de um sinal discreto (vibração, luz) para o próprio usuário.
