import tkinter as tk
from tkinter import ttk, messagebox
import psutil

def load_process_list(filter_pid=None, filter_name=None):
    for row in tree.get_children():
        tree.delete(row)
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
        try:
            memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
            pid_match = filter_pid is None or str(proc.info['pid']) == filter_pid
            name_match = filter_name is None or filter_name.lower() in proc.info['name'].lower()
            if pid_match or name_match:
                tree.insert("", tk.END, values=(
                    proc.info['pid'],
                    proc.info['name'],
                    f"{proc.info['cpu_percent']}%",
                    f"{memory_mb:.2f} MB",
                    proc.info['status']
                ))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def get_selected_pid():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Seleccione un proceso")
        return None
    return tree.item(selected_item, 'values')[0]

def kill_process():
    pid = get_selected_pid()
    if pid:
        try:
            psutil.Process(int(pid)).terminate()
            load_process_list()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo terminar el proceso: {e}")

def suspend_process():
    pid = get_selected_pid()
    if pid:
        try:
            psutil.Process(int(pid)).suspend()
            load_process_list()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo suspender el proceso: {e}")

def resume_process():
    pid = get_selected_pid()
    if pid:
        try:
            psutil.Process(int(pid)).resume()
            load_process_list()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reanudar el proceso: {e}")

def search_process():
    query = entry_search.get().strip()
    if not query:
        load_process_list()
        return

    if query.isdigit():
        load_process_list(filter_pid=query)
    else:
        load_process_list(filter_name=query)

def show_all_processes():
    entry_search.delete(0, tk.END)
    load_process_list()

# Crear ventana principal
root = tk.Tk()
root.title("Monitor de Procesos")
root.configure(bg="#f5f5f5")

# Estilo para los botones
button_style = {
    'width': 15,
    'bg': '#4CAF50',
    'fg': 'white',
    'relief': 'flat',
    'font': ('Arial', 10, 'bold'),
    'padx': 10,
    'pady': 5
}

# Entrada y botón de búsqueda
frame_search = tk.Frame(root, bg="#f5f5f5")
frame_search.pack(pady=5)

tk.Label(frame_search, text="Buscar por PID o Nombre:", bg="#f5f5f5", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
entry_search = tk.Entry(frame_search, font=('Arial', 10), width=30)
entry_search.pack(side=tk.LEFT, padx=5)

tk.Button(frame_search, text="Buscar", command=search_process, **button_style).pack(side=tk.LEFT, padx=5)
tk.Button(frame_search, text="Mostrar todos", command=show_all_processes, **button_style).pack(side=tk.LEFT, padx=5)

# Tabla de procesos
columns = ("PID", "Nombre", "CPU %", "Memoria", "Estado")
tree = ttk.Treeview(root, columns=columns, show="headings", height=8)
tree.pack(pady=10, fill=tk.BOTH, expand=True)

for i, col in enumerate(columns):
    tree.heading(col, text=col, anchor=tk.W)
    tree.column(col, width=130, anchor=tk.W)

# Botones de control
frame_buttons = tk.Frame(root, bg="#f5f5f5")
frame_buttons.pack(pady=5)

tk.Button(frame_buttons, text="Finalizar", command=kill_process, **button_style).pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="Suspender", command=suspend_process, **button_style).pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="Reanudar", command=resume_process, **button_style).pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="Actualizar", command=lambda: load_process_list(), **button_style).pack(side=tk.LEFT, padx=5)

# Cargar lista de procesos al iniciar
load_process_list()

# Ajustar ancho automático y alto fijo
root.update_idletasks()
fixed_width = root.winfo_reqwidth()
fixed_height = 700
root.geometry(f"{fixed_width}x{fixed_height}")
root.resizable(False, False)

# Ejecutar aplicación
root.mainloop()
