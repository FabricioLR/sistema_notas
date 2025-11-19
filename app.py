import tkinter as tk
from tkinter import ttk
import random
import psycopg2
from tkinter import messagebox

class EditarAlunoPopup:
    def __init__(self, parent, column, value):
        self.popup = tk.Toplevel(parent)
        self.popup.title("Editar " + str(column))
        self.popup.geometry("300x150")
        self.popup.grid_columnconfigure(0, weight=1)

        self.novo_valor = None

        tk.Label(self.popup, text=column, anchor="w").grid(row=0, column=0, padx=5, pady=(10, 0), sticky="ew")
        self.novo_valor_entry = tk.Entry(self.popup, textvariable=tk.StringVar(value=value))
        self.novo_valor_entry.grid(row=1, column=0, padx=5, sticky="ew")
        frame = tk.Frame(self.popup)
        frame.grid(row=2, column=0, padx=5, pady=(30, 5), sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=0)
        frame.grid_columnconfigure(3, weight=1)
        tk.Button(frame, text="Cancelar", command=self.cancelar, cursor="hand1").grid(row=0, column=1, sticky="ew")
        tk.Button(frame, text="Salvar", command=self.salvar, cursor="hand1").grid(row=0, column=2, sticky="ew")

        parent.wait_window(self.popup)

    def cancelar(self):
        self.novo_valor = None
        self.popup.destroy()

    def salvar(self):
        self.novo_valor = self.novo_valor_entry.get()
        self.popup.destroy()


class Application:
    #Função Inicial da aplicação. Executa as demais funções de criação de interface, inicialização do banco de dados e preenchimento de dados
    def __init__(self, root=None):
        #Definindo o título e tamanho da janela que será criada
        self.root = root
        self.root.title("Sistema de notas")
        self.root.geometry("1000x600")
        self.root.resizable(False, False)

        #Executando função de conexão com o banco de dados e crianda as tabelas do sistema
        self.conexao_db()
        self.criar_tabelas()

        #Executando as funções responsáveis por adicionar os items à interface
        #Criando as tabs(alunos, cursos e notas) e preenchendo com widgtes(Entry, Button, Label, TreeView)
        self.criar_paginas(self.root)
        self.criar_pagina_alunos()
        self.criar_pagina_cursos()
        self.criar_pagina_notas()

        #Funções que preenchem as tabelas dos alunos, cursos e notas com informações salvas no banco de dados
        self.preencher_tabela_alunos()
        self.preencher_tabela_cursos()
        self.preencher_tabela_notas()

    #
    #Funções de conexão e criação de tabela no banco de dados
    #
    def conexao_db(self):
        self.conexao = psycopg2.connect("dbname=alunos_db user=postgres")
        self.cursor = self.conexao.cursor()

    def criar_tabelas(self): 
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cursos(
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL UNIQUE
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos(
                id INT PRIMARY KEY,
                nome TEXT NOT NULL,
                matricula TEXT NOT NULL,
                curso_id INTEGER,
                CONSTRAINT fk_cursos FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE SET NULL
            );
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notas(
                id INTEGER PRIMARY KEY,
                aluno_id INTEGER NOT NULL,
                nota REAL NOT NULL CHECK (nota >= 0 AND nota <= 10),
                CONSTRAINT fk_alunos FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE
            );
        """)

        self.conexao.commit()

    #
    #Funções para criação da interface
    #
    def criar_paginas(self, root):
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both")

        self.frame1 = tk.Frame(notebook)
        self.frame2 = tk.Frame(notebook)
        self.frame3 = tk.Frame(notebook)

        self.frame1.configure(background="pink")
        self.frame2.configure(background="pink")
        self.frame3.configure(background="pink")
    
        notebook.add(self.frame1, text='Alunos')
        notebook.add(self.frame2, text='Cursos')
        notebook.add(self.frame3, text='Notas')

    def criar_pagina_alunos(self):
        tk.Label(self.frame1, text="Nome: ", width=25, anchor="w", bg="pink").place(x=10, y=10, width=250, height=20)
        tk.Label(self.frame1, text="Matrícula: ", width=25, anchor="w", bg="pink").place(x=260, y=10, width=250, height=20)
        tk.Label(self.frame1, text="Curso: ", width=29, anchor="w", bg="pink").place(x=520, y=10, width=250, height=20)

        self.input_alunos_nome = tk.Entry(self.frame1, width=25)
        self.input_alunos_matricula = tk.Entry(self.frame1, width=25)
        
        nome_cursos = self.listar_cursos()
        self.selected_option_curso = tk.StringVar()
        if (len(nome_cursos) > 0):
            self.selected_option_curso.set(nome_cursos[0])
            self.input_alunos_curso = tk.OptionMenu(self.frame1, self.selected_option_curso, *nome_cursos)
        else:
            self.input_alunos_curso = tk.OptionMenu(self.frame1, self.selected_option_curso, *nome_cursos, value="")

        self.input_alunos_curso.config(width=25, cursor="hand2")

        tk.Button(self.frame1, width=10, text="Adicionar", command=self.adicionar_aluno, cursor="hand2").place(x=890, y=35, width=100, height=30)

        self.input_alunos_nome.place(x=10, y=35, width=240, height=30)
        self.input_alunos_matricula.place(x=260, y=35, width=240, height=30)
        self.input_alunos_curso.place(x=520, y=35, width=240, height=30)

        self.table = ttk.Treeview(self.frame1, columns=("col1", "col2", "col3", "col4", "col5"), show='headings', height=23)

        self.table.heading("col1", text="ID")
        self.table.heading("col2", text="NOME")
        self.table.heading("col3", text="MATRÍCULA")
        self.table.heading("col4", text="ID_CURSO")
        self.table.heading("col5", text="")
        
        self.table.column("col1", anchor=tk.CENTER, width=100)
        self.table.column("col2", anchor="w", width=280)
        self.table.column("col3", anchor="w", width=280)
        self.table.column("col4", anchor="w", width=280)
        self.table.column("col5", anchor=tk.CENTER, width=40)

        self.table.place(x=10, y=80, width=980, height=480)

        self.table.bind("<Double-1>", self.evento_duplo_click_tabela_alunos)
        self.table.bind("<Button-1>", self.evento_click_tabela_alunos)
        self.table.bind("<Button-3>", self.mostrar_pagina_aluno_menu)

    def criar_pagina_cursos(self):
        tk.Label(self.frame2, text="Curso:", bg="pink").place(x=10, y=10, height=20)
        self.input_cursos_nome = tk.Entry(self.frame2)
        tk.Button(self.frame2, text="Adicionar", command=self.adicionar_curso, cursor="hand1").place(x=890, y=35, width=100, height=30)

        self.input_cursos_nome.place(x=10, y=35, width=240, height=30)

        self.table_cursos = ttk.Treeview(self.frame2, columns=("col11", "col22", "col33"), show='headings')

        self.table_cursos.heading("col11", text="ID")
        self.table_cursos.heading("col22", text="NOME")
        self.table_cursos.heading("col33", text="")
        
        self.table_cursos.column("col11", anchor=tk.CENTER, width=100)
        self.table_cursos.column("col22", anchor="w", width=840)
        self.table_cursos.column("col33", anchor=tk.CENTER, width=40)

        self.table_cursos.place(x=10, y=80, width=980, height=480)

        self.table_cursos.bind("<Double-1>", self.evento_duplo_click_tabela_cursos)
        self.table_cursos.bind("<Button-1>", self.evento_click_tabela_cursos)
        self.table_cursos.bind("<Button-3>", self.mostrar_pagina_cursos_menu)

    def criar_pagina_notas(self):
        tk.Label(self.frame3, text="Matrícula:", bg="pink").place(x=10, y=10, height=20)
        matricula_alunos = self.listar_alunos_matricula()
        self.selected_option_matricula = tk.StringVar()
        if (len(matricula_alunos) > 0):
            self.selected_option_matricula.set(matricula_alunos[0])
            self.input_notas_aluno_id = tk.OptionMenu(self.frame3, self.selected_option_matricula, *matricula_alunos)
        else:
            self.input_notas_aluno_id = tk.OptionMenu(self.frame3, self.selected_option_matricula, *matricula_alunos, value="")

        tk.Label(self.frame3, text="Nota:", bg="pink").place(x=260, y=10, height=20)
        self.input_notas_nota = tk.Entry(self.frame3, width=22)
        tk.Button(self.frame3, width=15, text="Adicionar", command=self.adicionar_notas).place(x=890, y=35, width=100, height=30)

        self.input_notas_aluno_id.place(x=10, y=35, height=30, width=240)
        self.input_notas_nota.place(x=260, y=35, height=30, width=240)

        self.table_notas = ttk.Treeview(self.frame3, columns=("ID", "ALUNO_ID", "NOTA", "EXCLUIR"), show='headings')

        self.table_notas.heading("ID", text="ID")
        self.table_notas.heading("ALUNO_ID", text="ALUNO_ID")
        self.table_notas.heading("NOTA", text="NOTA")
        self.table_notas.heading("EXCLUIR", text="")

        self.table_notas.column("ID", width=100, anchor="center")
        self.table_notas.column("ALUNO_ID", width=420, anchor="w")
        self.table_notas.column("NOTA", width=420, anchor="w")
        self.table_notas.column("EXCLUIR", width=40, anchor="center")

        self.table_notas.place(x=10, y=80, width=980, height=480)

        self.table_notas.bind("<Double-1>", self.evento_duplo_click_tabela_notas)
        self.table_notas.bind("<Button-1>", self.evento_click_tabela_notas)
        self.table_notas.bind("<Button-3>", self.mostrar_pagina_notas_menu)

    #
    #Funções para criação do menu de atualização das 3 tabelas
    #
    def mostrar_pagina_aluno_menu(self, event):
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.tk_popup(event.x_root, event.y_root)
        context_menu.add_command(label="Atualizar", command=self.preencher_tabela_alunos)

    def mostrar_pagina_cursos_menu(self, event):
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.tk_popup(event.x_root, event.y_root)
        context_menu.add_command(label="Atualizar", command=self.preencher_tabela_cursos)

    def mostrar_pagina_notas_menu(self, event):
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.tk_popup(event.x_root, event.y_root)
        context_menu.add_command(label="Atualizar", command=self.preencher_tabela_notas)

    #
    #Funções para criação dos eventos de click e duplo click das 3 tabelas
    #
    def evento_duplo_click_tabela_alunos(self, event):
        row_id = self.table.identify_row(event.y)
        column_id = self.table.identify_column(event.x)

        if not row_id:
            return

        if column_id == "#5" or column_id == "#1":
            return

        col_index = int(column_id[1:]) - 1
        row_values = self.table.item(row_id, 'values')
        if 0 <= col_index < len(row_values):
            cell_value = row_values[col_index]
        else:
            cell_value = None

        column = self.table.heading(column_id)["text"]

        popup = EditarAlunoPopup(self.root, column, cell_value)
        if popup.novo_valor is not None and popup.novo_valor:
            self.editar_aluno(row_values[0], column_id, row_id, popup.novo_valor)
    
    def evento_click_tabela_alunos(self, event):
        row_id = self.table.identify_row(event.y)
        column_id = self.table.identify_column(event.x)

        if not row_id:
            return

        if column_id != "#5":
            return
        
        row_values = self.table.item(row_id, 'values')

        self.table.delete(row_id)
        self.remover_aluno(row_values[0])
        self.remover_nota_pelo_aluno_id(row_values[0])

    def evento_duplo_click_tabela_cursos(self, event):
        row_id = self.table_cursos.identify_row(event.y)
        column_id = self.table_cursos.identify_column(event.x)

        if not row_id:
            return

        if column_id == "#3" or column_id == "#1":
            return

        col_index = int(column_id[1:]) - 1
        row_values = self.table_cursos.item(row_id, 'values')
        if 0 <= col_index < len(row_values):
            cell_value = row_values[col_index]
        else:
            cell_value = None

        column = self.table_cursos.heading(column_id)["text"]

        popup = EditarAlunoPopup(self.root, column, cell_value)
        if popup.novo_valor is not None and popup.novo_valor:
            self.editar_curso(row_values[0], column_id, row_id, popup.novo_valor)
    
    def evento_click_tabela_cursos(self, event):
        row_id = self.table_cursos.identify_row(event.y)
        column_id = self.table_cursos.identify_column(event.x)

        if not row_id:
            return

        if column_id != "#3":
            return
        
        row_values = self.table_cursos.item(row_id, 'values')

        self.table_cursos.delete(row_id)
        self.remover_curso(row_values[0])
        #self.remover_nota_pelo_aluno_id(row_values[0])

    def evento_duplo_click_tabela_notas(self, event):
        row_id = self.table_notas.identify_row(event.y)
        column_id = self.table_notas.identify_column(event.x)

        if not row_id:
            return

        if column_id == "#4" or column_id == "#1":
            return

        col_index = int(column_id[1:]) - 1
        row_values = self.table_notas.item(row_id, 'values')
        if 0 <= col_index < len(row_values):
            cell_value = row_values[col_index]
        else:
            cell_value = None

        column = self.table_notas.heading(column_id)["text"]

        popup = EditarAlunoPopup(self.root, column, cell_value)
        if popup.novo_valor is not None and popup.novo_valor:
            self.editar_nota(row_values[0], column_id, row_id, popup.novo_valor)
    
    def evento_click_tabela_notas(self, event):
        row_id = self.table_notas.identify_row(event.y)
        column_id = self.table_notas.identify_column(event.x)

        if not row_id:
            return

        if column_id != "#4":
            return
        
        row_values = self.table_notas.item(row_id, 'values')

        self.table_notas.delete(row_id)
        self.remover_nota(row_values[0])
        #self.remover_nota_pelo_aluno_id(row_values[0])

    #
    #Funções para preencher as tabelas dos alunos, cursos e notas com os dados salvos no banco de dados
    #
    def preencher_tabela_alunos(self):
        for item in self.table.get_children():
            self.table.delete(item)

        self.cursor.execute("SELECT * FROM alunos")
        alunos = self.cursor.fetchall()

        for aluno in alunos:
            self.table.insert("", tk.END, values=(aluno[0], aluno[1], aluno[2], aluno[3], "🗑️"))

    def preencher_tabela_cursos(self):
        for item in self.table_cursos.get_children():
            self.table_cursos.delete(item)

        self.cursor.execute("SELECT * FROM cursos")
        cursos = self.cursor.fetchall()

        for curso in cursos:
            self.table_cursos.insert("", tk.END, values=(curso[0], curso[1], "🗑️"))

    def preencher_tabela_notas(self):
        for item in self.table_notas.get_children():
            self.table_notas.delete(item)

        self.cursor.execute("SELECT * FROM notas")
        notas = self.cursor.fetchall()

        for nota in notas:
            self.table_notas.insert("", tk.END, values=(nota[0], nota[1], nota[2], "🗑️"))
    

    #
    #Funções para adicionar, remove e atualizar aluno, curso e nota tanto nas tabelas da interface como no banco de dados
    #
    def adicionar_aluno(self):
        try:
            nome_aluno = str(self.input_alunos_nome.get())
            matricula_aluno = int(self.input_alunos_matricula.get())
            curso_aluno = int(self.selected_option_curso.get())

            self.input_alunos_nome.delete(0, tk.END)
            self.input_alunos_matricula.delete(0, tk.END)

            if (len(nome_aluno) == 0 or len(matricula_aluno) == 0 or len(curso_aluno) == 0):
                return

            self.cursor.execute("SELECT id FROM alunos WHERE matricula = %s", (matricula_aluno,))
            if (self.cursor.fetchone() != None):
                messagebox.showerror("Error", "Matrícula já existe")
                return

            id = random.randint(0, 100000)

            curso_id = self.curso_nome_para_curso_id(curso_aluno)

            self.table.insert("", tk.END, values=(id, nome_aluno, matricula_aluno, curso_id, "🗑️"))

            self.cursor.execute("INSERT INTO alunos(id, nome, matricula, curso_id) VALUES (%s, %s, %s, %s)", (id, nome_aluno, matricula_aluno, curso_id))
            self.conexao.commit()

            self.atualizar_lista_matriculas()
        except (TypeError, ValueError):
            messagebox.showerror("Error", "Dados inseridos são inválidos")
        except:
            messagebox.showerror("Error", "Erro ao adicionar aluno")

    def remover_aluno(self, id):
        try:
            self.cursor.execute("DELETE FROM alunos WHERE id = %s", (id,))
            self.conexao.commit()

            self.preencher_tabela_notas()
        except:
            messagebox.showerror("Error", "Erro ao remover aluno")

    def editar_aluno(self, id, column_id, row_id, value):
        values = []

        for item_id in self.table.get_children():
            values = list(self.table.item(item_id, 'values'))
            if (values and values[0] == id):
                values[int(column_id[1:]) - 1] = value
                self.table.item(row_id, values=tuple(values))

        try:
            self.cursor.execute("UPDATE alunos SET nome = %s, matricula = %s, curso_id = %s WHERE id = %s", (values[1], values[2], values[3], id,))
            self.conexao.commit()
        except:
            messagebox.showerror("Error", "Erro ao tentar atualizar aluno")
            self.conexao.rollback()

        self.atualizar_lista_matriculas()

    
    def adicionar_curso(self):
        try:
            nome_curso = str(self.input_cursos_nome.get())
        
            self.input_cursos_nome.delete(0, tk.END)

            if (len(nome_curso) == 0):
                return
            
            self.cursor.execute("SELECT id FROM cursos WHERE nome = %s", (nome_curso,))
            if (self.cursor.fetchone() != None):
                print("curso ja existe")
                return

            id = random.randint(0, 100000)

            print(id, nome_curso)

            self.table_cursos.insert("", tk.END, values=(id, nome_curso, "🗑️"))

            self.cursor.execute("INSERT INTO cursos(id, nome) VALUES (%s, %s)", (id, nome_curso))
            self.conexao.commit()

            self.atualizar_lista_cursos()
        except (TypeError, ValueError):
            messagebox.showerror("Error", "Dados inseridos são inválidos")
        except:
            messagebox.showerror("Error", "Error ao adicionar curso")

    def remover_curso(self, id):
        try:
            self.cursor.execute("DELETE FROM cursos WHERE id = %s", (id,))
            self.conexao.commit()

            self.preencher_tabela_alunos()
        except:
            messagebox.showerror("Error", "Erro ao remover curso")

    def editar_curso(self, id, column_id, row_id, value):
        values = []

        for item_id in self.table_cursos.get_children():
            values = list(self.table_cursos.item(item_id, 'values'))
            if (values and values[0] == id):
                values[int(column_id[1:]) - 1] = value
                self.table_cursos.item(row_id, values=tuple(values))

        try:
            self.cursor.execute("UPDATE cursos SET nome = %s WHERE id = %s", (values[1], id,))
            self.conexao.commit()
        except:
            messagebox.showerror("Error", "Erro ao tentar atualizar curso")
            self.conexao.rollback()

        self.atualizar_lista_cursos()

    def adicionar_notas(self):
        try:
            aluno_matricula = int(self.selected_option_matricula.get())
            nota = float(self.input_notas_nota.get())

            self.input_notas_nota.delete(0, tk.END)

            aluno_id = self.matricula_aluno_para_id_aluno(aluno_matricula)

            print(aluno_matricula, aluno_id, nota)

            self.cursor.execute("SELECT id FROM alunos WHERE id = %s", (aluno_id, ))
            if (self.cursor.fetchone() == None):
                print("Aluno inexistente")
                return
        
            if (float(nota) < 0 or float(nota) > 10):
                print("Insira uma nota válida!")
                return

            id = random.randint(0, 100000)

            self.table_notas.insert("", tk.END, values=(id, aluno_id, nota, "🗑️"))

            self.cursor.execute("INSERT INTO notas(id, aluno_id, nota) VALUES (%s, %s, %s)", (id, aluno_id, nota))
            self.conexao.commit()
        except (TypeError, ValueError):
            messagebox.showerror("Error", "Dados inseridos são inválidos")
        except:
            messagebox.showerror("Error", "Error ao adicionar nota")

    def remover_nota_pelo_aluno_id(self, aluno_id):
        for item_id in self.table_notas.get_children():
            values = self.table_notas.item(item_id, 'values')
            if (values and values[1] == aluno_id):
                self.table_notas.delete(item_id)

    def remover_nota(self, id):
        try:
            self.cursor.execute("DELETE FROM notas WHERE id = %s", (id,))
            self.conexao.commit()
        except:
            messagebox.showerror("Error", "Erro ao remover nota")

    def editar_nota(self, id, column_id, row_id, value):
        values = []

        for item_id in self.table_notas.get_children():
            values = list(self.table_notas.item(item_id, 'values'))
            if (values and values[0] == id):
                values[int(column_id[1:]) - 1] = value
                self.table_notas.item(row_id, values=tuple(values))

        try:
            self.cursor.execute("UPDATE notas SET aluno_id = %s, nota = %s WHERE id = %s", (values[1], values[2], id,))
            self.conexao.commit()
        except:
            messagebox.showerror("Error", "Erro ao tentar atualizar nota")
            self.conexao.rollback()

    #
    #Funções de suporte
    #
    def listar_cursos(self):
        self.cursor.execute("SELECT nome FROM cursos")
        nome_cursos = self.cursor.fetchall()

        lista = []
        for nome_curso in nome_cursos:
            lista.append(nome_curso[0])

        return lista
    
    def listar_alunos_matricula(self):
        self.cursor.execute("SELECT matricula FROM alunos")
        matricula_alunos = self.cursor.fetchall()

        lista = []
        for matricula_aluno in matricula_alunos:
            lista.append(matricula_aluno[0])

        return lista

    def curso_nome_para_curso_id(self, nome_curso):
        self.cursor.execute("SELECT id FROM cursos WHERE nome = %s", (nome_curso, ))
        return self.cursor.fetchone()[0]
    
    def matricula_aluno_para_id_aluno(self, matricula):
        self.cursor.execute("SELECT id FROM alunos WHERE matricula = %s", (matricula,))
        return self.cursor.fetchone()[0]

    #
    #Funções para atualizar o widget OptionMenu
    #Toda vez que um aluno ou curso é adicionado, é preciso atualizar a lista de matrícula e lista de curso
    #
    def atualizar_lista_matriculas(self):
        matricula_alunos = self.listar_alunos_matricula()
        self.input_notas_aluno_id['menu'].delete(0, 'end')
        for option in matricula_alunos:
            self.input_notas_aluno_id['menu'].add_command(label=option, command=lambda value=option: self.selected_option_matricula.set(value))
        
    def atualizar_lista_cursos(self):
        nome_cursos = self.listar_cursos()
        self.input_alunos_curso['menu'].delete(0, 'end')
        for option in nome_cursos:
            self.input_alunos_curso['menu'].add_command(label=option, command=lambda value=option: self.selected_option_curso.set(value))

    #
    #Função para fechar a conexão com o banco de dados. Executada no final do programa
    #
    def fechar_conexao(self):
        self.conexao.close()

#
#Criação a interface em si
#
root = tk.Tk()
application = Application(root)
root.mainloop()
application.fechar_conexao()
