import tkinter as tk
import math
import time
import random

# ============================================================
# CONFIGURAÇÕES
# ============================================================

LARGURA = 1000
ALTURA = 700

FOV = math.pi / 3
NUM_RAIOS = 250
PROF_MAX = 20
PASSO_RAY = 0.03

ESCALA = LARGURA / NUM_RAIOS

COR_CEU = "#FF845F"
COR_CHAO = "#303030"

# ============================================================
# MAPA
# ============================================================

MAPA = [
    "###############",
    "#.............#",
    "#.....#.......#",
    "#.............#",
    "#.............#",
    "#....####.....#",
    "#.............#",
    "#.............#",
    "#.......#.....#",
    "#.............#",
    "###############"
]

# ============================================================
# JOGADOR
# ============================================================

class Jogador:

    def __init__(self):

        self.x = 3.5
        self.y = 3.5

        self.angulo = 0

        self.velocidade = 0.08
        self.rotacao = 0.08

        self.vida = 100
        self.municao = 50


player = Jogador()

# ============================================================
# JANELA
# ============================================================

janela = tk.Tk()

janela.title("Python DOOM - BETA")

janela.resizable(False, False)

canvas = tk.Canvas(
    janela,
    width=LARGURA,
    height=ALTURA,
    bg="black",
    highlightthickness=0
)

canvas.pack()

# ============================================================
# TECLAS
# ============================================================

teclas = set()


def pressionar(event):

    tecla = event.keysym

    teclas.add(tecla)

    if tecla == "space":

        atirar()


def soltar(event):

    teclas.discard(event.keysym)


janela.bind("<KeyPress>", pressionar)
janela.bind("<KeyRelease>", soltar)

# ============================================================
# COLISÃO
# ============================================================

def parede(x, y):

    if x < 0 or y < 0:
        return True

    if int(y) >= len(MAPA):
        return True

    if int(x) >= len(MAPA[0]):
        return True

    return MAPA[int(y)][int(x)] == "#"


# ============================================================
# MOVIMENTO DO JOGADOR
# ============================================================

def mover():

    if game_over:
        return

    if "Left" in teclas or "a" in teclas:

        player.angulo -= player.rotacao

    if "Right" in teclas or "d" in teclas:

        player.angulo += player.rotacao

    novo_x = player.x
    novo_y = player.y

    if "Up" in teclas or "w" in teclas:

        novo_x += (
            math.cos(player.angulo)
            * player.velocidade
        )

        novo_y += (
            math.sin(player.angulo)
            * player.velocidade
        )

    if "Down" in teclas or "s" in teclas:

        novo_x -= (
            math.cos(player.angulo)
            * player.velocidade
        )

        novo_y -= (
            math.sin(player.angulo)
            * player.velocidade
        )

    if not parede(novo_x, player.y):

        player.x = novo_x

    if not parede(player.x, novo_y):

        player.y = novo_y


# ============================================================
# RAYCAST
# ============================================================

zbuffer = []


def raycast():

    global zbuffer

    zbuffer = []

    # Céu

    canvas.create_rectangle(
        0,
        0,
        LARGURA,
        ALTURA // 2,
        fill=COR_CEU,
        outline=""
    )

    # Chão

    canvas.create_rectangle(
        0,
        ALTURA // 2,
        LARGURA,
        ALTURA,
        fill=COR_CHAO,
        outline=""
    )

    # Raios

    for raio in range(NUM_RAIOS):

        angulo_raio = (
            player.angulo
            - FOV / 2
            + FOV * raio / NUM_RAIOS
        )

        distancia = 0

        while distancia < PROF_MAX:

            rx = (
                player.x
                + math.cos(angulo_raio)
                * distancia
            )

            ry = (
                player.y
                + math.sin(angulo_raio)
                * distancia
            )

            if parede(rx, ry):

                break

            distancia += PASSO_RAY

        distancia *= math.cos(
            angulo_raio - player.angulo
        )

        zbuffer.append(distancia)

        altura_parede = (
            700 /
            (distancia + 0.0001)
        )

        brilho = int(
            255 /
            (1 + distancia * 0.25)
        )

        brilho = max(
            30,
            min(255, brilho)
        )

        cor = (
            f"#{brilho:02x}"
            f"{brilho:02x}"
            f"{brilho:02x}"
        )

        x1 = raio * ESCALA

        y1 = (
            ALTURA / 2
            - altura_parede / 2
        )

        y2 = (
            ALTURA / 2
            + altura_parede / 2
        )

        canvas.create_rectangle(
            x1,
            y1,
            x1 + ESCALA + 1,
            y2,
            fill=cor,
            outline=cor
        )


# ============================================================
# POSIÇÃO DE RESPAWN
# ============================================================

def encontrar_spawn():

    tentativas = 0

    while tentativas < 100:

        x = random.uniform(
            1.5,
            len(MAPA[0]) - 1.5
        )

        y = random.uniform(
            1.5,
            len(MAPA) - 1.5
        )

        if parede(x, y):

            tentativas += 1
            continue

        distancia = math.sqrt(
            (x - player.x) ** 2
            +
            (y - player.y) ** 2
        )

        # Não nascer grudado no jogador

        if distancia < 3:

            tentativas += 1
            continue

        return x, y

    return 8.5, 5.5


# ============================================================
# INIMIGO
# ============================================================

class Inimigo:

    def __init__(self):

        self.x = 0
        self.y = 0

        self.vida = 100

        self.vivo = True

        self.velocidade = 0.025

        self.dano = 1

        self.raio_colisao = 0.35

        self.respawn()

    # --------------------------------------------------------

    def respawn(self):

        self.x, self.y = encontrar_spawn()

        self.vida = 100

        self.vivo = True

    # --------------------------------------------------------

    def atualizar(self):

        if not self.vivo:
            return

        dx = player.x - self.x
        dy = player.y - self.y

        distancia = math.sqrt(
            dx ** 2 +
            dy ** 2
        )

        if distancia > 0.6:

            novo_x = (
                self.x
                +
                (dx / distancia)
                * self.velocidade
            )

            novo_y = (
                self.y
                +
                (dy / distancia)
                * self.velocidade
            )

            if not parede(
                novo_x,
                self.y
            ):

                self.x = novo_x

            if not parede(
                self.x,
                novo_y
            ):

                self.y = novo_y

        else:

            causar_dano_jogador(self.dano)

    # --------------------------------------------------------

    def receber_dano(self, dano):

        if not self.vivo:
            return

        self.vida -= dano

        if self.vida <= 0:

            self.morrer()

    # --------------------------------------------------------

    def morrer(self):

        self.vivo = False

        # Respawn depois de 2 segundos

        janela.after(
            2000,
            self.respawn
        )


# ============================================================
# CRIAR 2 INIMIGOS
# ============================================================

inimigos = [

    Inimigo(),

    Inimigo()

]

# ============================================================
# DANO AO JOGADOR
# ============================================================

ultimo_dano = 0


def causar_dano_jogador(dano):

    global ultimo_dano

    agora = time.time()

    # Pequeno cooldown para não perder
    # toda a vida instantaneamente

    if agora - ultimo_dano < 0.5:
        return

    ultimo_dano = agora

    player.vida -= dano

    if player.vida <= 0:

        player.vida = 0

        finalizar_jogo()


# ============================================================
# TIRO
# ============================================================

def atirar():

    if game_over:
        return

    if player.municao <= 0:
        return

    player.municao -= 1

    melhor_inimigo = None

    menor_diferenca = 999

    menor_distancia = 999

    for inimigo in inimigos:

        if not inimigo.vivo:
            continue

        dx = inimigo.x - player.x
        dy = inimigo.y - player.y

        distancia = math.sqrt(
            dx ** 2 +
            dy ** 2
        )

        angulo = math.atan2(
            dy,
            dx
        )

        diferenca = (
            angulo -
            player.angulo
        )

        while diferenca > math.pi:

            diferenca -= 2 * math.pi

        while diferenca < -math.pi:

            diferenca += 2 * math.pi

        if abs(diferenca) < menor_diferenca:

            # Limite da mira

            if abs(diferenca) < 0.10:

                melhor_inimigo = inimigo

                menor_diferenca = abs(
                    diferenca
                )

                menor_distancia = distancia

    if melhor_inimigo:

        # Dano maior de perto

        if menor_distancia < 5:

            dano = 50

        else:

            dano = 25

        melhor_inimigo.receber_dano(dano)

    iniciar_animacao_tiro()


# ============================================================
# ANIMAÇÃO DA ARMA
# ============================================================

atirando = False
tempo_tiro = 0


def iniciar_animacao_tiro():

    global atirando
    global tempo_tiro

    atirando = True

    tempo_tiro = 6


def atualizar_animacao_tiro():

    global atirando
    global tempo_tiro

    if atirando:

        tempo_tiro -= 1

        if tempo_tiro <= 0:

            atirando = False


# ============================================================
# DESENHAR INIMIGOS
# ============================================================

def desenhar_inimigos():

    inimigos_visiveis = []

    for inimigo in inimigos:

        if not inimigo.vivo:
            continue

        dx = (
            inimigo.x
            - player.x
        )

        dy = (
            inimigo.y
            - player.y
        )

        distancia = math.sqrt(
            dx ** 2 +
            dy ** 2
        )

        angulo_sprite = math.atan2(
            dy,
            dx
        )

        diferenca = (
            angulo_sprite
            -
            player.angulo
        )

        while diferenca > math.pi:

            diferenca -= 2 * math.pi

        while diferenca < -math.pi:

            diferenca += 2 * math.pi

        if abs(diferenca) > FOV / 2:

            continue

        inimigos_visiveis.append(
            (
                distancia,
                diferenca,
                inimigo
            )
        )

    # Desenha os mais distantes primeiro

    inimigos_visiveis.sort(
        reverse=True
    )

    for distancia, diferenca, inimigo in inimigos_visiveis:

        tamanho = 500 / (
            distancia + 0.01
        )

        tela_x = (
            (
                diferenca
                + FOV / 2
            )
            / FOV
        ) * LARGURA

        x1 = (
            tela_x
            - tamanho / 2
        )

        y1 = (
            ALTURA / 2
            - tamanho / 2
        )

        x2 = (
            tela_x
            + tamanho / 2
        )

        y2 = (
            ALTURA / 2
            + tamanho / 2
        )

        # Corpo

        canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill="#8B0000",
            outline="black",
            width=3
        )

        # Cabeça

        canvas.create_oval(
            x1 + tamanho * 0.2,
            y1 + tamanho * 0.1,
            x2 - tamanho * 0.2,
            y1 + tamanho * 0.6,
            fill="#B22222",
            outline="black"
        )

        # Olho esquerdo

        canvas.create_oval(
            x1 + tamanho * 0.30,
            y1 + tamanho * 0.25,
            x1 + tamanho * 0.42,
            y1 + tamanho * 0.38,
            fill="yellow"
        )

        # Olho direito

        canvas.create_oval(
            x1 + tamanho * 0.58,
            y1 + tamanho * 0.25,
            x1 + tamanho * 0.70,
            y1 + tamanho * 0.38,
            fill="yellow"
        )

        # Vida do inimigo

        barra_largura = tamanho * 0.8

        vida_percentual = (
            inimigo.vida / 100
        )

        canvas.create_rectangle(
            tela_x - barra_largura / 2,
            y1 - 10,
            tela_x + barra_largura / 2,
            y1 - 5,
            fill="black",
            outline=""
        )

        canvas.create_rectangle(
            tela_x - barra_largura / 2,
            y1 - 10,
            tela_x
            - barra_largura / 2
            + barra_largura
            * vida_percentual,
            y1 - 5,
            fill="red",
            outline=""
        )


# ============================================================
# MIRA
# ============================================================

def desenhar_mira():

    centro_x = LARGURA // 2
    centro_y = ALTURA // 2

    canvas.create_line(
        centro_x - 10,
        centro_y,
        centro_x + 10,
        centro_y,
        fill="white",
        width=2
    )

    canvas.create_line(
        centro_x,
        centro_y - 10,
        centro_x,
        centro_y + 10,
        fill="white",
        width=2
    )


# ============================================================
# ARMA
# ============================================================

def desenhar_arma():

    deslocamento = 0

    if atirando:

        deslocamento = 20

    x1 = 390
    y1 = 520 + deslocamento

    x2 = 610
    y2 = 690 + deslocamento

    # Corpo da arma

    canvas.create_rectangle(
        x1,
        y1,
        x2,
        y2,
        fill="gray50",
        outline="black",
        width=4
    )

    # Cano

    canvas.create_rectangle(
        480,
        470 + deslocamento,
        520,
        560 + deslocamento,
        fill="gray20",
        outline="black",
        width=3
    )

    # Disparo

    if atirando:

        canvas.create_polygon(
            480,
            470,
            500,
            420,
            520,
            470,
            fill="yellow",
            outline="orange"
        )


# ============================================================
# MINIMAPA
# ============================================================

TAMANHO = 12


def desenhar_minimapa():

    for y, linha in enumerate(MAPA):

        for x, bloco in enumerate(linha):

            if bloco == "#":

                cor = "gray20"

            else:

                cor = "white"

            canvas.create_rectangle(
                x * TAMANHO,
                y * TAMANHO,
                x * TAMANHO + TAMANHO,
                y * TAMANHO + TAMANHO,
                fill=cor,
                outline="black"
            )

    # Jogador

    px = (
        player.x
        * TAMANHO
    )

    py = (
        player.y
        * TAMANHO
    )

    canvas.create_oval(
        px - 3,
        py - 3,
        px + 3,
        py + 3,
        fill="blue",
        outline=""
    )

    # Direção

    lx = (
        px
        +
        math.cos(player.angulo)
        * 10
    )

    ly = (
        py
        +
        math.sin(player.angulo)
        * 10
    )

    canvas.create_line(
        px,
        py,
        lx,
        ly,
        fill="blue",
        width=2
    )

    # Inimigos

    for inimigo in inimigos:

        if not inimigo.vivo:
            continue

        ix = (
            inimigo.x
            * TAMANHO
        )

        iy = (
            inimigo.y
            * TAMANHO
        )

        canvas.create_oval(
            ix - 3,
            iy - 3,
            ix + 3,
            iy + 3,
            fill="red",
            outline=""
        )


# ============================================================
# FPS
# ============================================================

ultimo_tempo = time.time()
fps = 0


def calcular_fps():

    global ultimo_tempo
    global fps

    agora = time.time()

    delta = (
        agora -
        ultimo_tempo
    )

    if delta > 0:

        fps = int(1 / delta)

    ultimo_tempo = agora


# ============================================================
# HUD
# ============================================================

def desenhar_hud():

    # Vida

    canvas.create_text(
        40,
        ALTURA - 30,
        text=f"VIDA: {player.vida}",
        fill="white",
        anchor="w",
        font=("Arial", 18, "bold")
    )

    # Munição

    canvas.create_text(
        300,
        ALTURA - 30,
        text=f"MUNIÇÃO: {player.municao}",
        fill="white",
        anchor="w",
        font=("Arial", 18, "bold")
    )

    # FPS

    canvas.create_text(
        LARGURA - 20,
        20,
        text=f"FPS: {fps}",
        fill="white",
        anchor="e",
        font=("Arial", 12)
    )

    # Inimigos vivos

    vivos = 0

    for inimigo in inimigos:

        if inimigo.vivo:

            vivos += 1

    canvas.create_text(
        LARGURA - 20,
        45,
        text=f"INIMIGOS: {vivos}/2",
        fill="white",
        anchor="e",
        font=("Arial", 12)
    )


# ============================================================
# GAME OVER
# ============================================================

game_over = False


def finalizar_jogo():

    global game_over

    game_over = True


def desenhar_game_over():

    canvas.create_rectangle(
        0,
        0,
        LARGURA,
        ALTURA,
        fill="black",
        outline=""
    )

    canvas.create_text(
        LARGURA // 2,
        ALTURA // 2 - 30,
        text="GAME OVER",
        fill="red",
        font=(
            "Arial",
            60,
            "bold"
        )
    )

    canvas.create_text(
        LARGURA // 2,
        ALTURA // 2 + 40,
        text="Pressione R para reiniciar",
        fill="white",
        font=("Arial", 20)
    )


# ============================================================
# REINICIAR
# ============================================================

def reiniciar():

    global game_over

    player.x = 3.5
    player.y = 3.5

    player.angulo = 0

    player.vida = 100
    player.municao = 50

    for inimigo in inimigos:

        inimigo.respawn()

    game_over = False


# ============================================================
# REINICIAR COM R
# ============================================================

def tecla_reiniciar(event):

    if event.keysym.lower() == "r":

        if game_over:

            reiniciar()


janela.bind("<KeyPress-r>", tecla_reiniciar)
janela.bind("<KeyPress-R>", tecla_reiniciar)


# ============================================================
# ATUALIZAR INIMIGOS
# ============================================================

def atualizar_inimigos():

    if game_over:
        return

    for inimigo in inimigos:

        inimigo.atualizar()


# ============================================================
# LOOP PRINCIPAL
# ============================================================

def atualizar():

    calcular_fps()

    canvas.delete("all")

    if not game_over:

        mover()

        atualizar_inimigos()

        raycast()

        desenhar_inimigos()

        desenhar_arma()

        desenhar_mira()

        desenhar_minimapa()

        desenhar_hud()

        atualizar_animacao_tiro()

    else:

        desenhar_game_over()

    janela.after(
        16,
        atualizar
    )


# ============================================================
# INICIAR
# ============================================================

atualizar()

janela.mainloop()