import pygame
import sys
import math
import random

# --- Inicialização ---
pygame.init()

# --- Configurações ---
LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pênaltis: Clássico Listrado")

# --- Cores ---
GRAMADO = (34, 139, 34)
LINHAS = (255, 255, 255)
BOLA_COR = (255, 255, 255)
TRAVE_COR = (200, 200, 200)
MIRA_COR = (255, 50, 50)
TEXTO_COR = (255, 215, 0)
PRETO = (0, 0, 0)

# --- LISTA DE TIMES ---
TIMES = [
    {"nome": "Botafogo",    "cores": [(0, 0, 0), (255, 255, 255)]}, # Preto e Branco
    {"nome": "Flamengo",    "cores": [(0, 0, 0), (200, 0, 0)]},     # Preto e Vermelho
    {"nome": "Fluminense",  "cores": [(130, 0, 0), (0, 100, 0)]},   # Grená e Verde
    {"nome": "Vasco",       "cores": [(255, 255, 255), (0, 0, 0)]}, # Branco e Preto
    {"nome": "Grêmio",      "cores": [(0, 0, 0), (0, 0, 255)]},     # Preto e Azul
    {"nome": "Brasil",      "cores": [(255, 255, 0), (0, 150, 0)]}, # Amarelo e Verde
    {"nome": "Argentina",   "cores": [(255, 255, 255), (100, 200, 255)]}, # Branco e Azul Claro
]

# --- Variáveis Globais ---
placar_jogador = 0
placar_cpu = 0
rodada_atual = 1
max_rodadas = 5
turno = "JOGADOR"

# Variáveis do CHEAT VISUAL
cheat_alvo_x = 0
cheat_alvo_y = 0

# --- Elementos do Campo ---
GOL_X = LARGURA // 2 - 150
GOL_Y = 80
GOL_LARGURA = 300
GOL_ALTURA = 80

# Goleiro
goleiro_largura = 60
goleiro_altura = 40
goleiro_x = LARGURA // 2 - goleiro_largura // 2
goleiro_y = GOL_Y + 50
velocidade_goleiro = 8

# Bola
bola_raio = 10
bola_inicial_x = LARGURA // 2
bola_inicial_y = ALTURA - 100
bola_x = bola_inicial_x
bola_y = bola_inicial_y
velocidade_bola = 18

# Mira
mira_x = LARGURA // 2
mira_y = GOL_Y + 40
velocidade_mira = 5

# Comemoração
avatar_festa_x = 0
avatar_festa_y = 0
inicio_festa = 0
confetes = []

# Física
dx = 0
dy = 0
velocidade_goleiro_atual = 0

# Estados da Animação
PREPARANDO = 0
EM_MOVIMENTO = 1
COMEMORACAO = 2
RESULTADO = 3
FIM_DE_JOGO = 4

estado_animacao = PREPARANDO
msg_resultado = ""

fonte = pygame.font.SysFont("arial", 40, bold=True)
fonte_placar = pygame.font.SysFont("arial", 30, bold=True)
fonte_peq = pygame.font.SysFont("arial", 20)
relogio = pygame.time.Clock()

# --- NOVA FUNÇÃO DE DESENHO ---
def desenhar_personagem_listrado(superficie, x, y, largura, altura, cores, nome_time=""):
    """Desenha uniforme personalizado (Vasco com faixa) e símbolos"""
    
    cx = x + largura // 2
    cy = y + altura // 2

    # --- 1. DESENHO DO UNIFORME (Fundo) ---
    
    if nome_time == "Vasco":
        # REGRA EXCLUSIVA PARA VASCO: Fundo Preto com Faixa Diagonal Branca
        
        # A. Fundo Preto Sólido
        pygame.draw.rect(superficie, (0, 0, 0), (x, y, largura, altura))
        
        # B. Faixa Diagonal Branca (Top-Esq para Base-Dir)
        # Definimos 4 pontos para criar um polígono grosso que serve de faixa
        espessura_faixa = altura // 3 # Define a grossura da faixa
        
        pontos_faixa = [
            (x, y + altura),                                      # Canto Superior Esquerdo
            (x , y + altura - espessura_faixa), # Ponto na direita, um pouco acima do fim
            (x + largura, y ),                   # Canto Inferior Direito
            (x + largura, y + espessura_faixa)                     # Ponto na esquerda, um pouco abaixo do início
        ]
        pygame.draw.polygon(superficie, (255, 255, 255), pontos_faixa)
        
    else:
        # REGRA PADRÃO PARA OUTROS TIMES: Listras Verticais
        cor1, cor2 = cores
        largura_listra = 10 
        for i in range(0, largura, largura_listra):
            cor_atual = cor1 if (i // largura_listra) % 2 == 0 else cor2
            largura_atual = min(largura_listra, largura - i)
            rect_faixa = pygame.Rect(x + i, y, largura_atual, altura)
            pygame.draw.rect(superficie, cor_atual, rect_faixa)
    
    # 2. Borda do personagem (Comum a todos)
    pygame.draw.rect(superficie, (0,0,0), (x, y, largura, altura), 2)

    # --- 3. SÍMBOLOS ESPECIAIS (Por cima do uniforme) ---
    if nome_time == "Vasco" or nome_time == "Botafogo":
        tamanho_fonte = int(largura * 0.7)
        
        # Tenta achar a fonte de símbolos do Windows ou usa Arial
        caminho_fonte = pygame.font.match_font('segoe ui symbol') 
        if not caminho_fonte: caminho_fonte = pygame.font.match_font('arial')

        try:
            fonte_simbolo = pygame.font.Font(caminho_fonte, tamanho_fonte)
        except:
            fonte_simbolo = pygame.font.SysFont("arial", tamanho_fonte)

        if nome_time == "Vasco":
            # Cruz de Malta Vermelha (Unicode \u2720)
            # Ela vai ficar centralizada exatamente sobre a faixa branca
            try:
                texto = fonte_simbolo.render("\u2720", True, (200, 0, 0))
            except:
                texto = fonte_simbolo.render("+", True, (200, 0, 0))
            rect = texto.get_rect(center=(cx, cy))
            superficie.blit(texto, rect)

        elif nome_time == "Botafogo":
            # Estrela Solitária Branca com escudo preto (Unicode \u2605)
            tamanho_escudo = int(largura * 0.45)
            escudo = pygame.Rect(0, 0, tamanho_escudo, tamanho_escudo)
            escudo.center = (cx, cy)
            pygame.draw.rect(superficie, (0,0,0), escudo)
            
            texto = fonte_simbolo.render("\u2605", True, (255, 255, 255))
            rect = texto.get_rect(center=(cx, cy))
            superficie.blit(texto, rect)
 # ------------------------------

def criar_confetes():
    lista = []
    for _ in range(100):
        x = random.randint(0, LARGURA)
        y = random.randint(-500, 0)
        cor = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
        velocidade = random.randint(2, 7)
        lista.append([x, y, cor, velocidade])
    return lista

def reiniciar_rodada():
    global bola_x, bola_y, goleiro_x, mira_x, mira_y, estado_animacao, dx, dy, velocidade_goleiro_atual
    bola_x = bola_inicial_x
    bola_y = bola_inicial_y
    goleiro_x = LARGURA // 2 - goleiro_largura // 2
    mira_x = LARGURA // 2
    mira_y = GOL_Y + 40
    dx = 0
    dy = 0
    velocidade_goleiro_atual = 0
    estado_animacao = PREPARANDO

def reiniciar_jogo_completo():
    global placar_jogador, placar_cpu, rodada_atual, turno
    placar_jogador = 0
    placar_cpu = 0
    rodada_atual = 1
    turno = "JOGADOR"
    reiniciar_rodada()

# ---------------------------------------------------------
# MENU E CONFIGURAÇÕES INICIAIS
# ---------------------------------------------------------

TIMES = [
    {"nome": "Botafogo",    "cores": [(0, 0, 0), (255, 255, 255)]},
    {"nome": "Flamengo",    "cores": [(0, 0, 0), (200, 0, 0)]},
    {"nome": "Fluminense",  "cores": [(130, 0, 0), (0, 100, 0)]},
    {"nome": "Vasco",       "cores": [(255, 255, 255), (0, 0, 0)]},
    {"nome": "Grêmio",      "cores": [(0, 0, 0), (0, 0, 255)]},
    {"nome": "Corinthians", "cores": [(255, 255, 255), (0, 0, 0)]},
    {"nome": "Palmeiras",   "cores": [(0, 100, 0), (255, 255, 255)]},
    {"nome": "São Paulo",   "cores": [(255, 0, 0), (0, 0, 0)]}, # Simplificado tricolor
    {"nome": "Brasil",      "cores": [(255, 255, 0), (0, 150, 0)]},
    {"nome": "Argentina",   "cores": [(255, 255, 255), (100, 200, 255)]},
]

# ... (Seus imports, cores e definições de variáveis globais ficam aqui) ...

APP_RODANDO = True  # <--- NOVA VARIÁVEL MESTRE

while APP_RODANDO:  # <--- NOVO LOOP PAI
    
    # IMPORTANTE: Reiniciar as variáveis de controle do menu AQUI DENTRO
    selecionando_modo = True
    placar_jogador = 0
    placar_cpu = 0
    rodada_atual = 1
    turno = "JOGADOR"
    
    # ---------------------------------------------------------
    # AGORA VEM O SEU CÓDIGO EXISTENTE (MENU E JOGO)
    # TUDO ABAIXO DAQUI PRECISA DE UM 'TAB' PARA A DIREITA
    # ---------------------------------------------------------

    # while selecionando_modo: ... (Seu menu)
    
    # ... (Sua escolha de times) ...
    
    # rodando_jogo = True
    # while rodando_jogo: ... (Seu jogo)

# --- PASSO 1: ESCOLHER MODO DE JOGO ---
    modo_jogo = "CPU" # Padrão
    selecionando_modo = True

    while selecionando_modo:
        TELA.fill((20, 20, 40))
        
        txt_titulo = fonte.render("PENALTY KICK", True, (255, 255, 255))
        txt_1p = fonte.render("1. JOGADOR vs CPU", True, (0, 255, 0) if modo_jogo == "CPU" else (100, 100, 100))
        txt_2p = fonte.render("2. PLAYER 1 vs PLAYER 2", True, (0, 255, 0) if modo_jogo == "PVP" else (100, 100, 100))
        txt_inst = fonte_peq.render("Use SETAS para trocar e ENTER para confirmar", True, (200, 200, 200))

        TELA.blit(txt_titulo, (LARGURA//2 - txt_titulo.get_width()//2, 100))
        TELA.blit(txt_1p, (LARGURA//2 - txt_1p.get_width()//2, 250))
        TELA.blit(txt_2p, (LARGURA//2 - txt_2p.get_width()//2, 320))
        TELA.blit(txt_inst, (LARGURA//2 - txt_inst.get_width()//2, ALTURA - 100))
        
        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP or evento.key == pygame.K_DOWN:
                    modo_jogo = "PVP" if modo_jogo == "CPU" else "CPU"
                if evento.key == pygame.K_RETURN:
                    selecionando_modo = False

    # --- PASSO 2: ESCOLHER TIMES ---
    # Função auxiliar para escolher time (para não repetir código)
    def escolher_time(titulo_msg):
        idx = 0
        escolhendo = True
        while escolhendo:
            TELA.fill((30, 30, 30))
            titulo = fonte.render(titulo_msg, True, (255, 255, 255))
            TELA.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 80))
            
            # Desenha boneco
            time = TIMES[idx]
            desenhar_personagem_listrado(TELA, LARGURA//2 - 50, ALTURA//2 - 50, 100, 100, time["cores"], time["nome"])
            
            nome = fonte.render(f"< {time['nome']} >", True, (255, 215, 0))
            TELA.blit(nome, (LARGURA//2 - nome.get_width()//2, ALTURA//2 + 70))
            
            pygame.display.update()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT: pygame.quit(); sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RIGHT: idx = (idx + 1) % len(TIMES)
                    if evento.key == pygame.K_LEFT: idx = (idx - 1) % len(TIMES)
                    if evento.key == pygame.K_RETURN: return TIMES[idx]

    # Escolhe Time 1 (Sempre humano)
    time_p1 = escolher_time("ESCOLHA O TIME P1")

    # Escolhe Time 2 (Humano ou CPU)
    if modo_jogo == "PVP":
        # Pequena pausa para não pular direto com o mesmo Enter
        pygame.time.delay(500) 
        time_p2 = escolher_time("ESCOLHA O TIME P2")
    else:
        time_p2 = random.choice(TIMES)
        while time_p2 == time_p1: time_p2 = random.choice(TIMES)

    # Configura variáveis globais
    NOME_P1 = time_p1["nome"]
    CORES_P1 = time_p1["cores"]
    NOME_CPU = time_p2["nome"] # Usamos a var NOME_CPU mesmo se for Player 2 pra facilitar
    CORES_CPU = time_p2["cores"]

    rodando_jogo = True
    confirmando_saida = False # <--- ADICIONE ISSO (Começa desligado)

    reiniciar_rodada()

    # Loop Principal
    rodando_jogo = True
    # 5. LOOP DO JOGO
    # 5. LOOP DO JOGO
    while rodando_jogo:
        
        # --- BLOCÃO 1: EVENTOS (Teclado) ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando_jogo = False; APP_RODANDO = False
            
            if evento.type == pygame.KEYDOWN:
                # O ESC funciona sempre
                if evento.key == pygame.K_ESCAPE:
                    confirmando_saida = not confirmando_saida # Inverte (Abre/Fecha)

                # A) Se a janela de sair estiver ABERTA
                if confirmando_saida:
                    if evento.key == pygame.K_s:
                        rodando_jogo = False # Volta pro Menu
                    elif evento.key == pygame.K_n:
                        confirmando_saida = False # Cancela

                # B) Se a janela estiver FECHADA (Jogo Rolando)
                else: 
                    # --- Comandos de Interface (Enter) ---
                    if estado_animacao == COMEMORACAO and evento.key == pygame.K_RETURN:
                        estado_animacao = RESULTADO
                    elif estado_animacao == FIM_DE_JOGO and evento.key == pygame.K_RETURN:
                        rodando_jogo = False
                    elif estado_animacao == RESULTADO and evento.key == pygame.K_RETURN:
                        if turno == "JOGADOR": turno = "CPU"; reiniciar_rodada()
                        else:
                            if rodada_atual >= max_rodadas and placar_jogador != placar_cpu: estado_animacao = FIM_DE_JOGO
                            else: rodada_atual += 1; turno = "JOGADOR"; reiniciar_rodada()
                    
                    # --- Comandos de Chute (Espaço) ---
                    
                    # 1. CHUTE DO JOGADOR 1 (Atacante P1)
                    # O Goleiro (CPU ou P2) é automático (Sorteio)
                    elif turno == "JOGADOR" and estado_animacao == PREPARANDO and evento.key == pygame.K_SPACE:
                        ang = math.atan2(mira_y - bola_y, mira_x - bola_x)
                        dx = math.cos(ang) * velocidade_bola; dy = math.sin(ang) * velocidade_bola
                        velocidade_goleiro_atual = random.choice([-10, 0, 0, 10]) 
                        estado_animacao = EM_MOVIMENTO
                    
                    # 2. CHUTE DO JOGADOR 2 (MODO PVP)
                    # O Goleiro (P1) é automático (Sorteio) - Ninguém controla goleiro no PVP
                    elif turno == "CPU" and modo_jogo == "PVP" and estado_animacao == PREPARANDO and evento.key == pygame.K_SPACE:
                        ang = math.atan2(mira_y - bola_y, mira_x - bola_x)
                        dx = math.cos(ang) * velocidade_bola; dy = math.sin(ang) * velocidade_bola
                        velocidade_goleiro_atual = random.choice([-10, 0, 0, 10]) 
                        estado_animacao = EM_MOVIMENTO

                    # 3. CHUTE DA CPU (MODO SINGLE PLAYER)
                    # O Goleiro (P1) é MANUAL (Você controla nas setas) -> Velocidade Zero
                    elif turno == "CPU" and modo_jogo == "CPU" and estado_animacao == PREPARANDO and evento.key == pygame.K_SPACE:
                        tx = random.randint(GOL_X+20, GOL_X+GOL_LARGURA-20)
                        ty = random.randint(GOL_Y+20, GOL_Y+GOL_ALTURA-10)
                        if random.random() < 0.1: tx = random.choice([GOL_X-50, GOL_X+GOL_LARGURA+50])
                        cheat_alvo_x, cheat_alvo_y = tx, ty
                        
                        ang = math.atan2(ty - bola_y, tx - bola_x)
                        dx = math.cos(ang) * velocidade_bola; dy = math.sin(ang) * velocidade_bola
                        velocidade_goleiro_atual = 0 # Você defende, então o "automático" é zero
                        estado_animacao = EM_MOVIMENTO


        # --- BLOCÃO 2: LÓGICA E FÍSICA ---
        if not confirmando_saida:
            teclas = pygame.key.get_pressed()
            
            # 1. MIRA (Setas)
            # Funciona para P1 sempre, e para P2 só no PVP
            if estado_animacao == PREPARANDO:
                if (turno == "JOGADOR") or (turno == "CPU" and modo_jogo == "PVP"):
                    if teclas[pygame.K_LEFT]: mira_x -= velocidade_mira
                    if teclas[pygame.K_RIGHT]: mira_x += velocidade_mira
                    if teclas[pygame.K_UP]: mira_y -= velocidade_mira
                    if teclas[pygame.K_DOWN]: mira_y += velocidade_mira

            # 2. MOVIMENTO MANUAL DO GOLEIRO (SÓ NO SINGLE PLAYER)
            # Só funciona se for vez da CPU chutar E o modo for contra CPU
            if turno == "CPU" and modo_jogo == "CPU":
                if teclas[pygame.K_LEFT]: goleiro_x -= velocidade_goleiro
                if teclas[pygame.K_RIGHT]: goleiro_x += velocidade_goleiro
            
            # Limites Goleiro
            if goleiro_x < GOL_X: goleiro_x = GOL_X
            if goleiro_x > GOL_X + GOL_LARGURA - goleiro_largura: 
                goleiro_x = GOL_X + GOL_LARGURA - goleiro_largura

            # 3. FÍSICA (EM MOVIMENTO)
            if estado_animacao == EM_MOVIMENTO:
                bola_x += dx
                bola_y += dy
                
                # MOVIMENTO AUTOMÁTICO DO GOLEIRO
                # Se for PVP, a velocidade foi sorteada. Se for CPU, é 0.
                goleiro_x += velocidade_goleiro_atual
                
                # Limites Goleiro (De novo, para garantir no automático)
                if goleiro_x < GOL_X: goleiro_x = GOL_X
                if goleiro_x > GOL_X + GOL_LARGURA - goleiro_largura: 
                    goleiro_x = GOL_X + GOL_LARGURA - goleiro_largura

                # COLISÕES
                bola_rect = pygame.Rect(bola_x-bola_raio, bola_y-bola_raio, bola_raio*2, bola_raio*2)
                gol_rect = pygame.Rect(goleiro_x, goleiro_y, goleiro_largura, goleiro_altura)
                
                gol = False; defesa = False; fora = False
                
                if bola_rect.colliderect(gol_rect): defesa = True
                elif bola_y < GOL_Y + 60:
                    if GOL_X < bola_x < GOL_X + GOL_LARGURA: gol = True
                    else: fora = True
                
                if gol or defesa or fora:
                    if gol:
                        msg_resultado = "GOL!"
                        if turno == "JOGADOR": placar_jogador += 1
                        else: placar_cpu += 1
                    elif defesa: msg_resultado = "DEFENDEU!"
                    else: msg_resultado = "PRA FORA!"

                    festa = False
                    if (turno=="JOGADOR" and gol) or (turno=="CPU" and defesa):
                        festa = True
                        avatar_festa_x = LARGURA//2 if gol else goleiro_x
                        avatar_festa_y = ALTURA-100 if gol else goleiro_y
                    
                    if festa: estado_animacao = COMEMORACAO; inicio_festa = pygame.time.get_ticks(); confetes = criar_confetes()
                    else: estado_animacao = RESULTADO

            # 4. COMEMORAÇÃO
            if estado_animacao == COMEMORACAO:
                tempo = pygame.time.get_ticks() - inicio_festa
                if tempo > 5000: estado_animacao = RESULTADO
                if teclas[pygame.K_LEFT]: avatar_festa_x -= 10
                if teclas[pygame.K_RIGHT]: avatar_festa_x += 10
                if teclas[pygame.K_UP]: avatar_festa_y -= 10
                if teclas[pygame.K_DOWN]: avatar_festa_y += 10
                for c in confetes:
                    c[1] += c[3]
                    if c[1] > ALTURA: c[1] = -10; c[0] = random.randint(0, LARGURA)


        # --- BLOCÃO 3: DESENHO ---
        TELA.fill(GRAMADO)
        pygame.draw.rect(TELA, LINHAS, (100, 0, LARGURA-200, 250), 3)
        pygame.draw.circle(TELA, LINHAS, (LARGURA//2, 250), 40, 3)
        pygame.draw.rect(TELA, (20, 80, 20), (GOL_X, GOL_Y, GOL_LARGURA, 80))
        pygame.draw.line(TELA, TRAVE_COR, (GOL_X, GOL_Y), (GOL_X, GOL_Y+80), 8)
        pygame.draw.line(TELA, TRAVE_COR, (GOL_X+GOL_LARGURA, GOL_Y), (GOL_X+GOL_LARGURA, GOL_Y+80), 8)
        pygame.draw.line(TELA, TRAVE_COR, (GOL_X, GOL_Y), (GOL_X+GOL_LARGURA, GOL_Y), 8)

        if estado_animacao == COMEMORACAO:
            for c in confetes: pygame.draw.circle(TELA, c[2], (c[0], c[1]), 5)
            desenhar_personagem_listrado(TELA, avatar_festa_x, avatar_festa_y, 60, 40, CORES_P1, NOME_P1)
            txt = fonte.render(msg_resultado, True, TEXTO_COR)
            TELA.blit(txt, (LARGURA//2 - txt.get_width()//2, 150))
            pular = fonte_peq.render("ENTER para pular", True, (255,255,255))
            pygame.draw.rect(TELA, PRETO, (LARGURA//2-100, ALTURA-40, 200, 30))
            TELA.blit(pular, (LARGURA//2 - pular.get_width()//2, ALTURA-35))
        else:
            c_gol = CORES_P1 if turno == "CPU" else CORES_CPU
            n_gol = NOME_P1 if turno == "CPU" else NOME_CPU
            desenhar_personagem_listrado(TELA, goleiro_x, goleiro_y, goleiro_largura, goleiro_altura, c_gol, n_gol)
            pygame.draw.circle(TELA, BOLA_COR, (int(bola_x), int(bola_y)), bola_raio)
            if turno == "CPU" and estado_animacao == EM_MOVIMENTO and modo_jogo == "CPU":
                pygame.draw.circle(TELA, (255,0,255), (cheat_alvo_x, cheat_alvo_y), 15, 3)
            
            # Mostra a mira se for P1 OU se for P2 no modo PVP
            if (turno == "JOGADOR") or (turno == "CPU" and modo_jogo == "PVP"):
                 if estado_animacao == PREPARANDO:
                    pygame.draw.line(TELA, MIRA_COR, (mira_x, mira_y-10), (mira_x, mira_y+10), 3)
                    pygame.draw.line(TELA, MIRA_COR, (mira_x-10, mira_y), (mira_x+10, mira_y), 3)
                    pygame.draw.line(TELA, (255, 255, 255), (bola_x, bola_y), (mira_x, mira_y), 1)

        # Placar e Textos
        placar = fonte_placar.render(f"{NOME_P1} {placar_jogador}  x  {placar_cpu} {NOME_CPU}", True, LINHAS)
        rodada = fonte_peq.render(f"RODADA: {rodada_atual} / 5", True, LINHAS)
        pygame.draw.rect(TELA, PRETO, (LARGURA//2-250, 0, 500, 70))
        TELA.blit(placar, (LARGURA//2 - placar.get_width()//2, 5))
        TELA.blit(rodada, (LARGURA//2 - rodada.get_width()//2, 45))
        aviso = fonte_peq.render("ESC: Menu Inicial", True, (200,200,200))
        TELA.blit(aviso, (10, 10))

        if estado_animacao == PREPARANDO:
            msg = "SUA VEZ" if turno == "JOGADOR" else "DEFENDA"
            if modo_jogo == "PVP" and turno == "CPU": msg = "VEZ DO JOGADOR 2"
            inst = fonte_peq.render(msg, True, TEXTO_COR)
            TELA.blit(inst, (LARGURA//2 - inst.get_width()//2, ALTURA-40))

        if estado_animacao == RESULTADO:
            r_txt = fonte.render(msg_resultado, True, TEXTO_COR)
            pygame.draw.rect(TELA, PRETO, (LARGURA//2-150, ALTURA//2-30, 300, 100))
            TELA.blit(r_txt, (LARGURA//2 - r_txt.get_width()//2, ALTURA//2-20))
            ent = fonte_peq.render("ENTER Continuar", True, LINHAS)
            TELA.blit(ent, (LARGURA//2 - ent.get_width()//2, ALTURA//2+30))

        if estado_animacao == FIM_DE_JOGO:
            s = pygame.Surface((LARGURA,ALTURA)); s.set_alpha(200); s.fill((0,0,0))
            TELA.blit(s, (0,0))
            venc = f"{NOME_P1} CAMPEÃO!" if placar_jogador > placar_cpu else f"VITÓRIA DO {NOME_CPU}"
            v_txt = fonte.render(venc, True, (0,255,0))
            TELA.blit(v_txt, (LARGURA//2 - v_txt.get_width()//2, ALTURA//2))
            f_txt = fonte_peq.render("ENTER: Menu Inicial", True, LINHAS)
            TELA.blit(f_txt, (LARGURA//2 - f_txt.get_width()//2, ALTURA//2+50))

        # --- CAIXA DE CONFIRMAÇÃO ---
        if confirmando_saida:
            overlay = pygame.Surface((LARGURA, ALTURA))
            overlay.set_alpha(150); overlay.fill((0,0,0))
            TELA.blit(overlay, (0,0))
            rect_caixa = pygame.Rect(LARGURA//2 - 200, ALTURA//2 - 75, 400, 150)
            pygame.draw.rect(TELA, (0, 0, 0), rect_caixa)
            pygame.draw.rect(TELA, (255, 255, 255), rect_caixa, 4)
            txt_pergunta = fonte.render("DESEJA SAIR?", True, (255, 50, 50))
            txt_botoes = fonte_peq.render("[S] SIM       [N] NÃO", True, (255, 255, 255))
            TELA.blit(txt_pergunta, (LARGURA//2 - txt_pergunta.get_width()//2, ALTURA//2 - 30))
            TELA.blit(txt_botoes, (LARGURA//2 - txt_botoes.get_width()//2, ALTURA//2 + 30))

        pygame.display.update()
        relogio.tick(60)

pygame.quit()