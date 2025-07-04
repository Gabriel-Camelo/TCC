# TCC - PROPOSTA DE SISTEMA VESTÍVEL COM INTELIGÊNCIA ARTIFICIAL PARA SUPORTE A INDIVÍDUOS COM TRANSTORNO DO ESPECTRO AUTISTA

**Autor:** [Gabriel Camelo]
**Orientador:** [Almir Moura]

---

#### **1. Introdução**

O avanço das tecnologias de Informação e Comunicação (TIC) e a ampla adoção de dispositivos eletrônicos de consumo, como pulseiras e relógios inteligentes, apresentam uma oportunidade sem precedentes para o monitoramento da saúde e do bem-estar do usuário em seu cotidiano. A capacidade de obter feedback em tempo real sobre mudanças fisiológicas, monitorar o estresse e até detectar emoções está se tornando uma realidade tecnológica. Tal capacidade é particularmente valiosa para populações que vivenciam estados emocionais que mudam rapidamente, como é o caso de pessoas com Transtorno do Espectro Autista (TEA).

Indivíduos com TEA frequentemente enfrentam desafios significativos na comunicação e no gerenciamento da desregulação emocional, o que pode levar a uma redução na qualidade de vida. A ansiedade, em particular, é uma comorbidade psiquiátrica prevalente, com taxas que variam de 11% a 84% nesta população. Essa ansiedade pode intensificar dificuldades de interação social e magnificar a irritabilidade e a agressão. Para muitos, especialmente aqueles com maiores necessidades de suporte e com dificuldade em identificar e descrever seus próprios estados emocionais (uma condição associada conhecida como Alexitimia), a comunicação do sofrimento torna-se uma barreira expressiva.

Neste contexto, o presente trabalho propõe a concepção de um sistema de tecnologia assistiva vestível (wearable) para indivíduos com TEA, com foco naqueles que necessitam de maior nível de suporte. O sistema integra sensores fisiológicos e Inteligência Artificial (IA) com o objetivo de detectar precocemente os sinais de desregulação emocional, como a sobrecarga sensorial e o estresse agudo, que frequentemente precedem crises comportamentais. Ao identificar esses padrões, o sistema visa fornecer um suporte proativo, tanto alertando cuidadores quanto possibilitando intervenções ambientais automatizadas, buscando, em última instância, melhorar o bem-estar e a qualidade de vida do usuário.

#### **2. Fundamentação Teórica**

##### **2.1 Transtorno do Espectro Autista e a Necessidade de Suporte Emocional**

O Transtorno do Espectro Autista (TEA) é uma condição do neurodesenvolvimento caracterizada por déficits na interação social recíproca e nas habilidades de comunicação, acompanhada por comportamentos restritivos e repetitivos. Uma das comorbidades mais significativas é a ansiedade, que pode agravar os comportamentos ritualizados e os desafios sociais. A dificuldade em gerenciar o estresse e a ansiedade pode culminar em comportamentos desafiadores, que representam uma barreira para a participação social e afetam profundamente o bem-estar do indivíduo e de sua família.

A necessidade de uma ferramenta de monitoramento objetivo é reforçada pela dificuldade que muitos indivíduos com TEA têm em comunicar seu estado de sofrimento. Tecnologias vestíveis surgem, assim, como uma solução potencial que pode complementar as intervenções comportamentais existentes, oferecendo aos cuidadores uma janela para as mudanças emocionais internas do indivíduo em tempo real.

##### **2.2 Respostas Fisiológicas e Biomarcadores de Estresse no TEA**

A detecção de estados emocionais como o estresse pode ser realizada através do monitoramento de sinais fisiológicos (biomarcadores). O artigo de revisão de Taj-Eldin et al. (2018) aponta os seguintes como sendo os mais relevantes:
* **Frequência Cardíaca (HR) e Variabilidade da Frequência Cardíaca (HRV)**: Medem a atividade cardiovascular e suas alterações. A HRV, em particular, fornece informações valiosas sobre o processo de regulação emocional.
* **Atividade Eletrodérmica (EDA ou GSR)**: Mede a condutância da pele, que está ligada à ativação emocional e tem se mostrado um indicador útil de estresse.
* **Temperatura da Pele (ST)**: A temperatura periférica também pode ser um parâmetro fisiológico útil na avaliação do estresse.
* **Taxa de Respiração (RR)**: Alterações no ritmo respiratório também são um indicador de estresse.

É crucial notar que pessoas com TEA podem exibir padrões de resposta fisiológica diferentes dos seus pares neurotípicos. Estudos mostraram, por exemplo, que adultos com TEA podem apresentar uma diminuição da frequência cardíaca em resposta a estressores psicossociais. Essa variabilidade justifica a necessidade de sistemas que não apenas meçam, mas que também aprendam os padrões individuais de cada usuário. Com base em consulta com clínicos, o artigo de referência sugere que os parâmetros-chave para qualquer dispositivo com esta finalidade são, no mínimo, a **frequência cardíaca (HR) e a atividade eletrodérmica (EDA)**.

##### **2.3 Tecnologias Assistivas Vestíveis: Cenário Atual**

A revisão da literatura indica que o mercado de wearables para monitoramento fisiológico é abundante, porém, a grande maioria dos dispositivos (88%) é projetada para a população geral, com pouca atenção sendo dada às necessidades específicas de pessoas com TEA.
* **Dispositivos Comerciais**: Existem dispositivos robustos como a pulseira Empatica E4, que coleta múltiplos dados fisiológicos (HR, EDA, ST, aceleração) e é considerada adequada para uso em pesquisas com TEA. Sua sucessora, a Embrace, possui aprovação da FDA. No entanto, muitos dispositivos no mercado carecem de validação clínica contra um padrão-ouro.
* **Protótipos de Pesquisa**: A academia tem explorado formatos alternativos e menos estigmatizantes, como luvas e lenços inteligentes, que incorporam sensores de forma discreta.
* **Soluções Emergentes**: Soluções como o "Reveal" da Awake Labs estão sendo desenvolvidas especificamente para monitorar a ansiedade em TEA, utilizando algoritmos próprios para alertar cuidadores.

Esta análise revela uma lacuna no mercado e na pesquisa: a necessidade de sistemas integrados que não apenas detectem, mas que também ofereçam uma ação de suporte, e que sejam projetados com base nas preferências e sensibilidades do público com TEA.

##### **2.4 Fatores de Usabilidade e Design para a População com TEA**

Para que uma tecnologia assistiva seja adotada por indivíduos com TEA, o design e a usabilidade são fatores críticos. Pesquisas com usuários e seus pais revelam que:
* O **conforto** do dispositivo é frequentemente o fator mais importante.
* Há uma preferência por dispositivos feitos de materiais **flexíveis e macios**.
* O design deve ser **discreto** e assemelhar-se a produtos de consumo geral para evitar estigma.
* Formatos como **pulseiras e relógios** são os preferidos, enquanto dispositivos obstrusivos como cintas peitorais são os menos adequados.

#### **3. Proposta do Sistema**

##### **3.1 Objetivo Geral**

Propor a arquitetura de um sistema vestível integrado com Inteligência Artificial, projetado para monitorar sinais fisiológicos, detectar padrões precursores de crises de desregulação emocional em indivíduos com TEA de alto nível de suporte e acionar um mecanismo de suporte proativo.

##### **3.2 Objetivos Específicos**

* Definir os biomarcadores fisiológicos mais relevantes para a detecção de estresse e ansiedade no público-alvo, com base na literatura.
* Especificar a arquitetura de hardware do dispositivo vestível, incluindo os sensores mínimos necessários (HR e EDA).
* Descrever a arquitetura de software, detalhando o papel do modelo de Inteligência Artificial (Machine Learning) na análise de dados e personalização.
* Propor um mecanismo de intervenção em "ciclo fechado" (closed-loop), detalhando as ações de suporte possíveis (alerta ao cuidador, integração com automação residencial).
* Discutir os fatores de usabilidade e as considerações éticas (privacidade, consentimento) inerentes ao projeto.

##### **3.3 Arquitetura do Sistema**

O sistema proposto será composto por três módulos principais:
1.  **Módulo de Detecção (Hardware)**: Um dispositivo vestível em formato de pulseira, construído com materiais flexíveis e hipoalergênicos. O dispositivo conterá, no mínimo, um sensor de fotopletismografia (PPG) para medição de Frequência Cardíaca (HR) e Variabilidade da Frequência Cardíaca (HRV), e sensores para medir a Atividade Eletrodérmica (EDA/GSR) e a Temperatura da Pele (ST).
2.  **Módulo de Processamento (Software/IA)**: Os dados brutos coletados pelo wearable serão transmitidos via Bluetooth Low Energy (BLE) para um aplicativo em um smartphone. Neste aplicativo, um modelo de Machine Learning será treinado para aprender os padrões fisiológicos basais de cada usuário. O modelo será capaz de identificar desvios significativos que indiquem o aumento de estresse ou sobrecarga sensorial, gerando um "índice de risco de crise" em tempo real.
3.  **Módulo de Ação (Intervenção)**: Ao detectar um índice de risco elevado, o sistema acionará uma ou mais ações de suporte:
    * **Alerta ao Cuidador**: Uma notificação detalhada será enviada ao smartphone do cuidador, informando sobre o estado do usuário e o risco detectado.
    * **Intervenção Ambiental**: O sistema poderá se comunicar com dispositivos de casa inteligente (IoT) para, por exemplo, diminuir a intensidade das luzes, reduzir o volume de sons ambientes ou tocar uma música calmante.
    * **Feedback ao Usuário**: Para usuários que possam se beneficiar, o próprio dispositivo poderá emitir um sinal discreto (uma vibração suave, uma luz de cor específica) como um lembrete para utilizar uma técnica de autorregulação.
