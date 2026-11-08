import cv2
import numpy as np
import math

class PincelVirtual:
    def __init__(self):
        self.canvas = None
        self.posicao_anterior = None

        self.cores = [
    ("Ciano", (255, 255, 0)),
    ("Verde", (0, 255, 0)),
    ("Vermelho", (0, 0, 255)),
    ("Amarelo", (0, 255, 255))
]

        self.indice_cor = 0
        self.nome_cor, self.cor = self.cores[self.indice_cor]
        self.espessura = 5

        self.total_tracos = 0
        self.desenhando = False

    def preparar_canvas(self, frame):
        altura, largura = frame.shape[:2]

        if self.canvas is None:
            self.canvas = np.zeros(
                (altura, largura, 3),
                dtype=np.uint8
            )

    def desenhar(self, frame, landmarks):
        self.preparar_canvas(frame)

        altura, largura = frame.shape[:2]

        # Landmark 8: ponta do indicador
        indicador = landmarks[8]

        x = int(indicador.x * largura)
        y = int(indicador.y * altura)

        # Mantém coordenadas dentro da imagem
        x = max(0, min(x, largura - 1))
        y = max(0, min(y, altura - 1))

        posicao_atual = (x, y)

        # Distância máxima entre frames
        distancia_maxima = 45

        if self.posicao_anterior is None:
            self.total_tracos += 1

        else:
            distancia = math.hypot(
                x - self.posicao_anterior[0],
                y - self.posicao_anterior[1]
            )

            if distancia <= distancia_maxima:
                cv2.line(
                    self.canvas,
                    self.posicao_anterior,
                    posicao_atual,
                    self.cor,
                    self.espessura,
                    cv2.LINE_AA
                )
            else:
                # Evita linhas causadas por saltos
                self.total_tracos += 1

        self.posicao_anterior = posicao_atual
        self.desenhando = True

        return posicao_atual

    def parar(self):
        # Interrompe o traço atual
        self.posicao_anterior = None
        self.desenhando = False
        
    def limpar(self):
        if self.canvas is not None:
            self.canvas.fill(0)

        self.parar()
        self.total_tracos = 0

    def trocar_cor(self):
        self.indice_cor = (
            self.indice_cor + 1
        ) % len(self.cores)

        self.nome_cor, self.cor = self.cores[self.indice_cor]

        # Evita conectar traços de cores diferentes
        self.parar()

    def combinar(self, frame):
        if self.canvas is None:
            return frame

        # Identifica os pixels desenhados
        mascara = cv2.cvtColor(
            self.canvas,
            cv2.COLOR_BGR2GRAY
        )

        _, mascara = cv2.threshold(
            mascara,
            1,
            255,
            cv2.THRESH_BINARY
        )

        resultado = frame.copy()

        resultado[mascara > 0] = (
            self.canvas[mascara > 0]
        )

        return resultado
