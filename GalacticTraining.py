import pygame, sys, random

ANCHO = 850
ALTO = 480

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('GALACTIC TRAINING')
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("Fira code", 30)

# fondo
fondo = pygame.image.load('assets/fondo.jpg').convert_alpha()
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

# surface game over
srfcGameOver = pygame.Surface((ANCHO, 230), pygame.SRCALPHA) #pygame.SRCALPHA: perimta la opacidad

btnPlayAgain = pygame.Surface((124, 40))
btnPlayAgainRect = btnPlayAgain.get_rect(x=(ANCHO / 2 - 62), y=(srfcGameOver.get_size()[1] + 60))

# eventos de tiempo
TIEMPO_SEGUNDO = pygame.USEREVENT + 1
TIEMPO_RECARGA = pygame.USEREVENT + 2
TIEMPO_POWERUP = pygame.USEREVENT + 3

# sonidos
soundLaserShot = pygame.mixer.Sound("assets/soundLaserShot.mp3")
soundLaserShot.set_volume(0.2)
soundReload = pygame.mixer.Sound("assets/soundReload.mp3")
soundReload.set_volume(0.4)
soundGameOver = pygame.mixer.Sound("assets/soundGameOver.mp3")
soundGameOver.set_volume(0.2)
soundBackground = pygame.mixer.music
soundBackground.load("assets/soundBackground.mp3")
soundBackground.set_volume(0.4)
soundBackground.play(-1)

# ------ CLASES
class Identidad():
    def __init__(self, imagen):
        pygame.sprite.Sprite.__init__(self)
        self.imagen = pygame.image.load(imagen).convert_alpha()
        self.rect = self.imagen.get_rect()

    def dibujar(self):
        pantalla.blit(self.imagen, self.rect)


class Juego():
    def __init__(self):
        self.gameOver = False
        
        self.puntosJugador = 0
        self.scoreMultiplier = 1
        self.mejorPuntaje = 0
        
        self.tiempo = [0, 30]  # min, seg
        self.ceroIzq = ""  # para que el tiempo se vea "0:03" y no "0:3" 

        self.municion = 20
        self.recargando = False
        self.timeRecarga = ""
        self.imgBala = pygame.image.load("assets/bala.png").convert_alpha() # imagen de bala al recargar
        self.imgBala = pygame.transform.scale(self.imgBala, (10, 48))
        
        self.timePowerActive = False
        self.timeNextPower = 5

        pygame.time.set_timer(TIEMPO_SEGUNDO, 1000)
        pygame.time.set_timer(TIEMPO_RECARGA, 0)


class Mira(Identidad):
    def __init__(self, imagen):
        super().__init__(imagen)

    #La mira mueve segun la posicion del mouse
    def mover(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y


class Nave(Identidad):
    # posicion (x, y) de las 6 naves
    posNaveX = [225, 
                50, 
                (ANCHO-250), 
                100, 
                (ANCHO/2-100), 
                (ANCHO-300)]
    posNaveY = [100, 
                210, 
                210, 
                ALTO - 90, 
                270, 
                ALTO - 90]
    naveList = []

    def __init__(self, imagen, x, y):
        super().__init__(imagen)
        self.imagen = pygame.transform.scale(self.imagen, (200, 70))
        
        self.naveVel = 0
        self.rect.x = x
        self.rect.y = y
        
    #Movimiento de la nave horizontal y vertical
    def mover(self, index):
        if index == 0:
            if nave.rect.x <= 225: self.naveVel = 2
            elif nave.rect.x >= 425: self.naveVel = -2

            self.rect.move_ip(self.naveVel, 0)

        if index == 4:
            if nave.rect.y <= 270: self.naveVel = 1
            elif nave.rect.y >= 370: self.naveVel = -1

            self.rect.move_ip(0, self.naveVel)


class Alien(Identidad):
    numNave = 0  # variable estatica, numero de nave donde se ubica el alien

    def __init__(self, imagen, pxlsX):
        super().__init__(imagen)
        self.imagen = pygame.transform.scale(self.imagen, (85, 130))
        
        # Se hace mas pequeño el rect (hitbox) del alien
        self.surfaceImg = pygame.Surface((85, 85))
        self.surfaceImg.blit(self.imagen, (0, 0))
        self.rect = self.surfaceImg.get_rect()

        self.puntos = 0
        self.vida = 0

        self.pixelsX = pxlsX # Cantidad de pixels para que quede en el centro de la nave

    # Cambia aleatoriamente a una de las 6 naves
    @classmethod
    def cambiarNave(cls):
        anteriorNumNave = Alien.numNave
        #Se repite el ciclo si al cambiar de nave queda en la misma
        while anteriorNumNave == Alien.numNave:
            Alien.numNave = random.randint(0, 5)

    # Para que el alien se mueva a la misma posicion de una nave
    def mover(self):
        self.rect.x = Nave.naveList[Alien.numNave].rect.x + self.pixelsX
        self.rect.y = Nave.naveList[Alien.numNave].rect.y - 80

class Alien1(Alien):
    def __init__(self):
        super().__init__("assets/alien1.png", 55)
        self.puntos = 10
        self.vida = 1

class Alien2(Alien):
    def __init__(self):
        super().__init__("assets/alien2.png", 70)
        self.puntos = 20
        self.vida = 2

class PowerUp(Identidad):
    posPowerX = [180,
                 ANCHO-225,
                 ANCHO/2-130,
                 ANCHO/2+85,
                 80,
                 ANCHO-125]
    posPowerY = [50,
                 50,
                 ALTO/2-50,
                 ALTO/2-50,
                 ALTO-160,
                 ALTO-160]
    tipoPowerUp = 0

    def __init__(self, imagen):
        super().__init__(imagen)
        self.imagen = pygame.transform.scale(self.imagen, (45, 45))
        
        # Se hace mas pequeño el rect (hitbox) del powerUp
        self.surfaceImg = pygame.Surface((45, 45))
        self.surfaceImg.blit(self.imagen, (0, 0))
        self.rect = self.surfaceImg.get_rect()
        
    def mover(self, x, y):
        self.rect.x = x
        self.rect.y = y
        
    # Reinicia el tiempo del isiguiente powerUp luego de que se inactive o se dispare a él
    def inactivatePower():
        juego.timePowerActive = False
        juego.timeNextPower = 5
        pygame.time.set_timer(TIEMPO_POWERUP, 0)
        

class PowerAmmo(PowerUp):
    def __init__(self):
        super().__init__("assets/powerAmmo.png")
        
    # poder que obtiene el juegador si le dispra al powerUp
    def getPower(self):
        juego.municion += 10

class PowerPointsx2(PowerUp):
    def __init__(self):
        super().__init__("assets/powerPointsx2.png")
    
    def getPower(self):
        juego.scoreMultiplier = 2
        
class PowerTime(PowerUp):
    def __init__(self):
        super().__init__("assets/powerTime.png")
        
    def getPower(self):
        juego.tiempo[1] += 10
        
        
# ------ INICIALIZACION DE IDENTIDADES
# mira
mira = Mira('assets/mira.png')

# naves
for j in range(6):
    nuevaNave = Nave("assets/nave.png", Nave.posNaveX[j], Nave.posNaveY[j])
    Nave.naveList.append(nuevaNave)

# alien
alien = Alien1()
Alien.cambiarNave()
alien.mover()
#pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0)))

# powerup
power = PowerAmmo()

# Juego, inicializar todas las variables del juego
juego = Juego()


while True:
    pantalla.blit(fondo, (0, 0))

    # ------ EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # "Disparo"
        if not juego.gameOver and not juego.recargando and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                juego.municion -= 1
                soundLaserShot.play()

                if alien.rect.collidepoint(event.pos):
                    alien.vida -= 1

                    if alien.vida == 0:
                        juego.puntosJugador += (alien.puntos * juego.scoreMultiplier)

                        #si es 1, sera alien1. Si es 2, sera alien2
                        alien = (Alien1() if random.randint(1, 2) == 1 else Alien2())
                        Alien.cambiarNave()
                        alien.mover()

            if event.button == pygame.BUTTON_RIGHT:
                juego.municion -= 1
                soundLaserShot.play()
                
                if power.rect.collidepoint(event.pos):
                    PowerUp.inactivatePower()
                    power.getPower()
                    
        # Presionar boton volver a jugar
        if juego.gameOver and event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT and btnPlayAgainRect.collidepoint(event.pos):
                soundGameOver.stop()
                soundBackground.play()
                mejorPuntaje = juego.mejorPuntaje
                
                if juego.puntosJugador > mejorPuntaje: mejorPuntaje = juego.puntosJugador
                    
                juego = Juego() # Se reinician todos los valores del juego
                juego.mejorPuntaje = mejorPuntaje
                Alien.cambiarNave()
                vidaAlien = alien.vida
                
        # Tiempo
        if event.type == TIEMPO_SEGUNDO:
            if juego.timeNextPower != 0:
                juego.timeNextPower -= 1
            
            if juego.tiempo[0] >= 1 and juego.tiempo[1] == 0:
                juego.tiempo[0] -= 1
                juego.tiempo[1] = 59
            else:
                juego.tiempo[1] -= 1
            
            if juego.tiempo[0] == 0 and juego.tiempo[1] == 0:
                soundBackground.stop()
                soundGameOver.play()
                pygame.time.set_timer(TIEMPO_SEGUNDO, 0)
                juego.gameOver = True

        # Segundos de recarga, aparecen en el centro de la pantalla al recargar
        if event.type == TIEMPO_RECARGA:
            juego.timeRecarga = str(int(juego.timeRecarga) - 1)

        # tiempo powerUp, dura 3 segundas y se llama, cada 5 segundos
        if event.type == TIEMPO_POWERUP:
            PowerUp.inactivatePower()

    #------- FORMATEO DE TIEMPO
    juego.ceroIzq = ("0" if juego.tiempo[1] < 10 else "")
    
    if juego.tiempo[1] > 59:
        juego.tiempo[1] -= 60
        juego.tiempo[0] +=1
    
    # ------ CONDICIONES DE MUNICION / RECARGA
    # Cuando la municion llega a 0
    if juego.municion == 0 and juego.recargando == False:
        juego.recargando = True
        juego.timeRecarga = "3"
        soundReload.play()

        pygame.time.set_timer(TIEMPO_RECARGA, 1000)

    # Cuando se termina de recargar
    if juego.timeRecarga == "0":
        juego.municion = 20
        juego.recargando = False
        juego.timeRecarga = ""

        pygame.time.set_timer(TIEMPO_RECARGA, 0)
        
    # ------ CONDICIONES DE POWERUP
    # Crea un powerUp y la ubicacion de manera aleatoria
    if juego.timeNextPower == 0 and juego.timePowerActive == False:
        juego.scoreMultiplier = 1
        posPower = random.randint(0,5)
        anteriorTipoPower = PowerUp.tipoPowerUp
        
        #Se repite el ciclo si al vuelve a salir el mismo poder anterior
        while anteriorTipoPower == PowerUp.tipoPowerUp:
            PowerUp.tipoPowerUp = random.randint(0, 2)
            
        match PowerUp.tipoPowerUp:
            case 0: power = PowerAmmo()
            case 1: power = PowerPointsx2()
            case 2: power = PowerTime()
                
        power.mover(PowerUp.posPowerX[posPower], PowerUp.posPowerY[posPower])
            
        juego.timePowerActive = True
        pygame.time.set_timer(TIEMPO_POWERUP, 2000)
        
    
    # ------ DIBUJADO DE IDENTIDADES
    alien.dibujar()

    #naves
    for i, nave in enumerate(Nave.naveList):
        nave.mover(i)
        nave.dibujar()
        alien.mover()
        
    #Powerup
    if juego.timePowerActive == True:
        power.dibujar()
        
    # Texto
    puntos = fuente.render(f"Score: {str(juego.puntosJugador)}", True, "white")
    mejorPuntaje = fuente.render(f"Best score: {str(juego.mejorPuntaje)}", True, "white")
    txtTiempo = fuente.render(f"Time: {str(juego.tiempo[0])}:{juego.ceroIzq}{str(juego.tiempo[1])}", True, "white")
    txtMunicion = fuente.render(f"Ammo: {juego.municion}", True, "white")
    txtTimeRecarga = pygame.font.SysFont("Fira Code", 85).render(f"{juego.timeRecarga}", True, "red")
    txtGameOver = pygame.font.SysFont("Fira Code", 100).render("Game Over", True, "red")
    txtPuntajeTotal = pygame.font.SysFont("Fira Code", 60).render(f"Score: {juego.puntosJugador}", True, "white")
    txtPlayAgain = fuente.render("Play Again", True, "black")

    pantalla.blit(puntos, (10, 10))
    pantalla.blit(mejorPuntaje, (10, 40))
    pantalla.blit(txtTiempo, (10, 70))
    pantalla.blit(txtMunicion, (10, 100))
    pantalla.blit(txtTimeRecarga, (ANCHO / 2 - 50, ALTO / 2 - 60))
    btnPlayAgain.blit(txtPlayAgain, (10, 10))
    srfcGameOver.blit(txtGameOver, (ANCHO / 2 - 185, 20))
    srfcGameOver.blit(txtPuntajeTotal, (ANCHO / 2 - 100, 100))

    # imagenes de balas que aparecen al recargar
    if juego.recargando:
        if int(juego.timeRecarga) <= 3:
            pantalla.blit(juego.imgBala, (ANCHO / 2, ALTO / 2 - 60))
        if int(juego.timeRecarga) <= 2:
            pantalla.blit(juego.imgBala, (ANCHO / 2 + 15, ALTO / 2 - 60))
        if int(juego.timeRecarga) <= 1:
            pantalla.blit(juego.imgBala, (ANCHO / 2 + 30, ALTO / 2 - 60))

    # game over
    if juego.gameOver:
        pantalla.blit(srfcGameOver, (0, 125))
        srfcGameOver.fill((0, 0, 0, 100)) # opacidad: 100 (0=0%, 255=100%)
        pantalla.blit(btnPlayAgain, btnPlayAgainRect)
        btnPlayAgain.fill((255, 255, 255))
    
    # Mira
    mouse_pos = pygame.mouse.get_pos()
    mira.mover(mouse_pos[0], mouse_pos[1])
    mira.dibujar()
    
    pygame.display.update()
    reloj.tick(60)