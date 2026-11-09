# AirCanvas — Desenho Interativo com Gestos das Mãos

**Projeto acadêmico — C2 | Visão Computacional**

O **AirCanvas** é uma aplicação de visão computacional que permite desenhar no ar usando os movimentos da mão capturados por uma webcam. O sistema identifica pontos de referência (*landmarks*) da mão, interpreta gestos e transforma a posição do dedo indicador em traços exibidos sobre a imagem da câmera em tempo real.

A proposta desta etapa é demonstrar a integração entre captura de vídeo, reconhecimento de gestos, controle de estados e feedback visual. Recursos adicionais, como barra de ferramentas interativa, borracha, desfazer e exportação de imagens, ficam como possibilidades de evolução para a C3.

## 1. Tecnologias utilizadas

| Tecnologia | Utilização no projeto |
| --- | --- |
| **Python 3.11** | Linguagem principal, responsável pela lógica da aplicação e integração dos módulos. |
| **OpenCV (`opencv-python`)** | Captura de vídeo da webcam, espelhamento dos frames, desenho de linhas, exibição dos indicadores e composição do canvas com a imagem da câmera. |
| **MediaPipe Tasks API (`mediapipe`)** | Detecção e rastreamento da mão por meio do modelo **Hand Landmarker**, que fornece 21 landmarks por mão detectada. |
| **NumPy (`numpy`)** | Criação e manipulação da matriz de pixels usada como canvas persistente. |
| **Biblioteca padrão do Python (`math`, `time`, `pathlib`)** | Cálculo de distâncias, medição do tempo dos gestos e localização do arquivo do modelo. |

O projeto utiliza a **MediaPipe Tasks API**, com o arquivo `models/hand_landmarker.task`, e não a interface antiga `mp.solutions.hands`.

## 2. Organização do projeto

```text
aircanvas/
├── main.py
├── maos.py
├── gestos.py
├── desenho.py
├── visual.py
├── models/
│   └── hand_landmarker.task
├── requirements.txt
├── .gitignore
└── README.md
```

**Responsabilidade dos módulos:**

- `main.py`: inicia a webcam e coordena o ciclo de captura, detecção, interpretação dos gestos, desenho e exibição.
- `maos.py`: carrega o modelo Hand Landmarker e executa a detecção em cada frame, utilizando o modo de vídeo da MediaPipe Tasks API.
- `gestos.py`: calcula distâncias entre landmarks, reconhece a pinça e identifica os gestos de troca de cor e limpeza.
- `desenho.py`: mantém o canvas, desenha os traços, alterna as cores, interrompe o pincel e limpa a tela.
- `visual.py`: desenha os pontos e as conexões da mão detectada.
- `models/hand_landmarker.task`: modelo utilizado pela MediaPipe para estimar os landmarks.
- `requirements.txt`: dependências necessárias para executar a aplicação.

A separação em módulos facilita a manutenção e permite testar ou ajustar o reconhecimento de gestos sem modificar toda a lógica de desenho.

## 3. Como utilizar: gestos disponíveis

Posicione uma mão diante da webcam, com iluminação adequada e os dedos visíveis. A imagem é espelhada para facilitar a interação.

### Gesto 1 — Pinça: desenhar

1. Aproxime a ponta do **polegar** da ponta do **indicador**, formando uma pinça.
2. Mantenha a pinça fechada e movimente a mão: a ponta do indicador controla o pincel virtual.
3. Afaste o polegar do indicador para desligar o pincel e interromper o traço.
4. Faça outra pinça para iniciar um novo traço, sem apagar os anteriores.

**Landmarks utilizados:** ponta do polegar (`4`) e ponta do indicador (`8`). A distância entre eles é normalizada em relação à largura da palma, estimada pelos landmarks `5` e `17`.

### Gesto 2 — Dois dedos: trocar a cor

1. Solte a pinça.
2. Levante **indicador e médio**, mantendo anelar e mindinho abaixados.
3. Sustente o gesto por aproximadamente **0,6 segundo**.
4. A cor do pincel avança para a próxima opção.
5. Desfaça o gesto antes de repeti-lo para mudar novamente de cor.

**Cores disponíveis:** ciano, verde, vermelho e amarelo. Os traços já desenhados permanecem com suas cores originais.

### Gesto 3 — Três dedos: limpar a tela

1. Solte a pinça.
2. Levante **indicador, médio e anelar**, mantendo polegar e mindinho dobrados.
3. Sustente o gesto por aproximadamente **1,5 segundo**.
4. O canvas é limpo e o contador de traços é reiniciado.
5. Desfaça o gesto antes de realizar outra limpeza.

O gesto de três dedos foi escolhido no lugar da mão totalmente aberta para reduzir a possibilidade de apagar o desenho durante movimentos comuns.

### Quando a mão sai da câmera

O desenho é interrompido imediatamente enquanto não há mão detectada. Uma perda muito breve de rastreamento não reinicia automaticamente o estado lógico da pinça; se a ausência persistir, o reconhecimento do gesto é reiniciado. Os desenhos já realizados continuam visíveis.

### Encerrar a aplicação

Pressione **Q** na janela do AirCanvas.

## 4. Como o reconhecimento foi implementado

O processamento acontece continuamente, frame a frame:

1. O **OpenCV** captura uma imagem da webcam e a espelha horizontalmente.
2. O frame é convertido de BGR para RGB e encaminhado ao **Hand Landmarker** da MediaPipe Tasks API.
3. O modelo retorna até uma mão, representada por **21 landmarks** com coordenadas normalizadas.
4. O módulo `gestos.py` interpreta essas coordenadas para identificar pinça, dois dedos ou três dedos.
5. O módulo `desenho.py` converte a posição do indicador para coordenadas de pixels e desenha em um canvas NumPy independente do frame atual.
6. O canvas é combinado à imagem da câmera. Os landmarks e indicadores de estado são apresentados na janela.

### Reconhecimento da pinça

Para reduzir a influência da distância entre a mão e a câmera, a separação entre polegar e indicador é dividida por uma medida da largura da palma. O resultado é uma distância **relativa**.

O sistema utiliza **histerese**, com limites diferentes para ligar e desligar o pincel:

- **Ativação:** distância relativa menor ou igual a `0.35`.
- **Desativação:** distância relativa maior ou igual a `0.60`.

Enquanto a distância permanece entre esses dois valores, o estado anterior é preservado. Isso reduz oscilações causadas por pequenas variações na estimativa dos landmarks, sem impor um atraso artificial à abertura da pinça.

### Persistência dos traços

O desenho é armazenado em uma matriz NumPy separada da imagem da webcam. A cada frame, essa matriz é sobreposta à imagem atual. Dessa forma, o desenho não desaparece quando a câmera recebe um novo frame.

Para evitar linhas indevidas causadas por saltos repentinos do rastreamento, o módulo de desenho também verifica a distância entre a posição atual e a posição anterior do indicador, utilizando um limite inicial de **45 pixels**.

## 5. Testes realizados e ajustes durante o desenvolvimento

O AirCanvas foi desenvolvido e validado de forma incremental, com testes manuais usando a webcam e observação do comportamento dos gestos em tempo real.

| Teste | Objetivo | Resultado e ajuste |
| --- | --- | --- |
| Detecção da mão | Verificar se os 21 landmarks acompanham os movimentos. | Rastreamento visual implementado com MediaPipe Tasks API. |
| Desenho com o indicador | Verificar se o pincel acompanha o dedo e mantém os traços. | Canvas persistente implementado com NumPy e OpenCV. |
| Abertura e fechamento da pinça | Confirmar ativação e desativação do pincel. | Foram identificadas alternâncias inesperadas entre ligado e desligado. |
| Movimento com a pinça fechada | Verificar estabilidade durante deslocamentos da mão. | Foram feitos ajustes nos limiares e na lógica de reconhecimento. |
| Aproximação do dedo médio | Investigar interrupções inesperadas do desenho. | Foi removida uma regra que desligava o pincel quando o indicador e o médio se aproximavam. |
| Perda momentânea da mão | Observar o comportamento quando a detecção falha por poucos frames. | Foi adicionada tolerância de 150 ms para preservar o estado lógico do gesto, mantendo o desenho interrompido enquanto não há detecção. |
| Troca de cores | Verificar o gesto de dois dedos e a alternância das quatro cores. | Reconhecimento por permanência de 0,6 s implementado e testado. |
| Limpeza do canvas | Verificar o gesto de limpeza sem apagamentos involuntários. | O gesto de mão aberta foi substituído pelo número três, mantido por 1,5 s. |

### Problema principal: pincel alternando entre ligado e desligado

Durante os primeiros testes, o pincel apresentava oscilações mesmo quando o polegar e o indicador permaneciam encostados. Em alguns movimentos, o sistema desligava e religava o pincel, interrompendo o desenho.

**Primeira tentativa:** foram introduzidos suavização da distância e um atraso de aproximadamente 250 ms antes de desligar o pincel. Essa abordagem reduzia algumas mudanças rápidas, mas trouxe outro problema: quando a pinça era aberta intencionalmente, o pincel continuava desenhando por um curto período.

**Segunda tentativa:** foi acrescentada uma condição para desativar o pincel quando o indicador estivesse próximo do dedo médio. Nos testes, essa condição também se mostrou inadequada: aproximar os dedos podia desligar o pincel mesmo com a pinça ainda fechada.

**Solução adotada:** removemos o atraso de desativação e a regra de proximidade do dedo médio. Mantivemos a histerese entre os limites `0.35` e `0.60` e adicionamos uma tolerância curta para perdas momentâneas de rastreamento. O desenho continua sendo interrompido imediatamente quando a mão não é detectada.

Depois dessas alterações, os testes manuais apresentaram melhora de estabilidade e permitiram continuar com a implementação dos gestos de cor e limpeza. Como o reconhecimento depende da iluminação, da posição da mão e da webcam, não se trata de uma garantia de funcionamento perfeito em qualquer ambiente.

## 6. Instalação e execução no computador do professor

### Pré-requisitos

- **Python 3.11** instalado.
- Computador com **webcam** integrada ou USB.
- Permissão do sistema operacional para acessar a câmera.
- Conexão com a internet para instalar as dependências (e, se necessário, baixar o modelo).

O projeto foi desenvolvido em **Ubuntu**, mas pode ser executado em Windows ou macOS desde que as dependências e o acesso à webcam estejam disponíveis.

### Passo 1 — Obter o projeto

Baixe o repositório como ZIP e extraia os arquivos ou clone o repositório com Git. Abra um terminal na pasta `aircanvas`, onde está o arquivo `main.py`.

### Passo 2 — Criar um ambiente virtual

**Linux/macOS:**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, é possível executar diretamente o Python do ambiente virtual em vez de ativá-lo.

### Passo 3 — Instalar as dependências

Com o ambiente virtual ativo:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

O arquivo `requirements.txt` deve acompanhar o projeto e conter as dependências efetivamente utilizadas, incluindo `mediapipe`, `opencv-python` e `numpy`.

### Passo 4 — Conferir o modelo MediaPipe

Verifique se o arquivo abaixo existe:

```text
models/hand_landmarker.task
```

Se o modelo não estiver incluído no repositório ou no ZIP, crie a pasta `models` e baixe-o pelo terminal na raiz do projeto:

**Linux/macOS:**

```bash
mkdir -p models
curl -L --fail -o models/hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

**Windows (PowerShell):**

```powershell
New-Item -ItemType Directory -Force models
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -OutFile "models/hand_landmarker.task"
```

O caminho do modelo é resolvido relativamente ao arquivo do projeto, evitando dependência de um caminho absoluto específico do computador de desenvolvimento.

### Passo 5 — Executar

Na raiz do projeto, com o ambiente virtual ativo:

```bash
python main.py
```

Uma janela chamada **AirCanvas** deverá abrir com a imagem da webcam. Teste os três gestos descritos na seção 3 e pressione **Q** para encerrar.

### Solução de problemas comuns

- **Webcam não encontrada:** verifique a conexão da câmera, as permissões do sistema e se outro aplicativo está utilizando o dispositivo. O código usa `cv2.VideoCapture(0)`, que pode precisar de ajuste caso a câmera utilize outro índice.
- **`ModuleNotFoundError`:** confirme que o ambiente virtual está ativo e execute novamente `python -m pip install -r requirements.txt`.
- **Modelo não encontrado:** confirme que `models/hand_landmarker.task` existe na estrutura indicada.
- **Reconhecimento instável:** melhore a iluminação, mantenha a mão visível e evite sobreposição excessiva dos dedos.

## 7. Demonstração em vídeo

O vídeo de demonstração apresenta a execução do AirCanvas e as funcionalidades implementadas para a C2: detecção da mão, desenho com pinça, troca de cores, limpeza por gesto e comportamento quando a mão sai do campo de visão.

**Vídeo no YouTube:** [Assistir à demonstração do AirCanvas](https://youtu.be/RjjxEcW6hNY?is=8vj46hK0VfBi2bNV)

## 8. Possíveis evoluções para a C3

As seguintes funcionalidades foram planejadas como melhorias futuras, **não fazem parte da implementação atual da C2**:

- Barra de ferramentas visual e interativa.
- Borracha virtual.
- Desfazer o último traço (*undo*).
- Exportar o desenho para um arquivo de imagem.
- Aprimoramentos de interface, calibração e feedback dos gestos.

## 9. Considerações finais

O AirCanvas demonstra a aplicação prática de visão computacional em uma interface controlada por gestos. A solução combina estimativa de landmarks, regras geométricas, controle de estados ao longo do tempo e renderização de elementos gráficos em tempo real.

Os testes foram importantes não apenas para validar as funcionalidades, mas também para identificar limitações de uma abordagem baseada em distâncias entre pontos da mão. As correções realizadas no reconhecimento da pinça ilustram a importância de ajustar o comportamento da aplicação com base em observações práticas de uso.
