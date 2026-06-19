import customtkinter as ctk
import os
import json
from tkinter import messagebox

# ==============================================================================
# 🔌 VERIFICAÇÃO DE DEPENDÊNCIAS DE EXPORTAÇÃO
# ==============================================================================
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


class PegasusTypewriter:
    def __init__(self, nexus):
        self.nexus = nexus
        self.root = nexus._root
        
        # 🎨 PALETA DESIGN: Linen Paper
        self.bg_color = "#EAE4D9"       
        self.paper_color = "#FAF8F2"    
        self.text_color = "#3A332C"     
        self.accent_color = "#D1C7B7"   
        self.subtle_text = "#8B7E70"    
        
        self.root.configure(fg_color=self.bg_color)
        
        # 🛡️ INICIALIZAÇÃO DEFENSIVA
        os.makedirs("userdata", exist_ok=True)
        
        # 📂 GERENCIAMENTO DE ESTADO E MEMÓRIA DE CADERNO
        self.autosave_file = os.path.join("userdata", "typewriter_cache.json")
        self.pages = {1: ""}
        self.current_page = 1
        self.is_running = True
        
        self.build_ui()
        self.load_autosave()
        self.start_autosave_daemon()

    def build_ui(self):
        # ----------------------------------------------------------------------
        # 🧭 CONTROL BAR (Painel de Utilidades Superior)
        # ----------------------------------------------------------------------
        self.top_bar = ctk.CTkFrame(self.root, fg_color="transparent", height=40)
        self.top_bar.pack(fill="x", padx=30, pady=(15, 0))
        
        self.lbl_status = ctk.CTkLabel(
            self.top_bar, 
            text="SISTEMA: ESTABILIZADO", 
            font=("Consolas", 11, "bold"), 
            text_color=self.subtle_text
        )
        self.lbl_status.pack(side="left", anchor="center")
        
        self.btn_docx = ctk.CTkButton(
            self.top_bar, text="Mandar para DOCX", width=130, height=28,
            fg_color=self.accent_color, text_color=self.text_color,
            font=("Arial", 12, "bold"), hover_color="#C0B4A0", command=self.export_docx
        )
        self.btn_docx.pack(side="right", padx=5)
        
        self.btn_pdf = ctk.CTkButton(
            self.top_bar, text="Exportar em PDF", width=120, height=28,
            fg_color=self.accent_color, text_color=self.text_color,
            font=("Arial", 12, "bold"), hover_color="#C0B4A0", command=self.export_pdf
        )
        self.btn_pdf.pack(side="right", padx=5)

        # ----------------------------------------------------------------------
        # 📖 CANVAS DE ESCRITA (Diagramação Pinterest / Livro)
        # ----------------------------------------------------------------------
        self.page_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.page_container.pack(fill="both", expand=True, padx=53, pady=(20, 23))
        
        self.textbox = ctk.CTkTextbox(
            self.page_container, 
            font=("Georgia", 18), 
            fg_color=self.paper_color, 
            text_color=self.text_color,
            border_color=self.accent_color,
            border_width=1,
            corner_radius=11,
            wrap="word",
            padx=55, # Mantido para criar a "margem do papel"
            pady=50
        )
        self.textbox.pack(expand=True, fill="both")
        
        # Ativação do motor Undo/Redo nativo (Ctrl+Z / Ctrl+Y)
        self.textbox._textbox.configure(undo=True, maxundo=-1)
        self.textbox.focus_set()
        
        # ----------------------------------------------------------------------
        # 🎚️ FOOTER BAR (Painel de Rodapé e Paginação)
        # ----------------------------------------------------------------------
        self.bottom_bar = ctk.CTkFrame(self.root, fg_color="transparent", height=30)
        self.bottom_bar.pack(fill="x", padx=30, pady=(0, 15))
        
        self.lbl_page = ctk.CTkLabel(
            self.bottom_bar, 
            text=f"- {self.current_page} -", 
            font=("Georgia", 14, "italic"), 
            text_color=self.subtle_text
        )
        self.lbl_page.pack(expand=True)
        
        # ----------------------------------------------------------------------
        # ⌨️ MAPEAMENTO DE SUBROTINAS E HOTKEYS
        # ----------------------------------------------------------------------
        self.textbox.bind("<Prior>", self.prev_page)      
        self.textbox.bind("<Next>", self.next_page)       
        self.textbox.bind("<Control-d>", self.format_dialogue)
        self.textbox.bind("<Control-t>", self.format_title)
        self.textbox.bind("<KeyRelease>", self.mark_unsaved)

    # ==========================================================================
    # 📑 MECANISMO DE PAGINAÇÃO VOLÁTIL
    # ==========================================================================
    def save_current_page_to_memory(self):
        if self.textbox.winfo_exists():
            self.pages[self.current_page] = self.textbox.get("1.0", "end-1c")

    def load_page_to_ui(self):
        self.textbox.delete("1.0", "end")
        page_text = self.pages.get(self.current_page, "")
        self.textbox.insert("1.0", page_text)
        self.lbl_page.configure(text=f"- {self.current_page} -")
        self.textbox.see("insert")
        
        try:
            self.textbox._textbox.edit_reset()
        except:
            pass

    def prev_page(self, event=None):
        if self.current_page > 1:
            self.save_current_page_to_memory()
            self.current_page -= 1
            self.load_page_to_ui()
        return "break"

    def next_page(self, event=None):
        self.save_current_page_to_memory()
        self.current_page += 1
        if self.current_page not in self.pages:
            self.pages[self.current_page] = ""
        self.load_page_to_ui()
        return "break"

    # ==========================================================================
    # ⚡ AUTOMATIZAÇÕES DE FORMATAÇÃO INTELIGENTE (SMART TOGGLES)
    # ==========================================================================
    def format_dialogue(self, event=None):
        cursor_pos = self.textbox.index("insert")
        line_number = cursor_pos.split('.')[0]
        line_start = f"{line_number}.0"
        line_end = f"{line_number}.end"
        
        raw_text = self.textbox.get(line_start, line_end)
        
        try: self.textbox._textbox.edit_separator()
        except: pass

        # Correção: Removido o \t para que o diálogo fique alinhado à esquerda
        if raw_text.strip().startswith("— "):
            clean_text = raw_text.replace("— ", "").strip()
            self.textbox.delete(line_start, line_end)
            self.textbox.insert(line_start, clean_text)
            self.update_status("Revertido: Texto Normal")
        else:
            clean_text = raw_text.strip()
            self.textbox.delete(line_start, line_end)
            self.textbox.insert(line_start, f"— {clean_text}")
            self.update_status("Aplicado: Diálogo")
            
        try: self.textbox._textbox.edit_separator()
        except: pass
        return "break"

    def format_title(self, event=None):
        cursor_pos = self.textbox.index("insert")
        line_number = cursor_pos.split('.')[0]
        line_start = f"{line_number}.0"
        line_end = f"{line_number}.end"
        
        raw_text = self.textbox.get(line_start, line_end)
        stripped = raw_text.strip()
        
        if not stripped:
            return "break"
            
        try: self.textbox._textbox.edit_separator()
        except: pass

        if stripped.startswith("[") and stripped.endswith("]"):
            clean_text = stripped[1:-1].strip().capitalize()
            self.textbox.delete(line_start, line_end)
            self.textbox.insert(line_start, clean_text)
            self.update_status("Revertido: Texto Normal")
        else:
            self.textbox.delete(line_start, line_end)
            # Correção: Usando espaços em vez de \t\t para um centro mais harmônico
            title_formatted = f"          [ {stripped.upper()} ]"
            self.textbox.insert(line_start, title_formatted)
            self.update_status("Aplicado: Título")
            
        try: self.textbox._textbox.edit_separator()
        except: pass
        return "break"

    # ==========================================================================
    # 🛡️ PROTOCOLO DE SINCRO (AUTOSAVE ASSÍNCRONO NATIVO)
    # ==========================================================================
    def mark_unsaved(self, event=None):
        if event and event.keysym in ["Up", "Down", "Left", "Right", "Prior", "Next"]:
            return
        self.update_status("Escrevendo...")

    def update_status(self, text):
        if self.lbl_status.winfo_exists():
            self.lbl_status.configure(text=f"SISTEMA: {text.upper()}")

    def load_autosave(self):
        if os.path.exists(self.autosave_file):
            try:
                with open(self.autosave_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        self.pages = {int(k): v for k, v in data.items()}
                        # Abre na última página modificada
                        self.current_page = max(self.pages.keys()) if self.pages else 1
            except Exception:
                self.pages = {1: ""}
        self.load_page_to_ui()

    def start_autosave_daemon(self):
        def autosave_loop():
            if not self.is_running:
                return
            
            if hasattr(self, 'textbox') and self.textbox.winfo_exists():
                self.save_current_page_to_memory()
                try:
                    with open(self.autosave_file, "w", encoding="utf-8") as f:
                        json.dump(self.pages, f, ensure_ascii=False, indent=4)
                    self.update_status("Sincronizado (Automático)")
                except Exception as e:
                    print(f"[Erro Autosave] Falha ao gravar cache: {e}")
                
                self.root.after(10000, autosave_loop)
            
        self.root.after(10000, autosave_loop)

    # ==========================================================================
    # 🖨️ COMPILADORES DE MANUSCRITO (EXPORTADORES)
    # ==========================================================================
    def export_pdf(self):
        if not HAS_FPDF:
            messagebox.showerror("Mimas Abort", "Biblioteca fpdf2 ausente.\nExecute: pip install fpdf2")
            return
            
        try:
            self.save_current_page_to_memory()
            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.set_margins(left=25, top=25, right=25)
            pdf.set_auto_page_break(auto=True, margin=25)
            
            font_paths = [
                r"C:\Windows\Fonts\georgia.ttf",
                r"C:\Windows\Fonts\arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/Library/Fonts/Georgia.ttf",
                "/Library/Fonts/Arial.ttf"
            ]
            
            unicode_active = False
            for path in font_paths:
                if os.path.exists(path):
                    try:
                        pdf.add_font("BookFont", "", path)
                        pdf.set_font("BookFont", size=12)
                        unicode_active = True
                        break
                    except:
                        continue
            
            if not unicode_active:
                pdf.set_font("Helvetica", size=12)
            
            for page_num in sorted(self.pages.keys()):
                content = self.pages[page_num].strip()
                if content:
                    pdf.add_page()
                    if unicode_active:
                        pdf.multi_cell(w=0, h=7, txt=content)
                    else:
                        sanitized_text = content.encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(w=0, h=7, txt=sanitized_text)
            
            save_path = os.path.join("userdata", "Manuscrito_Compilado.pdf")
            pdf.output(save_path)
            messagebox.showinfo("Saturn Export", f"PDF compilado com suporte nativo a Unicode!\nSalvo em: {save_path}")
        except Exception as e:
            messagebox.showerror("Mimas Interception", f"Falha ao gerar PDF: {e}")

    def export_docx(self):
        if not HAS_DOCX:
            messagebox.showerror("Mimas Abort", "Biblioteca python-docx ausente.\nExecute: pip install python-docx")
            return
            
        try:
            self.save_current_page_to_memory()
            doc = docx.Document()
            
            sections = doc.sections
            for section in sections:
                section.top_margin = docx.shared.Inches(1)
                section.bottom_margin = docx.shared.Inches(1)
                section.left_margin = docx.shared.Inches(1)
                section.right_margin = docx.shared.Inches(1)

            for page_num in sorted(self.pages.keys()):
                content = self.pages[page_num].strip()
                if content:
                    paragraphs = content.split('\n')
                    for para in paragraphs:
                        doc.add_paragraph(para)
                    
                    doc.add_page_break()
                    
            save_path = os.path.join("userdata", "Manuscrito_Compilado.docx")
            doc.save(save_path)
            messagebox.showinfo("Saturn Export", f"Manuscrito estruturado em páginas DOCX!\nSalvo em: {save_path}")
        except Exception as e:
            messagebox.showerror("Mimas Interception", f"Falha ao escrever arquivo DOCX: {e}")

    def __del__(self):
        self.is_running = False


# ==============================================================================
# 🪐 INJECT POINT (NEXUS API V3)
# ==============================================================================
def run(nexus):
    app = PegasusTypewriter(nexus)
