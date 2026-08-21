import tkinter as tk
import math
import time
import random

from PIL import Image, ImageTk
from playsound import playsound
import threading


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

janela.focus_force()


# ============================================================
# SPRITES
# ============================================================

def carregar_sprite(caminho):

    try:

        return Image.open(
            caminho
        ).convert("RGBA")

    except FileNotFoundError:

        print()
        print("ERRO AO CARREGAR:")
        print(caminho)
        print()

        janela.destroy()

        raise SystemExit


arma_normal = carregar_sprite(
    "assets/weapons/arma.png"
)

arma_fogo = carregar_sprite(
    "assets/weapons/arma_fogo.png"
)

demon = carregar_sprite(
    "assets/enemies/demon.png"
)

demon_morto = carregar_sprite(
    "assets/enemies/demon2.png"
)


# ============================================================
# SOM DO TIRO
# ============================================================

CAMINHO_SOM = "som1.mp3"


def tocar_som_tiro():

    try:

        playsound(
            CAMINHO_SOM,
            block=False
        )

    except Exception as erro:

        print(
            "Erro ao tocar som:",
            erro
        )


# ============================================================
# TRANSPARÊNCIA
# ============================================================

def recortar_transparencia(imagem):

    alpha = imagem.getchannel("A")

    caixa = alpha.getbbox()

    if caixa:

        return imagem.crop(caixa)

    return imagem


arma_normal = recortar_transparencia(
    arma_normal
)

arma_fogo = recortar_transparencia(
    arma_fogo
)

demon = recortar_transparencia(
    demon
)

demon_morto = recortar_transparencia(
    demon_morto
)


# ============================================================
# TAMANHO DA ARMA
# ============================================================

TAMANHO_ARMA = (
    400,
    295
)


arma_normal = arma_normal.resize(
    TAMANHO_ARMA,
    Image.Resampling.LANCZOS
)

arma_fogo = arma_fogo.resize(
    TAMANHO_ARMA,
    Image.Resampling.LANCZOS
)


arma_normal_tk = ImageTk.PhotoImage(
    arma_normal
)

arma_fogo_tk = ImageTk.PhotoImage(
    arma_fogo
)


# ============================================================
# TECLAS
# ============================================================

teclas = set()


def pressionar(event):

    tecla = event.keysym.lower()

    teclas.add(tecla)

    if tecla == "space":

        atirar()

    if tecla == "r":

        if game_over:

            reiniciar()


def soltar(event):

    tecla = event.keysym.lower()

    teclas.discard(tecla)


janela.bind(
    "<KeyPress>",
    pressionar
)

janela.bind(
    "<KeyRelease>",
    soltar
)


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
# SPAWN
# ============================================================

def encontrar_spawn():

    for tentativa in range(100):

        x = random.uniform(
            1.5,
            len(MAPA[0]) - 1.5
        )

        y = random.uniform(
            1.5,
            len(MAPA) - 1.5
        )


        if parede(x, y):

            continue


        distancia = math.sqrt(
            (x - player.x) ** 2
            +
            (y - player.y) ** 2
        )


        if distancia < 3:

            continue


        return x, y


    return 8.5, 5.5


# ============================================================
# MOVIMENTO
# ============================================================

def mover():

    if game_over:

        return


    if "left" in teclas or "a" in teclas:

        player.angulo -= player.rotacao


    if "right" in teclas or "d" in teclas:

        player.angulo += player.rotacao


    novo_x = player.x
    novo_y = player.y


    if "up" in teclas or "w" in teclas:

        novo_x += (
            math.cos(player.angulo)
            *
            player.velocidade
        )

        novo_y += (
            math.sin(player.angulo)
            *
            player.velocidade
        )


    if "down" in teclas or "s" in teclas:

        novo_x -= (
            math.cos(player.angulo)
            *
            player.velocidade
        )

        novo_y -= (
            math.sin(player.angulo)
            *
            player.velocidade
        )


    if not parede(
        novo_x,
        player.y
    ):

        player.x = novo_x


    if not parede(
        player.x,
        novo_y
    ):

        player.y = novo_y


# ============================================================
# Z-BUFFER
# ============================================================

zbuffer = []


# ============================================================
# RAYCAST
# ============================================================

def raycast():

    global zbuffer

    zbuffer = []


    canvas.create_rectangle(
        0,
        0,
        LARGURA,
        ALTURA // 2,
        fill=COR_CEU,
        outline=""
    )


    canvas.create_rectangle(
        0,
        ALTURA // 2,
        LARGURA,
        ALTURA,
        fill=COR_CHAO,
        outline=""
    )


    for raio in range(NUM_RAIOS):

        angulo_raio = (
            player.angulo
            -
            FOV / 2
            +
            FOV
            *
            raio
            /
            NUM_RAIOS
        )


        distancia = 0


        while distancia < PROF_MAX:

            rx = (
                player.x
                +
                math.cos(angulo_raio)
                *
                distancia
            )

            ry = (
                player.y
                +
                math.sin(angulo_raio)
                *
                distancia
            )


            if parede(rx, ry):

                break


            distancia += PASSO_RAY


        distancia *= math.cos(
            angulo_raio
            -
            player.angulo
        )


        zbuffer.append(
            distancia
        )


        altura_parede = (
            700
            /
            (
                distancia
                +
                0.0001
            )
        )


        brilho = int(
            255
            /
            (
                1
                +
                distancia
                *
                0.25
            )
        )


        brilho = max(
            30,
            min(
                255,
                brilho
            )
        )


        cor = (
            f"#{brilho:02x}"
            f"{brilho:02x}"
            f"{brilho:02x}"
        )


        x1 = raio * ESCALA

        y1 = (
            ALTURA / 2
            -
            altura_parede / 2
        )

        y2 = (
            ALTURA / 2
            +
            altura_parede / 2
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
# INIMIGO
# ============================================================

class Inimigo:

    def __init__(self):

        self.x = 0
        self.y = 0

        self.vida = 100

        self.vivo = True

        self.morrendo = False

        self.velocidade = 0.025

        self.dano = 5

        self.cooldown_ataque = 0

        self.respawn()


    def respawn(self):

        self.x, self.y = encontrar_spawn()

        self.vida = 100

        self.vivo = True

        self.morrendo = False

        self.cooldown_ataque = 0


    def atualizar(self):

        if not self.vivo:

            return


        dx = player.x - self.x
        dy = player.y - self.y


        distancia = math.sqrt(
            dx ** 2 +
            dy ** 2
        )


        if distancia > 0.7:

            novo_x = (
                self.x
                +
                (
                    dx / distancia
                )
                *
                self.velocidade
            )


            novo_y = (
                self.y
                +
                (
                    dy / distancia
                )
                *
                self.velocidade
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

            self.atacar()


        if self.cooldown_ataque > 0:

            self.cooldown_ataque -= 1


    def atacar(self):

        if self.cooldown_ataque > 0:

            return


        causar_dano_jogador(
            self.dano
        )


        self.cooldown_ataque = 30


    def receber_dano(self, dano):

        if not self.vivo:

            return


        self.vida -= dano


        if self.vida <= 0:

            self.morrer()


    def morrer(self):

        if not self.vivo:

            return


        self.vivo = False

        self.morrendo = True

        self.vida = 0


        janela.after(
            2000,
            self.respawn
        )


# ============================================================
# CRIAR OS 2 DEMONS
# ============================================================

inimigos = [
    Inimigo(),
    Inimigo()
]


# ============================================================
# DANO NO JOGADOR
# ============================================================

ultimo_dano = 0


def causar_dano_jogador(dano):

    global ultimo_dano

    agora = time.time()


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

atirando = False
tempo_tiro = 0


def atirar():

    global atirando
    global tempo_tiro


    if game_over:

        return


    if player.municao <= 0:

        return


    player.municao -= 1


    # --------------------------------------------------------
    # SOM
    # --------------------------------------------------------

    threading.Thread(
        target=tocar_som_tiro,
        daemon=True
    ).start()


    # --------------------------------------------------------
    # ANIMAÇÃO
    # --------------------------------------------------------

    atirando = True

    tempo_tiro = 6


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
            angulo
            -
            player.angulo
        )


        while diferenca > math.pi:

            diferenca -= (
                2 * math.pi
            )


        while diferenca < -math.pi:

            diferenca += (
                2 * math.pi
            )


        if abs(diferenca) < 0.10:

            if abs(diferenca) < menor_diferenca:

                melhor_inimigo = inimigo

                menor_diferenca = abs(
                    diferenca
                )

                menor_distancia = distancia


    if melhor_inimigo:

        if menor_distancia < 5:

            dano = 50

        else:

            dano = 25


        melhor_inimigo.receber_dano(
            dano
        )


# ============================================================
# ANIMAÇÃO DA ARMA
# ============================================================

def atualizar_animacao_tiro():

    global atirando
    global tempo_tiro


    if not atirando:

        return


    tempo_tiro -= 1


    if tempo_tiro <= 0:

        atirando = False


# ============================================================
# ARMA
# ============================================================

def desenhar_arma():

    if atirando:

        sprite = arma_fogo_tk

    else:

        sprite = arma_normal_tk


    canvas.create_image(
        LARGURA // 2,
        ALTURA + 5,
        image=sprite,
        anchor="s"
    )


# ============================================================
# INIMIGOS NA TELA
# ============================================================

def desenhar_inimigos():

    inimigos_visiveis = []


    for inimigo in inimigos:

        if not inimigo.vivo and not inimigo.morrendo:

            continue


        dx = inimigo.x - player.x
        dy = inimigo.y - player.y


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

            diferenca -= (
                2 * math.pi
            )


        while diferenca < -math.pi:

            diferenca += (
                2 * math.pi
            )


        if abs(diferenca) > FOV / 2:

            continue


        inimigos_visiveis.append(
            (
                distancia,
                diferenca,
                inimigo
            )
        )


    inimigos_visiveis.sort(
        key=lambda item: item[0],
        reverse=True
    )


    canvas.sprites_demons = []


    for (
        distancia,
        diferenca,
        inimigo
    ) in inimigos_visiveis:


        tamanho = (
            500
            /
            (
                distancia
                +
                0.01
            )
        )


        tamanho = max(
            30,
            min(
                450,
                tamanho
            )
        )


        tela_x = (
            (
                diferenca
                +
                FOV / 2
            )
            /
            FOV
        ) * LARGURA


        if inimigo.vivo:

            imagem = demon

        else:

            imagem = demon_morto


        sprite = imagem.resize(
            (
                int(tamanho),
                int(tamanho)
            ),
            Image.Resampling.NEAREST
        )


        sprite_tk = ImageTk.PhotoImage(
            sprite
        )


        canvas.sprites_demons.append(
            sprite_tk
        )


        if inimigo.vivo:

            pos_y = (
                ALTURA / 2
                +
                tamanho * 0.10
            )

        else:

            pos_y = (
                ALTURA / 2
                +
                tamanho * 0.30
            )


        canvas.create_image(
            tela_x,
            pos_y,
            image=sprite_tk,
            anchor="center"
        )


        if inimigo.vivo:

            barra_largura = max(
                30,
                tamanho * 0.7
            )


            vida_percentual = (
                inimigo.vida / 100
            )


            canvas.create_rectangle(
                tela_x - barra_largura / 2,
                pos_y - tamanho / 2 - 12,
                tela_x + barra_largura / 2,
                pos_y - tamanho / 2 - 7,
                fill="black",
                outline=""
            )


            canvas.create_rectangle(
                tela_x - barra_largura / 2,
                pos_y - tamanho / 2 - 12,
                tela_x
                -
                barra_largura / 2
                +
                barra_largura
                *
                vida_percentual,
                pos_y - tamanho / 2 - 7,
                fill="red",
                outline=""
            )


# ============================================================
# MIRA
# ============================================================

def desenhar_mira():

    cx = LARGURA // 2
    cy = ALTURA // 2


    canvas.create_line(
        cx - 10,
        cy,
        cx + 10,
        cy,
        fill="white",
        width=2
    )


    canvas.create_line(
        cx,
        cy - 10,
        cx,
        cy + 10,
        fill="white",
        width=2
    )


# ============================================================
# MINIMAPA
# ============================================================

TAMANHO_MINIMAPA = 12


def desenhar_minimapa():

    for y, linha in enumerate(MAPA):

        for x, bloco in enumerate(linha):

            cor = (
                "gray20"
                if bloco == "#"
                else "white"
            )


            canvas.create_rectangle(
                x * TAMANHO_MINIMAPA,
                y * TAMANHO_MINIMAPA,
                x * TAMANHO_MINIMAPA
                +
                TAMANHO_MINIMAPA,
                y * TAMANHO_MINIMAPA
                +
                TAMANHO_MINIMAPA,
                fill=cor,
                outline="black"
            )


    px = (
        player.x
        *
        TAMANHO_MINIMAPA
    )

    py = (
        player.y
        *
        TAMANHO_MINIMAPA
    )


    canvas.create_oval(
        px - 3,
        py - 3,
        px + 3,
        py + 3,
        fill="blue",
        outline=""
    )


    lx = (
        px
        +
        math.cos(player.angulo)
        *
        10
    )

    ly = (
        py
        +
        math.sin(player.angulo)
        *
        10
    )


    canvas.create_line(
        px,
        py,
        lx,
        ly,
        fill="blue",
        width=2
    )


    for inimigo in inimigos:

        if not inimigo.vivo:

            continue


        ix = (
            inimigo.x
            *
            TAMANHO_MINIMAPA
        )

        iy = (
            inimigo.y
            *
            TAMANHO_MINIMAPA
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

    delta = agora - ultimo_tempo


    if delta > 0:

        fps = int(
            1 / delta
        )


    ultimo_tempo = agora


# ============================================================
# HUD
# ============================================================

def desenhar_hud():

    canvas.create_text(
        40,
        ALTURA - 30,
        text=f"VIDA: {player.vida}",
        fill="white",
        anchor="w",
        font=(
            "Arial",
            18,
            "bold"
        )
    )


    canvas.create_text(
        300,
        ALTURA - 30,
        text=f"MUNIÇÃO: {player.municao}",
        fill="white",
        anchor="w",
        font=(
            "Arial",
            18,
            "bold"
        )
    )


    canvas.create_text(
        LARGURA - 20,
        20,
        text=f"FPS: {fps}",
        fill="white",
        anchor="e",
        font=(
            "Arial",
            12
        )
    )


    vivos = sum(
        1
        for inimigo in inimigos
        if inimigo.vivo
    )


    canvas.create_text(
        LARGURA - 20,
        45,
        text=f"INIMIGOS: {vivos}/2",
        fill="white",
        anchor="e",
        font=(
            "Arial",
            12
        )
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
        text="PRESSIONE R PARA REINICIAR",
        fill="white",
        font=(
            "Arial",
            20,
            "bold"
        )
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
# ATUALIZAR INIMIGOS
# ============================================================

def atualizar_inimigos():

    if game_over:

        return


    for inimigo in inimigos:

        inimigo.atualizar()


# ============================================================
# LOOP
# ============================================================

def atualizar():

    calcular_fps()

    canvas.delete("all")

    canvas.sprites_demons = []


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