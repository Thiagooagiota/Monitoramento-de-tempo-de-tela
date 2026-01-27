import customtkinter as ctk
from tkinter import messagebox
try:
    from pygame import mixer
except ImportError:
    mixer = None
from pathlib import Path
import json
import time_check

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BASE_DIR = Path(__file__).resolve().parents[1]
sons = BASE_DIR / "assets" / "sons"
CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_SETTINGS = {
    "tempo_de_jogo": 25,
    "tempo_pausa": 15,
    "auto_pausa": False,
    "modo_atual": "tempo_de_jogo",
    "som_alarme": "Sino",
    "som_tictac": "Nenhum"
}

def carregar_config():
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                dados = json.load(f)
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in dados:
                        dados[key] = value
                return dados
        return DEFAULT_SETTINGS.copy()
    except Exception as e:
        print(f"Erro ao carregar config: {e}")
        return DEFAULT_SETTINGS.copy()

carregar = carregar_config()
DEFAULT_SETTINGS.update(carregar)

class FocoView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#0f1113")
        self.pack(fill="both", expand=True)
        self.controller = controller

        self.em_execucao = False
        self.id_temporizador = None
        self.dialogo_configuracoes = None
        self.janela_relatorio = None
        self.tracker = time_check.JanelaTracker()

        self.state_vars = {
            "tempo_de_jogo": ctk.IntVar(value=DEFAULT_SETTINGS["tempo_de_jogo"]),
            "tempo_pausa": ctk.IntVar(value=DEFAULT_SETTINGS["tempo_pausa"]),
            "modo_atual": ctk.StringVar(value=DEFAULT_SETTINGS["modo_atual"]),
            "auto_pausa": ctk.BooleanVar(value=DEFAULT_SETTINGS["auto_pausa"]),
            "som_alarme": ctk.StringVar(value=DEFAULT_SETTINGS["som_alarme"]),
            "som_tictac": ctk.StringVar(value=DEFAULT_SETTINGS["som_tictac"])
        }

        self.segundos = 0
        self.segundos_iniciais = 0

        self.configurar_interface()
        self.atualizar_selecao_modo()

    def configurar_interface(self):
        barra_superior = ctk.CTkFrame(self, height=60, fg_color="transparent")
        barra_superior.pack(fill="x", padx=20, pady=(10, 20))
        barra_superior.columnconfigure((0,1), weight=1)

        btn_config = ctk.CTkButton(barra_superior, text="Configurações", command=self.abrir_configuracoes,
                                   font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2e7bf6", hover_color="#1e5bb4",
                                   corner_radius=10, width=150)
        btn_config.grid(row=0, column=0, padx=0, pady=10, sticky="w")

        btn_relatorio = ctk.CTkButton(barra_superior, text="Relatório", command=self.abrir_relatorio,
                                   font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2e7bf6", hover_color="#1e5bb4",
                                   corner_radius=10, width=150)
        btn_relatorio.grid(row=0, column=1, padx=0, pady=10, sticky="e")

        container_principal = ctk.CTkFrame(self, fg_color="transparent")
        container_principal.pack(fill="both", expand=True, padx=20, pady=10)
        container_principal.grid_columnconfigure(0, weight=1)
        container_principal.grid_rowconfigure(0, weight=1)

        self.painel = ctk.CTkFrame(container_principal, fg_color="#111316", corner_radius=12,
                                   border_width=1, border_color="#2a2d2e")
        self.painel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.criar_painel_esquerdo()

    def abrir_configuracoes(self):
        if self.dialogo_configuracoes and self.dialogo_configuracoes.winfo_exists():
            self.dialogo_configuracoes.focus()
        else:
            self.dialogo_configuracoes = ConfiguracoesDialog(self, self.state_vars)

    def abrir_relatorio(self):
        if self.janela_relatorio and self.janela_relatorio.winfo_exists():
            self.janela_relatorio.focus()
        else:
            self.janela_relatorio = RelatorioDialog(self)
        

    def criar_painel_esquerdo(self):
        self.painel.grid_rowconfigure(2, weight=1)
        self.painel.grid_columnconfigure(0, weight=1)
        self.painel.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.painel, text="Foco Total", font=ctk.CTkFont(size=28, weight="bold")).grid(
            row=0, column=0, columnspan=2, pady=(20, 15), sticky="n")

        frame_modos = ctk.CTkFrame(self.painel, fg_color="transparent")
        frame_modos.grid(row=1, column=0, columnspan=2, pady=10)

        self.btn_tempo_de_jogo = self.criar_botao_modo(frame_modos, "tempo_de_jogo", 0)
        self.btn_pausa = self.criar_botao_modo(frame_modos, "Pausa", 2)

        self.state_vars["modo_atual"].trace_add("write", self.atualizar_selecao_modo)

        container_temporizador = ctk.CTkFrame(self.painel, fg_color="transparent")
        container_temporizador.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=(10, 20))
        container_temporizador.grid_columnconfigure(0, weight=1)
        container_temporizador.grid_rowconfigure(0, weight=1)

        self.lbl_tempo = ctk.CTkLabel(container_temporizador, text="25:00", font=ctk.CTkFont(size=72, weight="bold"),
                                      text_color="white")
        self.lbl_tempo.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        controle_frame = ctk.CTkFrame(container_temporizador, fg_color="transparent")
        controle_frame.grid(row=1, column=0, sticky="n", pady=(20, 0))

        self.btn_iniciar = ctk.CTkButton(controle_frame, text="Iniciar", command=self.alternar_temporizador,
                                         font=ctk.CTkFont(size=18, weight="bold"), height=50, width=160,
                                         fg_color="#2e7bf6", hover_color="#1e5bb4", corner_radius=12)
        self.btn_iniciar.pack(side="left", padx=(0, 10))

        btn_restaurar = ctk.CTkButton(controle_frame, text="Restaurar", command=self.restaurar_tempo,
                                      font=ctk.CTkFont(size=12, weight="bold"), height=50, width=80,
                                      fg_color="#363636", hover_color="#4a4a4a", corner_radius=12)
        btn_restaurar.pack(side="left")

    def criar_botao_modo(self, pai, texto, coluna):
        btn = ctk.CTkButton(pai, text=texto, command=lambda t=texto: self.trocar_modo(t),
                            font=ctk.CTkFont(size=15), height=30, width=120, fg_color="#2a2d2e",
                            text_color="#9aa0a6", hover_color="#3c4146")
        btn.grid(row=0, column=coluna, padx=5)
        return btn

    def atualizar_selecao_modo(self, *args):
        for btn in [self.btn_tempo_de_jogo, self.btn_pausa]:
            btn.configure(fg_color="#2a2d2e", text_color="#9aa0a6")

        modo = self.state_vars["modo_atual"].get()
        if modo == "tempo_de_jogo":
            self.btn_tempo_de_jogo.configure(fg_color="#2e7bf6", text_color="white")
            novo_tempo = self.state_vars["tempo_de_jogo"].get()
        elif modo == "Pausa":
            self.btn_pausa.configure(fg_color="#2e7bf6", text_color="white")
            novo_tempo = self.state_vars["tempo_pausa"].get()
        else:
            novo_tempo = 25

        self.segundos_iniciais = novo_tempo * 60
        if not self.em_execucao:
            self.segundos = self.segundos_iniciais
            self.atualizar_exibicao_temporizador()

        self.btn_iniciar.configure(text="Pausar" if self.em_execucao else "Iniciar")

    def trocar_modo(self, modo):
        if self.em_execucao:
            return
        self.state_vars["modo_atual"].set(modo)

    def formatar_tempo(self, segundos):
        m, s = divmod(segundos, 60)
        return f"{m:02d}:{s:02d}"

    def atualizar_exibicao_temporizador(self):
        self.lbl_tempo.configure(text=self.formatar_tempo(self.segundos))
        if self.em_execucao and self.segundos > 0:
            self.id_temporizador = self.after(1000, self.tick_temporizador)

    def tick_temporizador(self):
        if not self.em_execucao or self.segundos <= 0:
            return

        if self.state_vars["som_tictac"].get() == "Padrão":
            try:
                import winsound
                winsound.Beep(800, 50)
            except:
                pass

        self.segundos -= 1
        self.atualizar_exibicao_temporizador()

        if self.segundos == 0:
            modo = self.state_vars["modo_atual"].get()
            if modo == "tempo_de_jogo":
                self.tracker.parar()

                tempo_sessao = self.tracker.get_tempo_sessao()
                tempo_formatado = f"{int(tempo_sessao // 60):02d}:{int(tempo_sessao % 60):02d}"
                relatorio = self.tracker.get_relatorio_sessao()

                total_acumulado = self.tracker.get_tempo_total_acumulado()
                total_formatado = f"{int(total_acumulado // 3600):02d}:{int((total_acumulado % 3600) // 60):02d}:{int(total_acumulado % 60):02d}"

                print(f"\nSessão finalizada!")
                print(f"Tempo total da sessão atual: {tempo_formatado}")
                print("RELATÓRIO DA SESSÃO (tempo por app):")
                if relatorio:
                    for app, tempo in sorted(relatorio.items(), key=lambda x: x[1], reverse=True):
                        print(f"{app}: {tempo:.1f}s ({tempo / 60:.1f} min)")
                else:
                    print("Nenhum app detectado nesta sessão.")

                print(f"Tempo total acumulado (todas as sessões): {total_formatado}")

                # Reseta a sessão atual para o próximo ciclo ser independente
                self.tracker.reset_sessao()

            if self.state_vars["som_alarme"].get() == "Sino":
                self.bell(sons / "Sino.mp3")

            if modo == "tempo_de_jogo":
                NotificacaoDialog(self)

            self.em_execucao = False
            self.btn_iniciar.configure(text="Iniciar")

            if self.state_vars["auto_pausa"].get() and modo == "tempo_de_jogo":
                self.after(1000, self.alternar_proximo_modo_e_iniciar)

    def bell(self, caminho_som):
        try:
            if mixer:
                mixer.init()
                if caminho_som.exists():
                    mixer.music.load(str(caminho_som))
                    mixer.music.play()
                else:
                    raise FileNotFoundError
            else:
                import winsound
                winsound.Beep(1000, 500)
        except Exception as e:
            print(f"Erro ao tocar som: {e}")
            try:
                import winsound
                winsound.Beep(1000, 500)
            except:
                pass

    def alternar_temporizador(self):
        modo = self.state_vars["modo_atual"].get()

        if self.em_execucao:
            # Pausar
            self.em_execucao = False
            if self.id_temporizador:
                self.after_cancel(self.id_temporizador)
            self.btn_iniciar.configure(text="Iniciar")
            if modo == "tempo_de_jogo":
                self.tracker.parar()  # Garante que tracker pare quando pausa
        else:
            # Iniciar
            self.em_execucao = True
            self.btn_iniciar.configure(text="Pausar")
            if modo == "tempo_de_jogo":
                self.tracker.iniciar()  # Só inicia/retoma quando usuário clica "Iniciar"
            self.atualizar_exibicao_temporizador()

    def alternar_proximo_modo_e_iniciar(self):
        if self.em_execucao:
            return
        modo = self.state_vars["modo_atual"].get()
        proximo = "Pausa" if modo == "tempo_de_jogo" else "tempo_de_jogo"
        self.state_vars["modo_atual"].set(proximo)
        if self.state_vars["auto_pausa"].get():
            self.alternar_temporizador()

    def restaurar_tempo(self):
        if not self.em_execucao:
            self.segundos = self.segundos_iniciais
            self.atualizar_exibicao_temporizador()
            print(f"Tempo restaurado para {self.segundos_iniciais // 60} minutos")
            # Tracker NÃO reseta aqui (continua se rodando, ou espera "Iniciar")

    def destroy(self):
        if self.id_temporizador:
            self.after_cancel(self.id_temporizador)
        super().destroy()

class ConfiguracoesDialog(ctk.CTkToplevel):
    def __init__(self, parent, state_vars):
        super().__init__(parent)
        self.title("Configurações")
        self.geometry("500x450")
        self.transient(parent)
        self.focus_set()
        self.grab_set()
        self.state_vars = state_vars

        self.tempo_de_jogo_var = ctk.StringVar(value=str(state_vars["tempo_de_jogo"].get()))
        self.tempo_pausa_var = ctk.StringVar(value=str(state_vars["tempo_pausa"].get()))
        self.som_alarme_var = ctk.StringVar(value=state_vars["som_alarme"].get())
        self.som_tictac_var = ctk.StringVar(value=state_vars["som_tictac"].get())
        self.auto_pausa_var = ctk.BooleanVar(value=state_vars["auto_pausa"].get())

        self.criar_widgets_configuracoes()
        self.resizable(False, False)

    def criar_widgets_configuracoes(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        row = 0
        ctk.CTkLabel(content_frame, text=" TEMPORIZADOR", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=row, column=0, columnspan=2, pady=(0, 10), sticky="w")
        row += 1

        ctk.CTkLabel(content_frame, text="Tempo (minutos)", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 5))
        row += 1

        ctk.CTkLabel(content_frame, text="tempo_de_jogo (min):").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(content_frame, textvariable=self.tempo_de_jogo_var).grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        row += 1

        ctk.CTkLabel(content_frame, text=" pausa (min):").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(content_frame, textvariable=self.tempo_pausa_var).grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        row += 1

        ctk.CTkLabel(content_frame, text="Pausas automáticas:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.switch_auto_pausa = ctk.CTkSwitch(content_frame, text="", variable=self.auto_pausa_var)
        self.switch_auto_pausa.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        row += 1

        ctk.CTkFrame(content_frame, height=2, fg_color="#2a2d2e").grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1

        ctk.CTkLabel(content_frame, text="🔊 SOM", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=row, column=0, columnspan=2, pady=(5, 10), sticky="w")
        row += 1

        ctk.CTkLabel(content_frame, text="Som de alarme:").grid(row=row, column=0, padx=10, pady=8, sticky="w")
        self.option_som = ctk.CTkOptionMenu(content_frame, values=["Sino", "Nenhum"], width=150, variable=self.som_alarme_var)
        self.option_som.grid(row=row, column=1, padx=10, pady=8, sticky="e")
        row += 1

        ctk.CTkLabel(content_frame, text="Som de tique-taque:").grid(row=row, column=0, padx=10, pady=8, sticky="w")
        self.option_tictac = ctk.CTkOptionMenu(content_frame, values=["Nenhum", "Padrão"], width=150, variable=self.som_tictac_var)
        self.option_tictac.grid(row=row, column=1, padx=10, pady=8, sticky="e")

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        btn_redefinir = ctk.CTkButton(button_frame, text="Redefinir", command=self.fechar_e_avisar_resetar,
                                      font=ctk.CTkFont(size=16, weight="bold"), fg_color="#3c4146", hover_color="#52575c")
        btn_redefinir.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        btn_confirmar = ctk.CTkButton(button_frame, text="Confirmar", command=self.fechar_e_avisar_confirmar,
                                      font=ctk.CTkFont(size=16, weight="bold"), fg_color="#2e7bf6", hover_color="#1e5bb4")
        btn_confirmar.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    def fechar_e_avisar_confirmar(self):
        try:
            foco = int(self.tempo_de_jogo_var.get())
            pausa = int(self.tempo_pausa_var.get())
            if foco < 1 or pausa < 1:
                messagebox.showerror("Erro", "Tempos devem ser maiores que 0")
                return

            DEFAULT_SETTINGS.update({
                "tempo_de_jogo": foco,
                "tempo_pausa": pausa,
                "auto_pausa": self.auto_pausa_var.get(),
                "som_alarme": self.som_alarme_var.get(),
                "som_tictac": self.som_tictac_var.get()
            })

            for k, v in DEFAULT_SETTINGS.items():
                if k in self.state_vars:
                    self.state_vars[k].set(v)

            self.master.atualizar_selecao_modo()

            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Sucesso", "Configurações salvas!")
            self.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Digite números válidos")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def fechar_e_avisar_resetar(self):
        if messagebox.askyesno("Confirmar", "Restaurar configurações padrão?"):
            self.tempo_de_jogo_var.set("25")
            self.tempo_pausa_var.set("15")
            self.auto_pausa_var.set(False)
            self.som_alarme_var.set("Sino")
            self.som_tictac_var.set("Nenhum")
            if hasattr(self, 'switch_auto_pausa'):
                self.switch_auto_pausa.deselect()
            if hasattr(self, 'option_som'):
                self.option_som.set("Sino")
            if hasattr(self, 'option_tictac'):
                self.option_tictac.set("Nenhum")

class NotificacaoDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Tempo limite atingido")
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"300x150+{sw-320}+{sh-200}")
        self.transient(parent)
        self.focus_set()
        self.grab_set()

        ctk.CTkLabel(self, text="Tempo limite atingido!", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=20, pady=10)

        self.entry_minutos = ctk.CTkEntry(self, placeholder_text="+ minutos", width=100)
        self.entry_minutos.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        btn_pausa = ctk.CTkButton(self, text="Ir para pausa", command=self.ir_para_pausa)
        btn_pausa.grid(row=2, column=0, padx=20, pady=10, sticky="e")

        btn_add = ctk.CTkButton(self, text="Adicionar tempo", command=self.adicionar_tempo)
        btn_add.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    def ir_para_pausa(self):
        self.parent.state_vars["modo_atual"].set("Pausa")
        self.parent.em_execucao = False
        self.parent.alternar_temporizador()
        self.destroy()

    def adicionar_tempo(self):
        try:
            mins = int(self.entry_minutos.get())
            if mins > 0:
                self.parent.segundos += mins * 60
                self.parent.em_execucao = True
                self.parent.btn_iniciar.configure(text="Pausar")
                self.parent.atualizar_exibicao_temporizador()
                # Tracker continua (não reseta sessão — tempo extra soma na sessão atual)
                if not self.parent.tracker.rodando:
                    self.parent.tracker.iniciar()
        except ValueError:
            pass
        self.destroy()



class RelatorioDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Relatório de Uso do Dia")
        self.geometry("500x450")
        self.transient(parent)
        self.focus_set()
        self.grab_set()

        # título da janela
        self.titulo = ctk.CTkLabel(self, text="Relatório de Uso", font=ctk.CTkFont(size=16, weight="bold"))
        self.titulo.pack(padx=20, pady=(10))
        
        self.frame_relatorio = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_relatorio.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        
        # Frame do topo da Tabela
        self.frame_header = ctk.CTkFrame(self.frame_relatorio, fg_color="transparent")
        self.frame_header.pack(fill="x")
        
        self.frame_header.columnconfigure((0,1,2), weight=1)
        
        self.aplicacao_lbl = ctk.CTkLabel(self.frame_header, text="App", font=ctk.CTkFont(size=14, weight="bold"))
        self.aplicacao_lbl.grid(row=0, column=0)

        self.tempo_de_uso_lbl = ctk.CTkLabel(self.frame_header, text="Tempo de uso", font=ctk.CTkFont(size=14, weight="bold"))
        self.tempo_de_uso_lbl.grid(row=0, column=1)
        
        self.data_lbl = ctk.CTkLabel(self.frame_header, text="Data", font=ctk.CTkFont(size=14, weight="bold"))
        self.data_lbl.grid(row=0, column=2)
        
        # Frame dos dados
        self.frame_dados = ctk.CTkScrollableFrame(self.frame_relatorio)
        self.frame_dados.pack(fill="both", expand=True)
        
        btn_ver_mais = ctk.CTkButton(self.frame_relatorio, 
                                     text="Ver mais",
                                     font=ctk.CTkFont(size=14, weight="bold"), 
                                     fg_color="#2e7bf6", 
                                     hover_color="#1e5bb4",
                                     corner_radius=10, 
                                     width=150,
                                     command=self.gerar_mais_dados)
        btn_ver_mais.pack(fill="x", side="right")
        
        
        self.listar_dados_do_dia()
        
    # Funções para gerar dados na tabela a implementar
    def listar_dados_do_dia(self):
        ...
        # Esboço
        # for i in self.dados:
        #     self.aplicacao_lbl = ctk.CTkLabel(self.frame_dados, text=f"{i[0]}", font=ctk.CTkFont(size=14, weight="bold"))
        #     self.aplicacao_lbl.grid(row=(i+1), column=0, padx=20)

        #     self.tempo_de_uso_lbl = ctk.CTkLabel(self.frame_dados, text=f"{i[1]}", font=ctk.CTkFont(size=14, weight="bold"))
        #     self.tempo_de_uso_lbl.grid(row=(i+1), column=1, padx=20)
            
        #     self.data_lbl = ctk.CTkLabel(self.frame_dados, text=f"{i[2]}", font=ctk.CTkFont(size=14, weight="bold"))
        #     self.data_lbl.grid(row=(i+1), column=2, padx=20)
    
    def gerar_mais_dados(self):
        ...
            
        
    