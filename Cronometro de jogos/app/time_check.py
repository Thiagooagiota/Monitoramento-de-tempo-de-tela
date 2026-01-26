import time
import threading
from collections import defaultdict
import win32gui
import win32process
import psutil

class JanelaTracker:
    def __init__(self):
        # Tempo total acumulado de TODAS as sessões (soma tudo, nunca reseta automaticamente)
        self.tempo_total_acumulado = 0.0

        # Contadores da sessão atual (reseta quando timer zera)
        self.tempo_por_app_sessao = defaultdict(float)
        self.tempo_sessao = 0.0

        self.ultimo_app = None
        self.ultimo_tempo = time.time()
        self.rodando = False
        self.thread = None

    def get_app_atual(self):
        """Retorna o nome do app/processo em foco (foreground window)"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return "Sistema / Desktop"
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            p = psutil.Process(pid)
            return p.name().lower()
        except Exception:
            return "desconhecido"

    def loop(self):
        """Loop principal de monitoramento (roda em thread separada)"""
        while self.rodando:
            app = self.get_app_atual()
            agora = time.time()

            if self.ultimo_app is None:
                self.ultimo_app = app
                self.ultimo_tempo = agora
                time.sleep(0.5)
                continue

            if app != self.ultimo_app:
                delta = agora - self.ultimo_tempo
                # Atualiza sessão atual
                self.tempo_por_app_sessao[self.ultimo_app] += delta
                self.tempo_sessao += delta
                # Atualiza total acumulado (todas sessões)
                self.tempo_total_acumulado += delta
                self.ultimo_app = app
                self.ultimo_tempo = agora

            time.sleep(0.5)

    def iniciar(self):
        """Inicia ou retoma o monitoramento"""
        if self.rodando:
            return  # já está rodando
        self.rodando = True
        self.ultimo_tempo = time.time()
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def parar(self):
        """Para o monitoramento e atualiza o último delta"""
        if not self.rodando:
            return  # já está parado
        agora = time.time()
        if self.ultimo_app:
            delta = agora - self.ultimo_tempo
            self.tempo_por_app_sessao[self.ultimo_app] += delta
            self.tempo_sessao += delta
            self.tempo_total_acumulado += delta
        self.rodando = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)  # timeout para evitar travar
        self.ultimo_app = None
        self.ultimo_tempo = None

    def reset_sessao(self):
        """Reseta APENAS os contadores da sessão atual (relatório por app e tempo da sessão)
           O tempo total acumulado NÃO é afetado"""
        self.parar()  # garante que pare antes de resetar
        self.tempo_por_app_sessao.clear()
        self.tempo_sessao = 0.0
        self.ultimo_app = None
        self.ultimo_tempo = time.time()

    def get_tempo_sessao(self):
        return self.tempo_sessao

    def get_tempo_total_acumulado(self):
        return self.tempo_total_acumulado

    def get_relatorio_sessao(self):
        return dict(sorted(self.tempo_por_app_sessao.items(), key=lambda x: x[1], reverse=True))