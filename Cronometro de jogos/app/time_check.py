import time
import threading
from collections import defaultdict
import win32gui
import win32process
import psutil

class JanelaTracker:
    def __init__(self):
        self.tempo_por_app = defaultdict(float)
        self.ultimo_app = None
        self.ultimo_tempo = time.time()
        self.rodando = False
        self.thread = None
        
        self.tempo_total = 0.0

    def get_app_atual(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return "Sistema / Desktop"
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            p = psutil.Process(pid)
            return p.name().lower()
        except:
            return "desconhecido"

    def loop(self):
        while self.rodando:
            app = self.get_app_atual()
            agora = time.time()

            if self.ultimo_app is None:
                self.ultimo_app = app
                self.ultimo_tempo = agora
                time.sleep(0.5)
                continue

            if app != self.ultimo_app:
                self.tempo_por_app[self.ultimo_app] += agora - self.ultimo_tempo
                self.ultimo_app = app
                self.ultimo_tempo = agora

            time.sleep(0.5)


    def iniciar(self):
        if self.rodando:
            return

        self.rodando = True
        self.ultimo_tempo = time.time()
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def parar(self):
        if not self.rodando:
            return

        agora = time.time()

        # Soma tempo do último app
        if self.ultimo_app:
            delta = agora - self.ultimo_tempo
            self.tempo_por_app[self.ultimo_app] += delta
            self.tempo_total += delta  # ⬅️ soma no total da sessão

        self.rodando = False

        if self.thread and self.thread.is_alive():
            self.thread.join()

        self.ultimo_app = None
        self.ultimo_tempo = None
        


    def get_tempo_total(self):
        total = int(self.tempo_total)
        m, s = divmod(total, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"




    def get_relatorio(self):
        return dict(sorted(self.tempo_por_app.items(), key=lambda x: x[1], reverse=True))


# Uso dentro da sua aplicação:
# tracker = JanelaTracker()
# tracker.iniciar()
# ...
# ao fechar: tracker.parar()
# print(tracker.get_relatorio())