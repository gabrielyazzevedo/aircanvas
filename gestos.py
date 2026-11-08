import math
import time

class ReconhecedorGestos:
    def __init__(self):
        self.pinca_ativa = False

        self.limite_ativar = 0.35
        self.limite_desativar = 0.60
        self.distancia_pinca = 0.0

        # Troca de cores
        self.inicio_gesto_cor = None
        self.gesto_cor_executado = False
        self.tempo_gesto_cor = 0.6

        # Limpeza
        self.inicio_gesto_limpar = None
        self.gesto_limpar_executado = False
        self.tempo_gesto_limpar = 1.5

    def distancia(self, p1, p2, largura, altura):
        return math.hypot(
            (p1.x - p2.x) * largura,
            (p1.y - p2.y) * altura
        )

    def detectar_pinca(self, landmarks, largura, altura):
        polegar = landmarks[4]
        indicador = landmarks[8]

        palma = self.distancia(
            landmarks[5],
            landmarks[17],
            largura,
            altura
        )

        if palma < 1:
            self.resetar()
            return False

        self.distancia_pinca = self.distancia(
            polegar,
            indicador,
            largura,
            altura
        ) / palma

        if self.pinca_ativa:
            if self.distancia_pinca >= self.limite_desativar:
                self.pinca_ativa = False
        else:
            if self.distancia_pinca <= self.limite_ativar:
                self.pinca_ativa = True

        return self.pinca_ativa

    def dedo_estendido(self, landmarks, ponta, base):
        pulso = landmarks[0]

        distancia_ponta = math.hypot(
            landmarks[ponta].x - pulso.x,
            landmarks[ponta].y - pulso.y
        )

        distancia_base = math.hypot(
            landmarks[base].x - pulso.x,
            landmarks[base].y - pulso.y
        )

        return distancia_ponta > distancia_base * 1.15

    def detectar_troca_cor(self, landmarks):
        indicador = self.dedo_estendido(
            landmarks, 8, 6
        )

        medio = self.dedo_estendido(
            landmarks, 12, 10
        )

        anelar = self.dedo_estendido(
            landmarks, 16, 14
        )

        mindinho = self.dedo_estendido(
            landmarks, 20, 18
        )

        gesto_valido = (
            indicador
            and medio
            and not anelar
            and not mindinho
            and not self.pinca_ativa
        )

        if not gesto_valido:
            self.inicio_gesto_cor = None
            self.gesto_cor_executado = False
            return False

        if self.gesto_cor_executado:
            return False

        agora = time.monotonic()

        if self.inicio_gesto_cor is None:
            self.inicio_gesto_cor = agora
            return False

        if agora - self.inicio_gesto_cor >= self.tempo_gesto_cor:
            self.gesto_cor_executado = True
            return True

        return False

    
    def detectar_limpeza(self, landmarks):
        # Verifica os dedos estendidos
        indicador = self.dedo_estendido(
            landmarks, 8, 6
        )

        medio = self.dedo_estendido(
            landmarks, 12, 10
        )

        anelar = self.dedo_estendido(
            landmarks, 16, 14
        )

        mindinho = self.dedo_estendido(
            landmarks, 20, 18
        )

        # Verifica se o polegar está dobrado usando a distância até a base do mindinho
        polegar = landmarks[4]
        base_mindinho = landmarks[17]

        distancia_polegar = math.hypot(
            polegar.x - base_mindinho.x,
            polegar.y - base_mindinho.y
        )

        largura_palma = math.hypot(
            landmarks[5].x - landmarks[17].x,
            landmarks[5].y - landmarks[17].y
        )

        polegar_dobrado = (
            largura_palma > 0.001
            and distancia_polegar / largura_palma < 1.2
        )

        # Indicar número 3: indicador, médio e anelar
        gesto_valido = (
            indicador
            and medio
            and anelar
            and not mindinho
            and polegar_dobrado
            and not self.pinca_ativa
        )

        if not gesto_valido:
            self.inicio_gesto_limpar = None
            self.gesto_limpar_executado = False
            return False

        # Impede apagar em sequencia
        if self.gesto_limpar_executado:
            return False

        agora = time.monotonic()

        if self.inicio_gesto_limpar is None:
            self.inicio_gesto_limpar = agora
            return False

        # Exige 1,5 segundo de gesto contínuo
        if (
            agora - self.inicio_gesto_limpar
            >= self.tempo_gesto_limpar
        ):
            self.gesto_limpar_executado = True
            return True

        return False


    def resetar(self):
        self.pinca_ativa = False
        self.distancia_pinca = 0.0

        self.inicio_gesto_cor = None
        self.gesto_cor_executado = False

        self.inicio_gesto_limpar = None
        self.gesto_limpar_executado = False