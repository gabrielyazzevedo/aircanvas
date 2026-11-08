import cv2
import time
from maos import DetectorMaos
from desenho import PincelVirtual
from gestos import ReconhecedorGestos
from visual import desenhar_mao

def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Erro: webcam não encontrada.")
        return

    detector = None
    pincel = PincelVirtual()
    gestos = ReconhecedorGestos()

    # Controle de perda temporária da mão
    ultimo_instante_mao = None
    tolerancia_perda = 0.15

    try:
        detector = DetectorMaos()

        print("AirCanvas iniciado!")
        print("Faca uma pinca para desenhar.")
        print("Pressione Q para sair.")

        while True:
            sucesso, frame = camera.read()

            if not sucesso:
                print("Erro ao capturar imagem.")
                break

            # Espelha a imagem
            frame = cv2.flip(frame, 1)

            altura, largura = frame.shape[:2]

            # Detecta a mão usando MediaPipe
            maos = detector.detectar(frame)

            
            if maos:
                ultimo_instante_mao = time.monotonic()
                landmarks = maos[0]

                # Reconhece a pinça
                pinca = gestos.detectar_pinca(
                    landmarks,
                    largura,
                    altura
                )

                # Reconhece o gesto de troca de cor
                if gestos.detectar_troca_cor(landmarks):
                    pincel.trocar_cor()
                    print(
                        f"Cor alterada para: {pincel.nome_cor}"
                    )
                # Reconhece a mão aberta para limpar
                if gestos.detectar_limpeza(landmarks):
                    pincel.limpar()
                    print("Canvas limpo!")

                if pinca:
                    pincel.desenhar(frame, landmarks)

                    status = "PINCEL ATIVO"
                    cor_status = (0, 255, 0)

                else:
                    pincel.parar()

                    status = "PINCEL DESLIGADO"
                    cor_status = (0, 255, 255)

            else:
                # Interrompe o desenho sem a mão
                pincel.parar()

                agora = time.monotonic()

                if (
                    ultimo_instante_mao is None
                    or agora - ultimo_instante_mao > tolerancia_perda
                ):
                    gestos.resetar()

                status = "MAO NAO DETECTADA"
                cor_status = (0, 0, 255)


            # Combina os desenhos com a webcam
            frame = pincel.combinar(frame)

            # Desenha os landmarks sobre a imagem
            if maos:
                frame = desenhar_mao(
                    frame,
                    landmarks
                )

            # Exibe o estado atual do pincel
            cv2.putText(
                frame,
                status,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                cor_status,
                2
            )

            # Exibe a quantidade de traços
            cv2.putText(
                frame,
                f"Tracos: {pincel.total_tracos}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            # Exibe a distancia normalizada da pinça
            cv2.putText(
                frame,
                f"Distancia pinca: {gestos.distancia_pinca:.2f}",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            cv2.putText(
                frame,
                f"Cor: {pincel.nome_cor}",
                (20, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                pincel.cor,
                2
)
            cv2.imshow("AirCanvas", frame)

            # Pressione Q para sair
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()

        if detector is not None:
            detector.fechar()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
