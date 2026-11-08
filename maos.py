from pathlib import Path
import time
import cv2
import mediapipe as mp

class DetectorMaos:
    def __init__(self):
        caminho_modelo = (
            Path(__file__).resolve().parent
            / "models"
            / "hand_landmarker.task"
        )

        if not caminho_modelo.exists():
            raise FileNotFoundError(
                f"Modelo não encontrado: {caminho_modelo}"
            )

        opcoes = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(caminho_modelo)
            ),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.detector = (
            mp.tasks.vision.HandLandmarker
            .create_from_options(opcoes)
        )

        self.inicio = time.monotonic()
        self.ultimo_timestamp = -1

    def detectar(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        imagem = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp = int(
            (time.monotonic() - self.inicio) * 1000
        )

        timestamp = max(
            timestamp,
            self.ultimo_timestamp + 1
        )
        self.ultimo_timestamp = timestamp

        resultado = self.detector.detect_for_video(
            imagem,
            timestamp
        )

        return resultado.hand_landmarks

    def fechar(self):
        self.detector.close()
