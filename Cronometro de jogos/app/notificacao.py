import customtkinter as ctk



class NotificacaoDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Tempo limite atingido")
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"300x190+{sw-320}+{sh-285}")
        self.transient(parent)
        self.attributes('-topmost', True)
        self.focus_set()
        self.grab_set()
        self.configure(fg_color="#0f1113")
        self.columnconfigure((0,1), weight=1)

        ctk.CTkLabel(self, text="Tempo limite atingido!", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=20, pady=10)

        btn_pausa = ctk.CTkButton(self, text="Ir para pausa",  
                                  width=40, 
                                  font=ctk.CTkFont(size=14, weight="bold"), 
                                  fg_color="#2e7bf6", 
                                  hover_color="#1e5bb4",
                                  corner_radius=10,
                                  command=self.ir_para_pausa)
        btn_pausa.grid(row=1, column=0, columnspan=2, padx=10, pady=(20,5))
        
        frame_entry = ctk.CTkFrame(self, fg_color="transparent")
        frame_entry.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        
        self.entry_minutos = ctk.CTkEntry(frame_entry, placeholder_text="+", width=40, corner_radius=8)
        self.entry_minutos.grid(row=0, column=0, padx=10, pady=5)
        
        self.lbl_minutos = ctk.CTkLabel(frame_entry, text="min", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_minutos.grid(row=0, column=1, padx=5, pady=5)

        btn_add = ctk.CTkButton(self, text="Adicionar Tempo", 
                                width=40, 
                                font=ctk.CTkFont(size=14, weight="bold"), 
                                fg_color="#2e7bf6", 
                                hover_color="#1e5bb4",
                                corner_radius=10,
                                command=self.adicionar_tempo)
        btn_add.grid(row=2, column=1, padx=10, pady=20, sticky="w")

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
        
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("400x240")
    app.title("Janela")

    NotificacaoDialog(app)

    
    app.mainloop()        