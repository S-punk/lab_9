import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import mysql.connector

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.current_db = None

    def connect(self, host, user, password):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
            return "Подключение успешно выполнено"
        except mysql.connector.Error as err:
            return f"Ошибка подключения: {err}"

    def update_databases(self):
        cursor = self.connection.cursor()
        cursor.execute("SHOW DATABASES")
        return [db[0] for db in cursor.fetchall()]

    def use_database(self, db_name):
        cursor = self.connection.cursor()
        cursor.execute(f"USE {db_name}")
        self.current_db = db_name

    def execute_query(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return result, columns
            else:
                self.connection.commit()
                return "Запрос выполнен успешно", None
        except mysql.connector.Error as err:
            return str(err), None

    def create_table(self, db_name, table_name, columns):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {db_name}")
            column_definitions = ", ".join(columns)
            query = f"CREATE TABLE {table_name} ({column_definitions})"
            cursor.execute(query)
            return "Таблица успешно создана"
        except mysql.connector.Error as err:
            return f"Ошибка создания таблицы: {err}"

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления базами данных")
        self.root.configure(bg="#0A2840")
        self.db_manager = DatabaseManager()

        self.actions_log = []
        self.setup_ui()

    def setup_ui(self):
        # Цветовая схема
        bg_color = "#0A2840"
        button_color = "#AAB0C8"
        text_color = "#FFFFFF"
        highlight_color = "#D19A17"
        log_bg_color = "#CED1E0"

        # Верхние кнопки
        button_frame = tk.Frame(self.root, bg=bg_color)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        for text, command in [("\u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0438\u0442\u044c\u0441\u044f", self.connect_to_db),
                              ("\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0431\u0430\u0437\u0443 \u0434\u0430\u043d\u043d\u044b\u0445", self.create_database),
                              ("\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0442\u0430\u0431\u043b\u0438\u0446\u0443", self.create_table)]:
            tk.Button(button_frame, text=text, command=command, 
                      bg=button_color, fg=text_color, activebackground=highlight_color).pack(side=tk.LEFT, padx=5, pady=5)

        # Левое меню
        self.tree_frame = tk.Frame(self.root, bg=bg_color)
        self.tree_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.db_tree = ttk.Treeview(self.tree_frame)
        self.db_tree.pack(fill=tk.BOTH, expand=True)
        self.db_tree.bind("<ButtonRelease-1>", self.on_tree_select)

        # Правая часть
        self.right_frame = tk.Frame(self.root, bg=bg_color)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.query_text = tk.Text(self.right_frame, height=5, bg=log_bg_color, fg=text_color)
        self.query_text.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(self.right_frame, text="\u0412\u044b\u043f\u043e\u043b\u043d\u0438\u0442\u044c \u0437\u0430\u043f\u0440\u043e\u0441", 
                  command=self.execute_query, bg=highlight_color, fg="black").pack(pady=5)

        self.result_frame = tk.Frame(self.right_frame)
        self.result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = ttk.Treeview(self.result_frame, show="headings")
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.bind("<Button-1>", self.prevent_edit)

        # Лог действий
        self.log_frame = tk.Frame(self.root, bg=bg_color)
        self.log_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(self.log_frame, text="\u041b\u043e\u0433 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0439", bg=bg_color, fg=text_color).pack()
        self.log_text = tk.Text(self.log_frame, state="disabled", width=30, bg=log_bg_color, fg="black")
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def prevent_edit(self, event):
        return "break"

    def log_action(self, action):
        self.actions_log.append(action)
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, action + "\n")
        self.log_text.config(state="disabled")


    def connect_to_db(self):
        host = self.show_dialog("Подключение", "Введите хост:")
        user = self.show_dialog("Подключение", "Введите имя пользователя:")
        password = self.show_dialog("Подключение", "Введите пароль:", show="*")

        result = self.db_manager.connect(host, user, password)
        messagebox.showinfo("Результат", result)
        self.log_action(f"Подключение к MySQL: {result}")
        self.update_db_tree()

    def update_db_tree(self):
        self.db_tree.delete(*self.db_tree.get_children())
        databases = self.db_manager.update_databases()

        for db in databases:
            db_id = self.db_tree.insert("", "end", text=db, open=False)
            cursor = self.db_manager.connection.cursor()
            cursor.execute(f"SHOW TABLES FROM {db}")
            tables = cursor.fetchall()
            for table in tables:
                self.db_tree.insert(db_id, "end", text=table[0])

    def on_tree_select(self, event):
        selected_item = self.db_tree.selection()[0]
        selected_text = self.db_tree.item(selected_item, "text")

        if selected_text in self.db_manager.update_databases():
            self.db_manager.use_database(selected_text)
            self.display_current_db()
        else:
            self.show_table_contents(selected_text)

    def display_current_db(self):
        current_db_label = tk.Label(self.root, text=f"Текущая база данных: {self.db_manager.current_db}")
        current_db_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.log_action(f"Выбрана база данных: {self.db_manager.current_db}")

    def show_table_contents(self, table_name):
        query = f"SELECT * FROM {table_name}"
        result, columns = self.db_manager.execute_query(query)
        self.display_result(result, columns)

    def display_result(self, result, columns):
        for col in self.result_text.get_children():
            self.result_text.delete(col)
        self.result_text.config(columns=columns)

        for col in columns:
            self.result_text.heading(col, text=col)
            self.result_text.column(col, width=max(100, len(col) * 10))

        if isinstance(result, str):
            self.log_action(f"Ошибка: {result}")
            messagebox.showerror("Ошибка", result)
        else:
            for row in result:
                self.result_text.insert("", "end", values=row)

    def create_database(self):
        db_name = self.show_dialog("Создание базы данных", "Введите имя базы данных:")
        if not db_name:
            messagebox.showerror("Ошибка", "Имя базы данных не может быть пустым!")
            return

        query = f"CREATE DATABASE {db_name}"
        result, _ = self.db_manager.execute_query(query)
        messagebox.showinfo("Результат", result)
        self.log_action(f"Создание базы данных {db_name}: {result}")
        self.update_db_tree()

    def create_table(self):
        db_name = self.show_dialog("Выбор базы данных", "Введите имя базы данных:")
        if not db_name:
            messagebox.showerror("Ошибка", "Имя базы данных не может быть пустым!")
            return

        table_name = self.show_dialog("Создание таблицы", "Введите имя таблицы:")
        if not table_name:
            messagebox.showerror("Ошибка", "Имя таблицы не может быть пустым!")
            return

        try:
            column_count = int(self.show_dialog("Количество столбцов", "Введите количество столбцов:"))
        except ValueError:
            messagebox.showerror("Ошибка", "Количество столбцов должно быть числом!")
            return

        columns = []
        for i in range(column_count):
            column_name = self.show_dialog(f"Столбец {i + 1}", "Введите имя столбца:")
            if not column_name:
                messagebox.showerror("Ошибка", f"Имя столбца {i + 1} не может быть пустым!")
                return

            column_type = self.show_dialog(f"Тип данных столбца {i + 1}", "Введите тип данных (например, INT, VARCHAR(255)):")
            if not column_type:
                messagebox.showerror("Ошибка", f"Тип данных столбца {i + 1} не может быть пустым!")
                return

            properties = []
            if messagebox.askyesno(f"Столбец {i + 1}", "Сделать PRIMARY KEY?"):
                properties.append("PRIMARY KEY")
            if messagebox.askyesno(f"Столбец {i + 1}", "NOT NULL?"):
                properties.append("NOT NULL")
            if messagebox.askyesno(f"Столбец {i + 1}", "UNIQUE?"):
                properties.append("UNIQUE")
            if messagebox.askyesno(f"Столбец {i + 1}", "AUTO_INCREMENT?"):
                properties.append("AUTO_INCREMENT")

            column_definition = f"{column_name} {column_type} {' '.join(properties)}"
            columns.append(column_definition)

        result = self.db_manager.create_table(db_name, table_name, columns)
        messagebox.showinfo("Результат", result)
        self.log_action(f"Создание таблицы {table_name} в базе {db_name}: {result}")
        self.update_db_tree()

    def execute_query(self):
        query = self.query_text.get(1.0, tk.END).strip()
        if not query:
            messagebox.showerror("Ошибка", "Запрос не может быть пустым!")
            return

        result, columns = self.db_manager.execute_query(query)
        self.log_action(f"Выполнение запроса: {query}")
        self.display_result(result, columns)

    def show_dialog(self, title, prompt, show=None):
        dialog = tk.Toplevel(self.root)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.title(title)

        tk.Label(dialog, text=prompt).pack(pady=10)
        entry = tk.Entry(dialog, show=show)
        entry.pack(pady=5, padx=10)

        def on_submit():
            self.result = entry.get()
            dialog.destroy()

        tk.Button(dialog, text="OK", command=on_submit).pack(pady=10)

        self.root.wait_window(dialog)
        return getattr(self, 'result', '')

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()
