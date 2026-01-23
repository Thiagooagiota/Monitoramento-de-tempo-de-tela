import time
from pygame import mixer
from tkinter import messagebox

parar = False
atual = 60
ativo = False
rodando = False

def contador(tempo, som):
    global parar, atual, ativo, rodando
    parar = False
    ativo = True
    rodando = True

    timer = tempo

    while timer > 0 and not parar:
        time.sleep(1)
        timer -= 1
        atual = timer

    if parar:
        parar = False
        timer += 1
        atual = timer
        return

    if som == None:
        pass
    else:
        mixer.init()
        mixer.music.load(som)
        mixer.music.set_volume(1.0)
        mixer.music.play()
        
    messagebox.showinfo("notificação", "o tempo acabou")


def parar_contador():
    """Interrompe o contador em execução."""
    global parar, ativo, rodando
    parar = True
    rodando = False


if __name__ == "__main__":
    # TESTE MANUAL — rode este arquivo sozinho para ver se o som toca:
    from pathlib import Path

    som = Path("assets/sons/Sino.mp3")  # ajuste para o seu caminho real
    contador(5, som)  # conta 5 segundos
