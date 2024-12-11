import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Архитектурный планировщик")
root.geometry("800x600")

canvas = tk.Canvas(root, bg="white", width=1200, height=800)
canvas.pack(pady=20)

# Доступные элементы для добавления


elements = {
    "Кровать": "D:/лабы/4 курсы/практикум/8 лаба/bed.png",
    "Кухня": "D:/лабы/4 курсы/практикум/8 лаба/kitchen.png",
    "Стол": "D:/лабы/4 курсы/практикум/8 лаба/table.png",
    "Ванна": "D:/лабы/4 курсы/практикум/8 лаба/vanna.png",
    "Диван": "D:/лабы/4 курсы/практикум/8 лаба/sofa.png",
    "Туалет": "D:/лабы/4 курсы/практикум/8 лаба/closet.png",
    "Телевизор": "D:/лабы/4 курсы/практикум/8 лаба/tv.png",
    "Кухня2": "D:/лабы/4 курсы/практикум/8 лаба/kitchen_b.png",
    "Цветок": "D:/лабы/4 курсы/практикум/8 лаба/green.png",
    "Ванна2": "D:/лабы/4 курсы/практикум/8 лаба/vanna_2.png",
}

# Загрузка изображений для элементов
images = {}
for name, path in elements.items():
    if  name == "Туалет":
        img = Image.open(path).resize((70, 70))
    elif name == "Телевизор":
        img = Image.open(path).resize((150, 50))
    elif name == "Цветок":
        img = Image.open(path).resize((25, 25))
    elif name == "Кухня2":
        img = Image.open(path).resize((225, 150))
    elif name == "Ванна":
        img = Image.open(path).resize((150, 70))
    elif name == "Стол":
        img = Image.open(path).resize((150, 70))
    else:
        img = Image.open(path).resize((150, 100))  # Укажите размер по вашему усмотрению
    photo = ImageTk.PhotoImage(img)
    images[name] = photo  # Сохраняем изображения в словаре

# Переменные для рисования областей
start_x = None
start_y = None
room_rectangle = None
colors = ["lightblue", "lightgreen", "lightyellow", "lightcoral", "lightpink"]
current_color_index = 0  # Индекс текущего цвета

def start_draw(event):
    global start_x, start_y, room_rectangle, current_color_index
    start_x = event.x
    start_y = event.y
    color = colors[current_color_index]
    room_rectangle = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="black", fill=color)

def draw(event):
    global room_rectangle
    if room_rectangle is not None:
        canvas.coords(room_rectangle, start_x, start_y, event.x, event.y)

def end_draw(event):
    global start_x, start_y, room_rectangle, current_color_index
    if room_rectangle is not None:
        width = abs(event.x - start_x)
        height = abs(event.y - start_y)
        area = width * height
        canvas.create_text(start_x + width / 2, start_y + height / 2, text=f"Площадь: {round(area/10000, ndigits=2)} м2", fill="black", font=("Arial", 12))

        current_color_index = (current_color_index + 1) % len(colors)

    start_x = None
    start_y = None
    room_rectangle = None

def add_element(event):
    element_name = simpledialog.askstring("Добавить элемент", "Введите название элемента (Кровать, Стол, Кухня, Ванна, Диван):")
    if element_name in elements:
        # Позиции курсора
        x = canvas.winfo_pointerx() - canvas.winfo_rootx()
        y = canvas.winfo_pointery() - canvas.winfo_rooty()
        canvas.create_image(x, y, image=images[element_name], anchor=tk.CENTER)
    else:
        messagebox.showerror("Ошибка", "Элемент не найден")

# Привязываем события для рисования и добавления элементов
canvas.bind("<Button-1>", start_draw)  # Нажатие кнопки мыши для рисования областей
canvas.bind("<B1-Motion>", draw)         # Перемещение при нажатой кнопке
canvas.bind("<ButtonRelease-1>", end_draw)  # Отпускание кнопки мыши для рисования областей
root.bind("f", add_element)  # Нажатие клавиши f для добавления элемента

root.mainloop()
