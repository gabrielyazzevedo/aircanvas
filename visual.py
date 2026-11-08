import cv2

CONEXOES = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17),
    (17, 18), (18, 19), (19, 20)
]


def desenhar_mao(frame, landmarks):
    altura, largura = frame.shape[:2]

    pontos = []

    for ponto in landmarks:
        x = int(ponto.x * largura)
        y = int(ponto.y * altura)
        pontos.append((x, y))

    # Desenha as conexões da mão
    for inicio, fim in CONEXOES:
        cv2.line(
            frame,
            pontos[inicio],
            pontos[fim],
            (0, 255, 0),
            2
        )

    # Desenha os 21 pontos
    for indice, (x, y) in enumerate(pontos):
        cor = (0, 0, 255) if indice == 8 else (255, 255, 0)

        cv2.circle(
            frame,
            (x, y),
            5,
            cor,
            -1
        )

    # Destaca o indicador
    cv2.circle(
        frame,
        pontos[8],
        12,
        (255, 0, 255),
        2
    )

    return frame
