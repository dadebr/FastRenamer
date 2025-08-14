import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from name_sanitizer import FilenameSanitizer
from content_extractors import ContentExtractorManager

class RenamerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Renomeador de Arquivos em Lote")
        self.geometry("800x650") # Aumentar altura para novas opções

        self.directory = ""
        self.files = []
        self.extractor_manager = ContentExtractorManager()

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Widgets ---

        # Frame de seleção de pasta
        top_frame = ttk.Frame(self, padding="10")
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(top_frame, text="Pasta:").grid(row=0, column=0, padx=(0, 5))
        self.folder_path_entry = ttk.Entry(top_frame)
        self.folder_path_entry.grid(row=0, column=1, sticky="ew")
        self.folder_path_entry.config(state="readonly")

        self.browse_button = ttk.Button(top_frame, text="Selecionar Pasta...", command=self.select_folder)
        self.browse_button.grid(row=0, column=2, padx=(5, 0))

        # Frame principal (arquivos e opções)
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=0, minsize=300) # Aumentar minsize
        main_frame.grid_rowconfigure(0, weight=1)

        # Lista de arquivos
        files_frame = ttk.Labelframe(main_frame, text="Arquivos", padding="10")
        files_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        files_frame.grid_columnconfigure(0, weight=1)
        files_frame.grid_rowconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(files_frame, selectmode="extended")
        self.file_listbox.grid(row=0, column=0, sticky="nsew")

        files_scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.file_listbox.yview)
        files_scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.config(yscrollcommand=files_scrollbar.set)

        # Botões de seleção de arquivos
        selection_buttons_frame = ttk.Frame(files_frame)
        selection_buttons_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,0))
        ttk.Button(selection_buttons_frame, text="Selecionar Todos", command=self.select_all).pack(side="left", padx=(0,5))
        ttk.Button(selection_buttons_frame, text="Desmarcar Todos", command=self.deselect_all).pack(side="left")

        # --- Coluna de Opções ---
        options_column_frame = ttk.Frame(main_frame)
        options_column_frame.grid(row=0, column=1, sticky="ns")

        # Opções de Renomeação
        rename_options_frame = ttk.Labelframe(options_column_frame, text="Opções de Renomeação", padding="10")
        rename_options_frame.pack(fill="x", expand=False, pady=(0, 10))

        self.rename_option = tk.StringVar(value="sequential")

        ttk.Radiobutton(rename_options_frame, text="Nome Sequencial", variable=self.rename_option, value="sequential", command=self.create_option_widgets).pack(anchor="w")
        ttk.Radiobutton(rename_options_frame, text="Adicionar Prefixo/Sufixo", variable=self.rename_option, value="add_text", command=self.create_option_widgets).pack(anchor="w")
        ttk.Radiobutton(rename_options_frame, text="Substituir Texto", variable=self.rename_option, value="replace", command=self.create_option_widgets).pack(anchor="w")
        ttk.Radiobutton(rename_options_frame, text="Nome da Pasta + Sequencial", variable=self.rename_option, value="folder_name_seq", command=self.create_option_widgets).pack(anchor="w")
        ttk.Radiobutton(rename_options_frame, text="Extrair do Conteúdo", variable=self.rename_option, value="extract_content", command=self.create_option_widgets).pack(anchor="w")

        # --- Frame para inputs das opções ---
        self.option_inputs_frame = ttk.Frame(rename_options_frame, padding="5 10 5 5")
        self.option_inputs_frame.pack(fill="x", expand=True)

        # --- Opções de Sanitização ---
        sanitize_options_frame = ttk.Labelframe(options_column_frame, text="Opções de Finalização", padding="10")
        sanitize_options_frame.pack(fill="x", expand=False)

        # Case style
        self.case_style_var = tk.StringVar(value="Nenhum")
        ttk.Label(sanitize_options_frame, text="Caixa do Texto:").pack(anchor="w")
        self.case_style_combo = ttk.Combobox(
            sanitize_options_frame,
            textvariable=self.case_style_var,
            values=["Nenhum", "minúsculas", "MAIÚSCULAS", "Título", "Sentença"],
            state="readonly"
        )
        self.case_style_combo.pack(fill="x", pady=(0, 5))

        # Replace spaces
        self.replace_spaces_var = tk.BooleanVar(value=False)
        self.replace_spaces_check = ttk.Checkbutton(
            sanitize_options_frame,
            text="Substituir espaços por '_'",
            variable=self.replace_spaces_var
        )
        self.replace_spaces_check.pack(anchor="w")

        self.create_option_widgets() # Chamar para criar os widgets da opção default

        # Botão de Renomear
        rename_button = ttk.Button(self, text="Renomear Arquivos Selecionados", command=self.rename_files, style="Accent.TButton")
        rename_button.grid(row=2, column=0, pady=10, padx=10, sticky="e")

        # Estilo
        style = ttk.Style(self)
        style.configure("Accent.TButton", foreground="white", background="blue")

    def create_option_widgets(self):
        # Limpa widgets antigos
        for widget in self.option_inputs_frame.winfo_children():
            widget.destroy()

        option = self.rename_option.get()

        if option == "sequential":
            ttk.Label(self.option_inputs_frame, text="Nome Base:").pack(anchor="w")
            self.base_name_entry = ttk.Entry(self.option_inputs_frame)
            self.base_name_entry.pack(fill="x")
            self.base_name_entry.insert(0, "arquivo_")
        elif option == "add_text":
            ttk.Label(self.option_inputs_frame, text="Prefixo:").pack(anchor="w")
            self.prefix_entry = ttk.Entry(self.option_inputs_frame)
            self.prefix_entry.pack(fill="x")
            ttk.Label(self.option_inputs_frame, text="Sufixo:").pack(anchor="w")
            self.suffix_entry = ttk.Entry(self.option_inputs_frame)
            self.suffix_entry.pack(fill="x")
        elif option == "replace":
            ttk.Label(self.option_inputs_frame, text="Encontrar:").pack(anchor="w")
            self.find_entry = ttk.Entry(self.option_inputs_frame)
            self.find_entry.pack(fill="x")
            ttk.Label(self.option_inputs_frame, text="Substituir por:").pack(anchor="w")
            self.replace_entry = ttk.Entry(self.option_inputs_frame)
            self.replace_entry.pack(fill="x")
        elif option == "extract_content":
            ttk.Label(self.option_inputs_frame, text="Extrai o nome do conteúdo do arquivo.").pack(anchor="w")

            supported_exts = self.extractor_manager.get_supported_extensions()
            ext_str = ", ".join(sorted(list(supported_exts)))
            ttk.Label(self.option_inputs_frame, text=f"Suportado: {ext_str}", wraplength=250).pack(anchor="w", pady=(5,5))

            ttk.Label(self.option_inputs_frame, text="Padrão Regex (Opcional):").pack(anchor="w")
            self.regex_entry = ttk.Entry(self.option_inputs_frame)
            self.regex_entry.pack(fill="x")
            ttk.Label(self.option_inputs_frame, text="Usa o 1º grupo de captura do regex.").pack(anchor="w")


    def select_folder(self):
        """Abre o diálogo para selecionar uma pasta e atualiza a lista de arquivos."""
        path = filedialog.askdirectory(title="Selecione uma pasta")
        if path:
            self.directory = path
            self.folder_path_entry.config(state="normal")
            self.folder_path_entry.delete(0, "end")
            self.folder_path_entry.insert(0, self.directory)
            self.folder_path_entry.config(state="readonly")
            self.load_files()

    def load_files(self):
        """Carrega os arquivos do diretório selecionado na listbox."""
        self.file_listbox.delete(0, "end")
        self.files = []
        if self.directory:
            try:
                self.files = [f for f in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, f))]
                for f in sorted(self.files):
                    self.file_listbox.insert("end", f)
            except OSError as e:
                messagebox.showerror("Erro", f"Não foi possível acessar a pasta: {e}")

    def select_all(self):
        self.file_listbox.select_set(0, "end")

    def deselect_all(self):
        self.file_listbox.select_clear(0, "end")

    def rename_files(self):
        """Executa a operação de renomeação com base nas opções selecionadas."""
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Nenhum Arquivo", "Por favor, selecione ao menos um arquivo para renomear.")
            return

        selected_files = [self.file_listbox.get(i) for i in selected_indices]
        option = self.rename_option.get()
        renamed_count = 0
        errors = []

        if not messagebox.askyesno("Confirmar Renomeação", f"Você tem certeza que deseja renomear {len(selected_files)} arquivo(s)?"):
            return

        # Configurar o sanitizador com base nas opções da UI
        case_map = {
            "Nenhum": None,
            "minúsculas": "lower",
            "MAIÚSCULAS": "upper",
            "Título": "title",
            "Sentença": "sentence"
        }
        case_style = case_map.get(self.case_style_var.get())

        sanitizer = FilenameSanitizer(
            replace_spaces=self.replace_spaces_var.get(),
            case_style=case_style,
            conflict_resolution=True
        )

        for i, filename in enumerate(selected_files):
            try:
                old_path = os.path.join(self.directory, filename)
                name, ext = os.path.splitext(filename)
                proposed_new_name = ""

                if option == "sequential":
                    base_name = self.base_name_entry.get()
                    proposed_new_name = f"{base_name}{i+1:03d}{ext}"
                elif option == "add_text":
                    prefix = self.prefix_entry.get()
                    suffix = self.suffix_entry.get()
                    proposed_new_name = f"{prefix}{name}{suffix}{ext}"
                elif option == "replace":
                    find_text = self.find_entry.get()
                    replace_text = self.replace_entry.get()
                    if find_text:
                        proposed_new_name = name.replace(find_text, replace_text) + ext
                    else:
                        proposed_new_name = filename
                elif option == "folder_name_seq":
                    folder_name = os.path.basename(self.directory)
                    proposed_new_name = f"{folder_name}_{i+1:03d}{ext}"
                elif option == "extract_content":
                    file_path = Path(self.directory) / filename
                    regex_pattern = self.regex_entry.get()

                    extractor_kwargs = {}
                    if regex_pattern:
                        extractor_kwargs['regex_pattern'] = regex_pattern

                    extracted_text = self.extractor_manager.extract_content(file_path, **extractor_kwargs)

                    if extracted_text:
                        proposed_new_name = f"{extracted_text}{ext}"
                    else:
                        errors.append(f"'{filename}': Não foi possível extrair conteúdo.")
                        continue # Pula para o próximo arquivo

                if not proposed_new_name or proposed_new_name == filename:
                    # Nenhum nome novo foi gerado ou o nome é o mesmo.
                    # Podemos adicionar uma nota se quisermos, mas por enquanto pulamos.
                    continue

                # Sanitizar e resolver conflitos
                final_new_name = sanitizer.sanitize(proposed_new_name, directory=Path(self.directory))

                if final_new_name != filename:
                    new_path = os.path.join(self.directory, final_new_name)
                    os.rename(old_path, new_path)
                    renamed_count += 1
                else:
                    # O nome final sanitizado é o mesmo que o original
                    errors.append(f"'{filename}': O nome gerado ('{proposed_new_name}') resultou no nome original após a finalização.")

            except Exception as e:
                errors.append(f"Erro ao renomear '{filename}': {e}")

        # Feedback final
        message = f"{renamed_count} arquivo(s) renomeado(s) com sucesso."
        if errors:
            error_details = "\n".join(errors)
            message += f"\n\nOcorreram {len(errors)} erro(s):\n{error_details}"
            messagebox.showerror("Erros na Renomeação", message)
        else:
            messagebox.showinfo("Sucesso", message)

        self.load_files()

if __name__ == "__main__":
    app = RenamerApp()
    app.mainloop()
