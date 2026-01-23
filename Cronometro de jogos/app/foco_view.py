import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
try:
    from pygame import mixer
except ImportError:
    mixer = None
    pygame = None
from pathlib import Path
import json
import timer_count
import time_check

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")



BASE_DIR = Path(__file__).resolve().parents[2]

sons = BASE_DIR / "assets" / "sons"

CONFIG_PATH = BASE_DIR / "config.json"

t = 0
s = None

class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("FocusDesk IA - Temporizador Básico")
        self.geometry("800x600")
        self.minsize(1200, 800)


        self.main_view = FocoView(self) 


def carregar_config():

    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                dados = json.load(f)
                # Garantir que todas as chaves existam
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in dados:
                        dados[key] = value
                return dados
        else:
            return DEFAULT_SETTINGS.copy()
    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
        print(f"Erro ao carregar configurações: {e}")
        return DEFAULT_SETTINGS.copy()

# Configurações Padrão
DEFAULT_SETTINGS = {
    "tempo_de_jogo": 25,
    "tempo_pausa": 15,
    "auto_pausa": False,
    "modo_atual": "tempo_de_jogo",
    "som_alarme": "Sino",
    "som_tictac": "Nenhum"
}


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
        
        btn_config = ctk.CTkButton(barra_superior,  text="Configurações",  command=self.abrir_configuracoes,  font=ctk.CTkFont(size=14, weight="bold"),  fg_color="#2e7bf6",  hover_color="#1e5bb4",  corner_radius=10, width=150)
        btn_config.grid(row=0, column=0, padx=0, pady=10)
        
        container_principal = ctk.CTkFrame(self, fg_color="transparent")
        container_principal.pack(fill="both", expand=True, padx=20, pady=10)
        container_principal.grid_columnconfigure(0, weight=1)
        container_principal.grid_rowconfigure(0, weight=1)
        
        self.painel = ctk.CTkFrame(container_principal, fg_color="#111316", corner_radius=12, border_width=1, border_color="#2a2d2e")
        self.painel.grid(row=0, column=0, sticky="nsew", padx=(10), pady=10)
        

        
        self.criar_painel_esquerdo()



    def abrir_configuracoes(self):
        """Abre a janela de Configurações."""
        try:
            if self.dialogo_configuracoes and self.dialogo_configuracoes.winfo_exists():
                self.dialogo_configuracoes.focus()
            else:
                self.dialogo_configuracoes = ConfiguracoesDialog(self, self.state_vars)
        except Exception as e:
            print(f"Erro ao abrir configurações: {e}")

    def criar_painel_esquerdo(self):
        self.painel.grid_rowconfigure(2, weight=1)
        self.painel.grid_columnconfigure(0, weight=1)
        self.painel.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.painel, text="Foco Total", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(20, 15), sticky="n")

        # Modos de Tempo
        frame_modos = ctk.CTkFrame(self.painel, fg_color="transparent")
        frame_modos.grid(row=1, column=0, columnspan=2, pady=10)

        self.btn_tempo_de_jogo = self.criar_botao_modo(frame_modos, "tempo_de_jogo", 0)
        self.btn_pausa = self.criar_botao_modo(frame_modos, "Pausa", 2)
        
        self.state_vars["modo_atual"].trace_add("write", self.atualizar_selecao_modo)

        # Container do Timer
        container_temporizador = ctk.CTkFrame(self.painel, fg_color="transparent")
        container_temporizador.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=(10, 20))
        container_temporizador.grid_columnconfigure(0, weight=1)
        container_temporizador.grid_rowconfigure(0, weight=1)
        
        # Label para exibir o contador
        self.lbl_tempo = ctk.CTkLabel(container_temporizador, text="25:00", font=ctk.CTkFont(size=72, weight="bold"), text_color="white")
        self.lbl_tempo.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Frame para botões de controle
        controle_frame = ctk.CTkFrame(container_temporizador, fg_color="transparent")
        controle_frame.grid(row=1, column=0, sticky="n", pady=(20, 0))
        
        # Botão de Controle Principal
        self.btn_iniciar = ctk.CTkButton(controle_frame, text="Iniciar", command=self.alternar_temporizador, 
                                        font=ctk.CTkFont(size=18, weight="bold"), height=50, width=160, 
                                        fg_color="#2e7bf6", hover_color="#1e5bb4", corner_radius=12)
        self.btn_iniciar.pack(side="left", padx=(0, 10))
        
        # Botão Restaurar Tempo
        btn_restaurar = ctk.CTkButton(controle_frame, text="Restaurar", command=self.restaurar_tempo, 
                                     font=ctk.CTkFont(size=12, weight="bold"), height=50, width=80, 
                                     fg_color="#363636", hover_color="#4a4a4a", corner_radius=12)
        btn_restaurar.pack(side="left")
        
    def criar_botao_modo(self, pai, nome, coluna):
        btn = ctk.CTkButton(pai, text=nome, command=lambda n=nome: self.trocar_modo(n), font=ctk.CTkFont(size=15), height=30, width=120, fg_color="#2a2d2e", text_color="#9aa0a6", hover_color="#3c4146")
        btn.grid(row=0, column=coluna, padx=5)
        return btn

    def atualizar_selecao_modo(self, *args):
        
        global t,s
        
        for btn in [self.btn_tempo_de_jogo, self.btn_pausa]:
            btn.configure(fg_color="#2a2d2e", text_color="#9aa0a6")

        modo = self.state_vars["modo_atual"].get()
        novo_tempo_minutos = 0

        if modo == "tempo_de_jogo":
            self.btn_tempo_de_jogo.configure(fg_color="#2e7bf6", text_color="white")
            novo_tempo_minutos = self.state_vars["tempo_de_jogo"].get()
        elif modo == "Pausa":
            self.btn_pausa.configure(fg_color="#2e7bf6", text_color="white")
            novo_tempo_minutos = self.state_vars["tempo_pausa"].get()
        
        if timer_count.rodando == True:
            self.btn_iniciar.configure(text="Pausar")
        else:
            self.btn_iniciar.configure(text="Iniciar")




        self.segundos_iniciais = novo_tempo_minutos * 60
        t = self.segundos_iniciais

        if timer_count.ativo == True:
            novo_tempo_minutos = timer_count.atual
            self.segundos_iniciais = novo_tempo_minutos


        s= self.state_vars["som_alarme"].get()
        if s.lower() == "sino":
            s = sons / "Sino.mp3"
        else:
            s = None
            
        
        if not self.em_execucao:
             self.segundos = t
             self.atualizar_exibicao_temporizador()
    
    def trocar_modo(self, nome_modo):
        if self.em_execucao:
            return
        self.state_vars["modo_atual"].set(nome_modo)

    

    
    def carregar_dados_iniciais(self):
        print(f"Debug: Controller = {self.controller}")
        if self.controller:
            print("Debug: Carregando metas...")
            self.carregar_metas()
        else:
            print("Debug: Controller é None!")


    

        
    # Temporizador 
    def formatar_tempo(self, segundos):
        m, s = divmod(segundos, 60)
        return f"{m:02d}:{s:02d}"
    
    def atualizar_exibicao_temporizador(self):

        if timer_count.rodando == True:
            self.segundos = timer_count.atual
            self.em_execucao = True

        self.lbl_tempo.configure(text=self.formatar_tempo(self.segundos))
        
        if self.em_execucao and self.segundos > 0:
            self.id_temporizador = self.after(1000, self.tick_temporizador)

    
    def tick_temporizador(self):
        
        if not self.em_execucao or self.segundos <= 0:
            return
        
        
        # Som de tique-taque
        if self.state_vars["som_tictac"].get() == "Padrão":
            try:
                import winsound
                winsound.Beep(800, 50)
            except (ImportError, RuntimeError, OSError):
                pass  # Sistema não suporta som
            
        self.segundos -= 1
        self.atualizar_exibicao_temporizador()
            
        if self.segundos == 0:
            som_escolhido = self.state_vars["som_alarme"].get()

            modo = self.state_vars['modo_atual'].get()

            if modo == "tempo_atual":
                self.tracker.parar()
                self.tracker.get_relatorio()
                self.tracker.get_tempo_total()

                relatorio = self.tracker.get_relatorio()
                total = self.tracker.get_tempo_total()

            

                
                print(f"tempo gasto na frente da tela: {total}")
                print("\nRELATÓRIO DA SESSÃO:")
                
                for app, tempo in relatorio.items():
                    print(f"{app}: {tempo:.1f} segundos")

            if som_escolhido == "Sino":
                try:
                    self.bell(sons / "sino.mp3")
                except Exception as e:
                    print(f"Erro ao tocar som de alarme: {e}")
            else:
                print("Som de alarme desativado")
            
            messagebox.showinfo("timer zerado", "o tempo acabou")
            self.em_execucao = False
            self.btn_iniciar.configure(text="Iniciar")

            if self.state_vars["auto_pausa"].get():
                self.after(2000, self.alternar_proximo_modo_e_iniciar)  # Aguarda 2 segundos
            
        
    def bell(self, som):
        try:
            if mixer is None:
                raise ImportError("pygame não disponível")
            
            mixer.init()
            if som.exists():
                mixer.music.load(str(som))
                mixer.music.play()
            else:
                # Som alternativo se arquivo não existir
                import winsound
                winsound.Beep(1000, 500)
        except Exception as e:
            print(f"Erro ao reproduzir som: {e}")
            try:
                import winsound
                winsound.Beep(1000, 500)
            except Exception:
                pass


    def alternar_temporizador(self):
        
        global t,s

        modo = self.state_vars["modo_atual"].get()


        if self.id_temporizador:
            self.after_cancel(self.id_temporizador)
            self.id_temporizador = None

        if not self.em_execucao and self.segundos > 0:
            self.em_execucao = True
            self.btn_iniciar.configure(text="Pausar")
            self.atualizar_exibicao_temporizador()

            if modo == "tempo_de_jogo":
                self.tracker.iniciar()
            
            from threading import Thread
            Thread(target=timer_count.contador, args=(self.segundos,s), daemon=True).start()
            
        else:
            timer_count.parar_contador()
            
            if modo == "tempo_de_jogo":
                self.tracker.parar()
                self.tracker.get_relatorio()
                self.tracker.get_tempo_total

                relatorio = self.tracker.get_relatorio()
                total = self.tracker.get_tempo_total()

            

                print(f"tempo gasto na frente da tela: {total}")
                print("\nRELATÓRIO DA SESSÃO:")
                
                for app, tempo in relatorio.items():
                    print(f"{app}: {tempo:.1f} segundos")

            self.em_execucao = False
            self.btn_iniciar.configure(text="Iniciar")
            self.atualizar_exibicao_temporizador()
            
    
    def alternar_proximo_modo_e_iniciar(self):
        if not self.em_execucao:  # Só alterna se não estiver rodando
            modo = self.state_vars["modo_atual"].get()
            
            if modo == "tempo_de_jogo":
                proximo_modo = "Descanso" 
            else:
                proximo_modo = "tempo_de_jogo" 
            self.state_vars["modo_atual"].set(proximo_modo)
            # Iniciar automaticamente se auto_pausa estiver ativo
            if self.state_vars["auto_pausa"].get():
                self.alternar_temporizador()
    
    def restaurar_tempo(self):
        global t
        """Restaura o tempo para o valor inicial do modo atual"""
        if not self.em_execucao:
            self.segundos = t
            timer_count.ativo == False
            timer_count.rodando == False
            timer_count.atual = self.segundos
            self.atualizar_exibicao_temporizador()
            print(f"Tempo restaurado para {t // 60} minutos")
    
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
        
        # Garantir que state_vars tenha todas as variáveis necessárias
        if "som_tictac" not in state_vars:
            state_vars["som_tictac"] = ctk.StringVar(value=DEFAULT_SETTINGS["som_tictac"])
        
        self.state_vars = state_vars

        
        # Variáveis locais da janela
        self.tempo_de_jogo_var = ctk.StringVar(value=str(self.state_vars["tempo_de_jogo"].get()))
        self.tempo_pausa_var = ctk.StringVar(value=str(self.state_vars["tempo_pausa"].get()))
        self.som_alarme_var = ctk.StringVar(value=self.state_vars["som_alarme"].get())
        self.som_tictac_var = ctk.StringVar(value=self.state_vars["som_tictac"].get())
        self.auto_pausa_var = ctk.BooleanVar(value=self.state_vars["auto_pausa"].get()) 

        
        self.criar_widgets_configuracoes()
        
        self.resizable(False, False)

    def criar_widgets_configuracoes(self):
        
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0) 
        self.grid_columnconfigure(0, weight=1)

        #FRAME DE CONTEÚDO (Temporizador e Som)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        row_counter = 0

        #TEMPORIZADOR 
        ctk.CTkLabel(content_frame, text=" TEMPORIZADOR", font=ctk.CTkFont(size=16, weight="bold")).grid(row=row_counter, column=0, columnspan=2, pady=(0, 10), sticky="w")
        row_counter += 1
        
        ctk.CTkLabel(content_frame, text="Tempo (minutos)", font=ctk.CTkFont(size=14, weight="bold")).grid(row=row_counter, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 5))
        row_counter += 1
        
        ctk.CTkLabel(content_frame, text="tempo_de_jogo (min):").grid(row=row_counter, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(content_frame, textvariable=self.tempo_de_jogo_var).grid(row=row_counter, column=1, padx=10, pady=5, sticky="ew")
        row_counter += 1

        ctk.CTkLabel(content_frame, text=" pausa (min):").grid(row=row_counter, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(content_frame, textvariable=self.tempo_pausa_var).grid(row=row_counter, column=1, padx=10, pady=5, sticky="ew")
        row_counter += 1
        
        ctk.CTkLabel(content_frame, text="Pausas automáticas:").grid(row=row_counter, column=0, padx=10, pady=5, sticky="w")
        self.switch_auto_pausa = ctk.CTkSwitch(content_frame, text="", variable=self.auto_pausa_var)
        self.switch_auto_pausa.grid(row=row_counter, column=1, padx=10, pady=5, sticky="e")
        row_counter += 1
        
        # Separador visual
        ctk.CTkFrame(content_frame, height=2, fg_color="#2a2d2e").grid(row=row_counter, column=0, columnspan=2, sticky="ew", pady=15)
        row_counter += 1
        
        #SOM 
        ctk.CTkLabel(content_frame, text="🔊 SOM", font=ctk.CTkFont(size=16, weight="bold")).grid(row=row_counter, column=0, columnspan=2, pady=(5, 10), sticky="w")
        row_counter += 1

        ctk.CTkLabel(content_frame, text="Som de alarme:").grid(row=row_counter, column=0, padx=10, pady=8, sticky="w")
        self.option_som = ctk.CTkOptionMenu(content_frame, values=["Sino", "Nenhum"], width=150, variable=self.som_alarme_var)
        self.option_som.grid(row=row_counter, column=1, padx=10, pady=8, sticky="e")
        row_counter += 1
        
        ctk.CTkLabel(content_frame, text="Som de tique-taque:").grid(row=row_counter, column=0, padx=10, pady=8, sticky="w")
        self.option_tictac = ctk.CTkOptionMenu(content_frame, values=["Nenhum", "Padrão"], width=150, variable=self.som_tictac_var)
        self.option_tictac.grid(row=row_counter, column=1, padx=10, pady=8, sticky="e")
        row_counter += 1

        # --- FRAME DE BOTÕES (Rodapé) ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Botão Redefinir
        btn_redefinir = ctk.CTkButton(button_frame,  text="Redefinir",  command=self.fechar_e_avisar_resetar,  
                                      font=ctk.CTkFont(size=16, weight="bold"), fg_color="#3c4146",  hover_color="#52575c")
        btn_redefinir.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # Botão Confirmar
        btn_confirmar = ctk.CTkButton(button_frame,  text="Confirmar",  command=self.fechar_e_avisar_confirmar,  
                                      font=ctk.CTkFont(size=16, weight="bold"), fg_color="#2e7bf6",  hover_color="#1e5bb4")
        btn_confirmar.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
    def fechar_e_avisar_confirmar(self):
        global DEFAULT_SETTINGS
        som_alarme_escolhido = self.som_alarme_var.get()
        som_tictac_escolhido = self.som_tictac_var.get()
        
        # Atualizar state_vars do FocoView
        self.master.state_vars["som_alarme"].set(som_alarme_escolhido)
        self.master.state_vars["som_tictac"].set(som_tictac_escolhido)
        
        print(f"Configurações aplicadas - Alarme: {som_alarme_escolhido}, Tictac: {som_tictac_escolhido}")

        minutos_foco = self.tempo_de_jogo_var.get()
        minutos_descanso = self.tempo_pausa_var.get()

        try:
            minutos_foco = int(minutos_foco)
            minutos_descanso = int(minutos_descanso)
            
            # Validar valores mínimos
            if minutos_foco < 1 or minutos_descanso < 1:
                messagebox.showerror("Erro", "Os tempos devem ser maiores que 0")
                return
            
            # Atualizar configurações
            DEFAULT_SETTINGS["tempo_de_jogo"] = minutos_foco
            DEFAULT_SETTINGS["tempo_pausa"] = minutos_descanso
            DEFAULT_SETTINGS["auto_pausa"] = self.auto_pausa_var.get()
            DEFAULT_SETTINGS["som_tictac"] = self.som_tictac_var.get()
            
            # Salvar som de alarme também
            DEFAULT_SETTINGS["som_alarme"] = self.som_alarme_var.get()
            
            # Atualizar variáveis do FocoView
            self.master.state_vars["tempo_de_jogo"].set(minutos_foco)
            self.master.state_vars["tempo_pausa"].set(minutos_descanso)
            self.master.state_vars["auto_pausa"].set(self.auto_pausa_var.get())
            self.master.state_vars["som_alarme"].set(self.som_alarme_var.get())
            self.master.state_vars["som_tictac"].set(self.som_tictac_var.get())
            
            # Atualizar modo atual
            self.master.atualizar_selecao_modo()
            
            # Salvar em arquivo JSON
            try:
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_SETTINGS, f, indent=4, ensure_ascii=False)
            except (PermissionError, OSError) as e:
                messagebox.showerror("Erro", f"Não foi possível salvar configurações: {e}")
                return
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            
        except ValueError as e:
            messagebox.showerror("Erro", "Digite apenas números nos campos de tempo")
            return
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
            return


        self.destroy()

    def fechar_e_avisar_resetar(self):
        # Resetar para valores padrão
        resposta = messagebox.askyesno("Confirmar", "Deseja restaurar as configurações padrão?")
        if resposta:
            self.tempo_de_jogo_var.set("25")
            self.tempo_pausa_var.set("15")
            self.auto_pausa_var.set(False)
            self.som_alarme_var.set("Sino")
            self.som_tictac_var.set("Nenhum")
            
            # Atualizar widgets visualmente
            if hasattr(self, 'switch_auto_pausa'):
                self.switch_auto_pausa.deselect()
            if hasattr(self, 'option_som'):
                self.option_som.set("Sino")
            if hasattr(self, 'option_tictac'):
                self.option_tictac.set("Nenhum")
        
    def on_close(self):
        self.destroy()
        

class NotificacaoDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Tempo limite atingido")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = screen_width-300-20
        y = screen_height-150-90

        self.geometry(f"300x150+{x}+{y}") 

        self.columnconfigure((0,1), weight=1)

        label = ctk.CTkLabel(self, text="Tempo limite atingido", fg_color="transparent", font=("Helvetica", 15))
        label.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")


        btn_pausa = ctk.CTkButton(self, text="Ir para\npausa", width=75)
        btn_pausa.grid(row=2, column=0, padx=20, pady=10, sticky="e")

        btn_add_tempo = ctk.CTkButton(self, text="Adicionar\ntempo", width=75)
        btn_add_tempo.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        entry = ctk.CTkEntry(self, placeholder_text="+ min", width=60)
        entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("400x240")
    app.title("Janela")

    NotificacaoDialog(app)

    
    app.mainloop()