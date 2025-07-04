# TCC - PROPOSTA DE SISTEMA VESTÍVEL COM INTELIGÊNCIA ARTIFICIAL PARA SUPORTE A INDIVÍDUOS COM TRANSTORNO DO ESPECTRO AUTISTA

**Autor:** [Gabriel Camelo]
**Orientador:** [Almir Moura]

---

#### **1. Introdução**

[cite_start]O avanço das tecnologias de Informação e Comunicação (TIC) e a ampla adoção de dispositivos eletrônicos de consumo, como pulseiras e relógios inteligentes, apresentam uma oportunidade sem precedentes para o monitoramento da saúde e do bem-estar do usuário em seu cotidiano[cite: 1]. [cite_start]A capacidade de obter feedback em tempo real sobre mudanças fisiológicas, monitorar o estresse e até detectar emoções está se tornando uma realidade tecnológica[cite: 1]. [cite_start]Sendo facilmente portáteis e discretos [cite: 2][cite_start], estes dispositivos podem seguir o usuário em suas atividades diárias de forma não intrusiva[cite: 2]. [cite_start]Tal capacidade é particularmente valiosa para populações que vivenciam estados emocionais que mudam rapidamente, como é o caso de pessoas com Transtorno do Espectro Autista (TEA)[cite: 1].

[cite_start]Indivíduos com TEA frequentemente enfrentam desafios significativos na comunicação e no gerenciamento da desregulação emocional, o que pode levar a uma redução na qualidade de vida[cite: 1]. [cite_start]A ansiedade, em particular, é uma comorbidade psiquiátrica prevalente, com taxas que variam de 11% a 84% nesta população[cite: 1]. [cite_start]Essa ansiedade pode intensificar dificuldades de interação social e magnificar a irritabilidade e a agressão[cite: 1]. [cite_start]Para muitos, especialmente aqueles com maiores necessidades de suporte e com dificuldade em identificar e descrever seus próprios estados emocionais (uma condição associada conhecida como Alexitimia) [cite: 1][cite_start], a comunicação do sofrimento torna-se uma barreira expressiva[cite: 1].

Neste contexto, o presente trabalho propõe a concepção de um sistema de tecnologia assistiva vestível (*wearable*) para indivíduos com TEA, com foco naqueles que necessitam de maior nível de suporte. [cite_start]O sistema integra sensores fisiológicos e Inteligência Artificial (IA), sendo que algoritmos de IA podem apoiar o processo de gerenciamento de estresse e ansiedade[cite: 2]. [cite_start]O objetivo é detectar precocemente os sinais de desregulação emocional que frequentemente precedem crises comportamentais[cite: 1]. [cite_start]A literatura aponta a necessidade de mais estudos que empreguem inteligência artificial e computação afetiva para apoiar tanto o diagnóstico quanto as intervenções terapêuticas[cite: 2]. [cite_start]Ao identificar esses padrões, o sistema visa fornecer um suporte proativo, tanto alertando cuidadores quanto possibilitando intervenções ambientais automatizadas, buscando, em última instância, melhorar o bem-estar e a qualidade de vida do usuário[cite: 1].

#### **2. Fundamentação Teórica**

##### **2.1 Transtorno do Espectro Autista e a Necessidade de Suporte Emocional**

[cite_start]O Transtorno do Espectro Autista (TEA) é uma deficiência do neurodesenvolvimento caracterizada principalmente por comprometimento no comportamento social e na comunicação[cite: 2, 791]. [cite_start]Uma das comorbidades mais significativas é a ansiedade, que pode agravar os comportamentos ritualizados e os desafios sociais[cite: 1]. [cite_start]A dificuldade em gerenciar o estresse e a ansiedade pode culminar em comportamentos desafiadores, que representam uma barreira para a participação social e afetam profundamente o bem-estar do indivíduo e de sua família[cite: 1, 2].

[cite_start]A necessidade de uma ferramenta de monitoramento objetivo é reforçada pela dificuldade que muitos indivíduos com TEA têm em comunicar seu estado de sofrimento[cite: 1]. [cite_start]Tecnologias vestíveis surgem, assim, como uma solução potencial que pode complementar as intervenções comportamentais existentes [cite: 1][cite_start], oferecendo aos cuidadores uma janela para os estados internos dos indivíduos que são incapazes de comunicar seus sentimentos[cite: 2].

##### **2.2 Respostas Fisiológicas e Biomarcadores de Estresse no TEA**

[cite_start]A detecção de estados emocionais como o estresse pode ser realizada através do monitoramento de sinais fisiológicos[cite: 1]. [cite_start]Sensores vestíveis são capazes de medir diversas variáveis, como frequência cardíaca (HR), eletromiograma (EMG), eletrocardiograma (ECG), atividade eletrodérmica (EDA), temperatura corporal, saturação de oxigênio (SpO2) e taxa de respiração (RR)[cite: 2]. Os biomarcadores mais relevantes para o monitoramento de estresse, apontados pela literatura, incluem:
* **Frequência Cardíaca (HR) e Variabilidade da Frequência Cardíaca (HRV)**: Medem a atividade cardiovascular e suas alterações. [cite_start]A HRV, em particular, fornece informações valiosas sobre o processo de regulação emocional[cite: 1].
* [cite_start]**Atividade Eletrodérmica (EDA ou GSR)**: Mede a condutância da pele, que está ligada à ativação emocional e tem se mostrado um indicador útil de estresse[cite: 1]. [cite_start]A EDA, junto com a temperatura da pele e a frequência cardíaca, são usadas para medir os níveis de estresse, um sintoma comum em pessoas com TEA[cite: 2].
* [cite_start]**Temperatura da Pele (ST)** e **Taxa de Respiração (RR)**[cite: 1].

[cite_start]É crucial notar que pessoas com TEA podem exibir padrões de resposta fisiológica diferentes dos seus pares neurotípicos[cite: 1]. [cite_start]Essa variabilidade justifica a necessidade de sistemas que não apenas meçam, mas que também aprendam os padrões individuais de cada usuário, demandando soluções altamente personalizáveis[cite: 2]. Com base em consulta com clínicos, o artigo de Taj-Eldin et al. [cite_start](2018) sugere que os parâmetros-chave para qualquer dispositivo com esta finalidade são, no mínimo, a **frequência cardíaca (HR) e a atividade eletrodérmica (EDA)**[cite: 1].

##### **2.3 Tecnologias Assistivas Vestíveis e Inteligência Artificial**

[cite_start]A revisão da literatura indica que o mercado de wearables para monitoramento fisiológico é abundante, porém, a maioria dos dispositivos (88%) é projetada para a população geral, com pouca atenção sendo dada às necessidades específicas de pessoas com TEA[cite: 1]. [cite_start]As pesquisas existentes podem ser categorizadas em três finalidades principais: treinamento (53%), monitoramento (30,8%) e suporte (15,4%)[cite: 2].

Um ponto fundamental para este projeto é o uso de Inteligência Artificial. [cite_start]Embora a Computação Afetiva ocupe uma posição proeminente (20,8%) nas pesquisas [cite: 2][cite_start], a **Inteligência Artificial (IA), por outro lado, foi implementada em apenas dois dos estudos revisados por Koumpouros & Kafazis (2019), principalmente para detectar comportamentos estereotipados**[cite: 2]. Isso revela uma lacuna significativa e uma oportunidade para trabalhos que explorem IA de forma mais robusta para predição de crises. [cite_start]Acredita-se que a IA dominará o campo em um futuro próximo[cite: 2], tornando este projeto especialmente oportuno.

##### **2.4 Fatores de Usabilidade e Design para a População com TEA**

[cite_start]Para que uma tecnologia assistiva seja adotada por indivíduos com TEA, o design e a usabilidade são fatores críticos[cite: 2]. [cite_start]O conforto do dispositivo é frequentemente o fator mais importante[cite: 1]. [cite_start]Dispositivos devem ser feitos de materiais flexíveis e macios, uma vez que muitas crianças podem apresentar hipersensibilidade a roupas e outros materiais[cite: 2].

[cite_start]O design do dispositivo deve ser discreto e o mais similar possível a produtos de consumo geral para mitigar o risco de estigma associado[cite: 1]. [cite_start]Nesse sentido, **smartwatches e pulseiras parecem ser uma solução mais ideal para a população examinada do que outros sensores mais obstrusivos (por exemplo, adesivos, etc.)**[cite: 2].

##### **2.5 Desafios e Limitações na Pesquisa Atual**

[cite_start]A literatura aponta diversos desafios que dificultam o avanço da área e a transição das soluções da pesquisa para o mercado[cite: 2]. Os principais problemas identificados nos estudos existentes incluem:
* [cite_start]**Amostras pequenas**: A maioria dos estudos é conduzida com um número muito limitado de participantes (muitas vezes, menos de 11)[cite: 2].
* [cite_start]**Resultados não generalizáveis**: Devido ao tamanho das amostras e à falta de diversidade, os resultados dificilmente podem ser generalizados[cite: 2].
* [cite_start]**Falta de grupos de controle**: Pouquíssimos projetos incluem um grupo de controle em sua metodologia, o que fragiliza as conclusões sobre a eficácia da intervenção[cite: 2].
* [cite_start]**Subjetividade na avaliação**: A maioria dos estudos utiliza questionários customizados (86,2%) em vez de instrumentos validados para avaliar a eficácia e satisfação, questionando a confiabilidade dos resultados[cite: 2].
* [cite_start]**Considerações tecnológicas**: Problemas práticos como custo, tamanho, vida útil da bateria dos sensores e a dificuldade de uso por crianças são barreiras constantes[cite: 2].
* [cite_start]**Foco em ambientes controlados**: Há uma necessidade de que os esforços de pesquisa se concentrem em testar as aplicações em condições reais, e não apenas em ambientes controlados de laboratório[cite: 2].

#### **3. Proposta do Sistema**

##### **3.1 Objetivo Geral**

Propor a arquitetura de um sistema vestível integrado com Inteligência Artificial, projetado para monitorar sinais fisiológicos, detectar padrões precursores de crises de desregulação emocional em indivíduos com TEA de alto nível de suporte e acionar um mecanismo de suporte proativo. O projeto visa responder à necessidade de soluções altamente personalizáveis e que sejam testadas em cenários do mundo real.

##### **3.2 Objetivos Específicos**

* Definir os biomarcadores fisiológicos mais relevantes para a detecção de estresse e ansiedade no público-alvo, com base na literatura.
* Especificar a arquitetura de hardware do dispositivo vestível, incluindo os sensores mínimos necessários (HR e EDA) e considerando os fatores de usabilidade cruciais para a população com TEA.
* Descrever a arquitetura de software, detalhando o papel do modelo de Inteligência Artificial (Machine Learning) na análise de dados e personalização, preenchendo a lacuna de pesquisas que aplicam IA para predição de crises.
* Propor um mecanismo de intervenção em "ciclo fechado" (*closed-loop*), detalhando as ações de suporte possíveis (alerta ao cuidador, integração com automação residencial).
* Delinear um protocolo de validação que busque superar limitações de estudos anteriores, como o tamanho da amostra e a ausência de um grupo de controle.

##### **3.3 Arquitetura do Sistema**

O sistema proposto será composto por três módulos principais:
1.  **Módulo de Detecção (Hardware)**: Um dispositivo vestível em formato de pulseira, construído com materiais flexíveis e hipoalergênicos. O dispositivo conterá, no mínimo, um sensor de fotopletismografia (PPG) para medição de Frequência Cardíaca (HR) e Variabilidade da Frequência Cardíaca (HRV), e sensores para medir a Atividade Eletrodérmica (EDA/GSR) e a Temperatura da Pele (ST).
2.  **Módulo de Processamento (Software/IA)**: Os dados brutos coletados pelo wearable serão transmitidos via Bluetooth Low Energy (BLE) para um aplicativo em um smartphone. Neste aplicativo, um modelo de Machine Learning será treinado para aprender os padrões fisiológicos basais de cada usuário, em linha com a necessidade de alta personalização. O modelo será capaz de identificar desvios significativos que indiquem o aumento de estresse ou sobrecarga sensorial, gerando um "índice de risco de crise" em tempo real.
3.  **Módulo de Ação (Intervenção)**: Ao detectar um índice de risco elevado, o sistema acionará uma ou mais ações de suporte:
    * **Alerta ao Cuidador**: Uma notificação detalhada será enviada ao smartphone do cuidador, informando sobre o estado do usuário e o risco detectado.
    * **Intervenção Ambiental**: O sistema poderá se comunicar com dispositivos de casa inteligente (IoT) para, por exemplo, diminuir a intensidade das luzes, reduzir o volume de sons ambientes ou tocar uma música calmante.
    * **Feedback ao Usuário**: Para usuários que possam se beneficiar, o próprio dispositivo poderá emitir um sinal discreto (uma vibração suave, uma luz de cor específica) como um lembrete para utilizar uma técnica de autorregulação.
