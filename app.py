"""
Tela do robô de agendamento.

Rodar em modo desenvolvimento:   python app.py
Gerar executável:                pyinstaller --onefile --windowed --name AgendamentoVazios app.py
"""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

from main import realizar_agendamento, salvar_em_files

FORMATO_DATA = '%d/%m/%Y %H:%M'  # ex.: 30/09/2026 14:30


# ---------------------------------------------------------------------------
# Funções chamadas pelos botões
# ---------------------------------------------------------------------------

def escolher_arquivo(variavel):
    """Abre a janela do sistema para escolher um PDF e guarda o caminho na variável."""
    caminho = filedialog.askopenfilename(
        title='Selecione o arquivo',
        filetypes=[('PDF', '*.pdf'), ('Todos os arquivos', '*.*')],
    )
    if caminho:  # se o usuário cancelar, vem vazio
        variavel.set(caminho)


def ler_data(texto, nome_campo):
    """Converte o texto digitado em datetime. Se o formato estiver errado, gera um erro claro."""
    try:
        return datetime.strptime(texto.strip(), FORMATO_DATA)
    except ValueError:
        raise ValueError(f'"{nome_campo}" inválida. Use o formato dd/mm/aaaa hh:mm')


def clicar_agendar():
    """Valida os campos e dispara o robô."""
    minuta = var_minuta.get()
    booking = var_booking.get()

    if not minuta or not booking:
        messagebox.showwarning('Atenção', 'Selecione os dois arquivos.')
        return

    try:
        data_1 = ler_data(var_data_1.get(), 'Data e hora 1')
        data_2 = ler_data(var_data_2.get(), 'Data e hora 2')
    except ValueError as erro:
        messagebox.showwarning('Atenção', str(erro))
        return

    botao_agendar.config(state='disabled', text='Agendando...')

    # O robô demora. Se rodasse aqui direto, a janela "congelaria" até terminar.
    # Por isso ele roda numa thread (uma tarefa paralela) e a tela continua respondendo.
    threading.Thread(
        target=executar_robo,
        args=(minuta, booking, data_1, data_2),
        daemon=True,  # a thread morre se a janela for fechada
    ).start()


def executar_robo(minuta, booking, data_1, data_2):
    """Roda na thread paralela."""
    try:
        # Guarda uma cópia dos arquivos em files/ e passa a usar essas cópias.
        minuta, booking = salvar_em_files(minuta, booking)

        realizar_agendamento(minuta, booking, data_1, data_2)
        resultado = ('info', 'Agendamento realizado com sucesso!')
    except Exception as erro:
        resultado = ('erro', f'Falha no agendamento:\n{erro}')

    # Regra do tkinter: só a thread principal pode mexer na tela.
    # "after(0, ...)" pede para a thread principal executar a função assim que puder.
    janela.after(0, finalizar, resultado)


def finalizar(resultado):
    tipo, mensagem = resultado
    if tipo == 'info':
        messagebox.showinfo('Pronto', mensagem)
    else:
        messagebox.showerror('Erro', mensagem)
    botao_agendar.config(state='normal', text='Agendar')


# ---------------------------------------------------------------------------
# Montagem da tela
# ---------------------------------------------------------------------------

janela = tk.Tk()
janela.title('Agendamento de Vazios')
janela.resizable(False, False)

# StringVar é uma "caixinha" ligada ao campo: quando o campo muda, ela muda também.
var_minuta = tk.StringVar()
var_booking = tk.StringVar()
var_data_1 = tk.StringVar(value=datetime.now().strftime(FORMATO_DATA))
var_data_2 = tk.StringVar(value=datetime.now().strftime(FORMATO_DATA))

# grid = organiza em linhas (row) e colunas (column), como uma tabela.
# padx/pady = espaçamento em pixels.

# Linha 0 e 1: arquivos
tk.Label(janela, text='Minuta:').grid(row=0, column=0, sticky='w', padx=10, pady=5)
tk.Entry(janela, textvariable=var_minuta, width=50, state='readonly').grid(row=0, column=1, padx=5)
tk.Button(janela, text='Procurar...', command=lambda: escolher_arquivo(var_minuta)).grid(row=0, column=2, padx=10)

tk.Label(janela, text='Booking:').grid(row=1, column=0, sticky='w', padx=10, pady=5)
tk.Entry(janela, textvariable=var_booking, width=50, state='readonly').grid(row=1, column=1, padx=5)
tk.Button(janela, text='Procurar...', command=lambda: escolher_arquivo(var_booking)).grid(row=1, column=2, padx=10)

# Linha 2 e 3: datas
tk.Label(janela, text='Data e hora 1:').grid(row=2, column=0, sticky='w', padx=10, pady=5)
tk.Entry(janela, textvariable=var_data_1, width=20).grid(row=2, column=1, sticky='w', padx=5)

tk.Label(janela, text='Data e hora 2:').grid(row=3, column=0, sticky='w', padx=10, pady=5)
tk.Entry(janela, textvariable=var_data_2, width=20).grid(row=3, column=1, sticky='w', padx=5)

tk.Label(janela, text='Formato: dd/mm/aaaa hh:mm', fg='gray').grid(row=4, column=1, sticky='w', padx=5)

# Linha 5: botão
botao_agendar = tk.Button(janela, text='Agendar', width=20, command=clicar_agendar)
botao_agendar.grid(row=5, column=0, columnspan=3, pady=15)

# mainloop = mantém a janela aberta, esperando cliques. Tudo acima só "monta" a tela.
janela.mainloop()
