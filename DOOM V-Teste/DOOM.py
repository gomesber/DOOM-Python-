import tkinter as tk
import math
import time

# ================= CONFIGURAÇÕES =================

LARGURA = 1000
ALTURA = 700

FOV = math.pi / 3
NUM_RAIOS = 250
PROF_MAX = 20
PASSO_RAY = 0.03

ESCALA = LARGURA / NUM_RAIOS

COR_CEU = "#FF845F"
COR_CHAO = "#303030"

# ================= MAPA =================

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

# ================= JOGADOR =================

class Jogador:

    def __init__(self):
        self.x = 3.5
        self.y = 3.5
        self.angulo = 0
        self.velocidade = 0.08
        self.rotacao = 0.08

player = Jogador()

# ================= JANELA =================

janela = tk.Tk()
janela.title("Python DOOM")

canvas = tk.Canvas(
    janela,
    width=LARGURA,
    height=ALTURA,
    bg="black"
)

canvas.pack()

# ================= TECLAS =================

teclas = set()

def pressionar(event):
    teclas.add(event.keysym)

def soltar(event):
    teclas.discard(event.keysym)

janela.bind("<KeyPress>", pressionar)
janela.bind("<KeyRelease>", soltar)

# ================= COLISÃO =================

def parede(x, y):

    if x < 0 or y < 0:
        return True

    if int(y) >= len(MAPA):
        return True

    if int(x) >= len(MAPA[0]):
        return True

    return MAPA[int(y)][int(x)] == "#"

# ================= MOVIMENTO =================

def mover():

    if "Left" in teclas:
        player.angulo -= player.rotacao

    if "Right" in teclas:
        player.angulo += player.rotacao

    novo_x = player.x
    novo_y = player.y

    if "Up" in teclas:
        novo_x += math.cos(player.angulo) * player.velocidade
        novo_y += math.sin(player.angulo) * player.velocidade

    if "Down" in teclas:
        novo_x -= math.cos(player.angulo) * player.velocidade
        novo_y -= math.sin(player.angulo) * player.velocidade

    if not parede(novo_x, player.y):
        player.x = novo_x

    if not parede(player.x, novo_y):
        player.y = novo_y

# ================= RAYCAST =================

def raycast():

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
            - FOV / 2
            + FOV * raio / NUM_RAIOS
        )

        distancia = 0

        while distancia < PROF_MAX:

            rx = player.x + math.cos(angulo_raio) * distancia
            ry = player.y + math.sin(angulo_raio) * distancia

            if parede(rx, ry):
                break

            distancia += PASSO_RAY

        distancia *= math.cos(
            angulo_raio - player.angulo
        )

        altura_parede = 700 / (distancia + 0.0001)

        brilho = int(
            255 / (1 + distancia * 0.25)
        )

        brilho = max(30, min(255, brilho))

        cor = (
            f'#{brilho:02x}'
            f'{brilho:02x}'
            f'{brilho:02x}'
        )

        x1 = raio * ESCALA

        y1 = ALTURA / 2 - altura_parede / 2
        y2 = ALTURA / 2 + altura_parede / 2

        canvas.create_rectangle(
            x1,
            y1,
            x1 + ESCALA + 1,
            y2,
            fill=cor,
            outline=cor
        )

# ================= MINIMAPA =================

TAMANHO = 12

def desenhar_minimapa():

    for y, linha in enumerate(MAPA):

        for x, bloco in enumerate(linha):

            cor = "white"

            if bloco == "#":
                cor = "gray20"

            canvas.create_rectangle(
                x * TAMANHO,
                y * TAMANHO,
                x * TAMANHO + TAMANHO,
                y * TAMANHO + TAMANHO,
                fill=cor
            )

    px = player.x * TAMANHO
    py = player.y * TAMANHO

    canvas.create_oval(
        px - 3,
        py - 3,
        px + 3,
        py + 3,
        fill="red"
    )

    lx = px + math.cos(player.angulo) * 10
    ly = py + math.sin(player.angulo) * 10

    canvas.create_line(
        px,
        py,
        lx,
        ly,
        fill="red",
        width=2
    )

# ================= FPS =================

ultimo_tempo = time.time()
fps = 0

def mostrar_fps():

    global ultimo_tempo
    global fps

    agora = time.time()

    delta = agora - ultimo_tempo

    if delta > 0:
        fps = int(1 / delta)

    ultimo_tempo = agora

    canvas.create_text(
        930,
        20,
        text=f"FPS: {fps}",
        fill="white",
        font=("Arial", 12)
    )

# ================= ARMA =================

atirando = False
tempo_tiro = 0

def pressionar(event):

    global atirando
    global tempo_tiro

    teclas.add(event.keysym)

    if event.keysym == "space":
        if not atirando:
            atirando = True
            tempo_tiro = 5


# ================= INIMIGO =================

class Inimigo:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.vivo = True

        self.vida = 100

        self.velocidade = 0.02

        self.dano = 1

inimigos = []

inimigos.append(
    Inimigo(
        8.5,
        5.5
    )
)

vida = 100

municao = 50

game_over = False

inimigos.append(
    Inimigo(
        10.5,
        8.5
    )
)

inimigos.append(
    Inimigo(
        7.5,
        6.5
    )
)


# ================= MIRA =================

def desenhar_mira():

    centro_x = LARGURA // 2
    centro_y = ALTURA // 2

    canvas.create_line(
        centro_x - 10,
        centro_y,
        centro_x + 10,
        centro_y,
        fill="white"
    )

    canvas.create_line(
        centro_x,
        centro_y - 10,
        centro_x,
        centro_y + 10,
        fill="white"
    )


# ================= ARMA NA TELA =================

def desenhar_arma():

    deslocamento = 0

    global atirando
    global tempo_tiro

    if atirando:

        deslocamento = 20

        tempo_tiro -= 1

        if tempo_tiro <= 0:
            atirando = False

    x1 = 390
    y1 = 520 + deslocamento

    x2 = 610
    y2 = 690 + deslocamento

    canvas.create_rectangle(
        x1,
        y1,
        x2,
        y2,
        fill="gray50",
        outline="black",
        width=3
    )

    canvas.create_rectangle(
        480,
        480 + deslocamento,
        520,
        560 + deslocamento,
        fill="gray30",
        outline="black"
    )


# ================= SPRITES =================

def desenhar_inimigos():

    for inimigo in inimigos:

        if not inimigo.vivo:
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
            angulo_sprite -
            player.angulo
        )

        while diferenca > math.pi:
            diferenca -= 2 * math.pi

        while diferenca < -math.pi:
            diferenca += 2 * math.pi

        if abs(diferenca) > FOV / 2:
            continue

        tamanho = 500 / distancia

        tela_x = (
            (diferenca + FOV / 2)
            / FOV
        ) * LARGURA

        x1 = tela_x - tamanho / 2
        y1 = ALTURA / 2 - tamanho / 2

        x2 = tela_x + tamanho / 2
        y2 = ALTURA / 2 + tamanho / 2

        brilho = int(
            255 /
            (1 + distancia * 0.3)
        )

        brilho = max(
            50,
            min(
                255,
                brilho
            )
        )

        cor = (
            f'#ff'
            f'{brilho:02x}'
            f'{brilho:02x}'
        )

        canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=cor,
            outline="black",
            width=3
        )

        canvas.create_oval(
            x1 + tamanho * 0.25,
            y1 + tamanho * 0.3,
            x1 + tamanho * 0.4,
            y1 + tamanho * 0.45,
            fill="black"
        )

        canvas.create_oval(
            x1 + tamanho * 0.6,
            y1 + tamanho * 0.3,
            x1 + tamanho * 0.75,
            y1 + tamanho * 0.45,
            fill="black"
        )

# ================= HUD =================



#====================================================

        global vida

    global game_over

    for inimigo in inimigos:

        if not inimigo.vivo:
            continue

        dx = player.x - inimigo.x

        dy = player.y - inimigo.y

        distancia = math.sqrt(
            dx**2 +
            dy**2
        )

        if distancia > 0.5:

            inimigo.x += (
                dx / distancia
            ) * inimigo.velocidade

            inimigo.y += (
                dy / distancia
            ) * inimigo.velocidade

        else:

            vida -= inimigo.dano

        if vida <= 0:

            game_over = True

# ================= LOOP =================

def atualizar():

    mover()

    canvas.delete("all")

    raycast()

    desenhar_minimapa()

    mostrar_fps()

    janela.after(16, atualizar)

atualizar()

janela.mainloop()

atualizar()

janela.mainloop()

def desenhar_game_over():

    canvas.create_rectangle(
        0,
        0,
        LARGURA,
        ALTURA,
        fill="black"
    )

    canvas.create_text(
        LARGURA // 2,
        ALTURA // 2,
        text="GAME OVER",
        fill="red",
        font=(
            "Arial",
            50,
            "bold"
        )
    )