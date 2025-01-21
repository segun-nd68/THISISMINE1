"""
Author: Belov Roman Andreevich
Created on: 2025-01-15
License: MIT (if applicable)

"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from enum import Enum
from datetime import datetime
import json
import os

class NoteCategory(Enum):
    """
    Перечисление для категорий заметок.
    Каждая категория будет представлена строкой, определяющей тип заметки.
    """
    WORK = "Работа"
    HOME = "Дом"
    HEALTH = "Здоровье и Спорт"
    PEOPLE = "Люди"
    DOCUMENTS = "Документы"
    FINANCE = "Финансы"
    MISC = "Разное"

class Note:
    """
    Класс для представления заметки.
    Каждая заметка имеет название, категорию, содержимое, а также дату создания и последнего изменения.
    """
    def __init__(self, title="Без названия", category=NoteCategory.MISC, content=""):
        """
        Конструктор для инициализации заметки.
        title: строка с названием заметки.
        category: категория заметки (по умолчанию "Разное").
        content: текстовое содержимое заметки.
        """
        self.title = title[:50]  # Ограничение длины названия до 50 символов.
        self.category = category  # Категория заметки.
        self.content = content  # Содержимое заметки.
        self.created_at = datetime.now()  # Время создания заметки.
        self.updated_at = self.created_at  # Время последнего изменения, по умолчанию равно времени создания.

    def update(self, title=None, category=None, content=None):
        """
        Обновление существующей заметки.
        Параметры title, category, content могут быть None, если они не требуют изменения.
        Обновляется также время последнего изменения.
        """
        if title:
            self.title = title[:50]  # Обновление названия, если передано новое значение.
        if category:
            self.category = category  # Обновление категории.
        if content:
            self.content = content  # Обновление содержимого.
        self.updated_at = datetime.now()  # Обновление времени последнего изменения.

    def to_dict(self):
        """
        Преобразование заметки в словарь для сериализации в JSON.
        """
        return {
            "title": self.title,
            "category": self.category.value,  # Сохраняем строковое представление категории.
            "content": self.content,
            "created_at": self.created_at.isoformat(),  # Дата создания в формате ISO.
            "updated_at": self.updated_at.isoformat()  # Дата последнего изменения в формате ISO.
        }

    @classmethod
    def from_dict(cls, data):
        """
        Создание заметки из словаря, полученного при загрузке из файла.
        """
        note = cls(
            title=data["title"],
            category=NoteCategory(data["category"]),  # Преобразуем строку обратно в категорию.
            content=data["content"]
        )
        note.created_at = datetime.fromisoformat(data["created_at"])  # Преобразуем строку в объект datetime.
        note.updated_at = datetime.fromisoformat(data["updated_at"])  # Преобразуем строку в объект datetime.
        return note

class Project:
    """
    Класс для представления проекта, который содержит список заметок.
    """
    def __init__(self):
        self.notes = []  # Список заметок в проекте.

    def add_note(self, note):
        """Добавление заметки в проект."""
        self.notes.append(note)

    def remove_note_by_index(self, index):
        """Удаление заметки по индексу."""
        if 0 <= index < len(self.notes):
            del self.notes[index]  # Удаляем заметку по указанному индексу.

    def to_dict(self):
        """Преобразование проекта в словарь для сериализации в JSON."""
        return {"notes": [note.to_dict() for note in self.notes]}  # Преобразуем все заметки в список словарей.

    @classmethod
    def from_dict(cls, data):
        """Создание проекта из словаря, полученного при загрузке из файла."""
        project = cls()
        project.notes = [Note.from_dict(note_data) for note_data in data["notes"]]  # Преобразуем каждый элемент в объект Note.
        return project

class ProjectManager:
    """
    Класс для управления сохранением и загрузкой проекта из файла.
    """
    FILE_PATH = os.path.join(os.path.expanduser("~"), "Documents", "NoteApp.notes")  # Путь к файлу для сохранения данных проекта.

    @staticmethod
    def save_project(project):
        """Сохранение проекта в файл в формате JSON."""
        with open(ProjectManager.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(project.to_dict(), f, ensure_ascii=False, indent=4)  # Сериализация проекта в JSON с отступами для читаемости.

    @staticmethod
    def load_project():
        """Загрузка проекта из файла."""
        if os.path.exists(ProjectManager.FILE_PATH):  # Проверяем, существует ли файл.
            with open(ProjectManager.FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)  # Загружаем данные из файла в формате JSON.
                return Project.from_dict(data)  # Преобразуем данные в объект проекта.
        return Project()  # Если файл не существует, возвращаем новый пустой проект.

class NoteApp:
    """
    Основной класс приложения для работы с заметками.
    """
    def __init__(self, root):
        self.root = root  # Главное окно приложения.
        self.root.title("NoteApp")  # Заголовок окна.

        # Загрузка проекта из файла.
        self.project = ProjectManager.load_project()
        self.current_note_index = None  # Индекс текущей выбранной заметки.

        # Настройка пользовательского интерфейса.
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        self.left_frame = tk.Frame(self.root)  # Левый фрейм для списка заметок и кнопок.
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = tk.Frame(self.root)  # Правый фрейм для отображения содержания заметки.
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Список заметок.
        self.notes_listbox = tk.Listbox(self.left_frame)
        self.notes_listbox.pack(fill=tk.BOTH, expand=True)
        self.notes_listbox.bind("<<ListboxSelect>>", self.display_note)  # Связываем выбор заметки с функцией отображения.

        # Кнопки для добавления, редактирования и удаления заметок.
        self.add_button = tk.Button(self.left_frame, text="Add Note", command=self.add_note)
        self.add_button.pack(fill=tk.X)

        self.edit_button = tk.Button(self.left_frame, text="Edit Note", command=self.edit_note)
        self.edit_button.pack(fill=tk.X)

        self.remove_button = tk.Button(self.left_frame, text="Remove Note", command=self.remove_note)
        self.remove_button.pack(fill=tk.X)

        # Метки и поля для отображения содержания выбранной заметки.
        self.note_title_label = tk.Label(self.right_frame, text="Title:", font=("Arial", 14))
        self.note_title_label.pack(anchor=tk.W)

        self.note_content_text = tk.Text(self.right_frame, state=tk.DISABLED, wrap=tk.WORD)
        self.note_content_text.pack(expand=True, fill=tk.BOTH)

        # Главное меню с пунктами для выхода, добавления, редактирования и удаления заметок.
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(self.menu, tearoff=0)
        edit_menu.add_command(label="Add Note", command=self.add_note)
        edit_menu.add_command(label="Edit Note", command=self.edit_note)
        edit_menu.add_command(label="Remove Note", command=self.remove_note)
        self.menu.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(self.menu, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menu.add_cascade(label="Help", menu=help_menu)

        self.refresh_notes_list()  # Обновляем список заметок в интерфейсе.

    def add_note_dialog(self, note=None):
        """
        Диалоговое окно для добавления или редактирования заметки.
        Если note передано, то будет редактирование.
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Note" if note else "Add Note")

        # Ввод названия заметки.
        tk.Label(dialog, text="Title:").pack()
        title_entry = tk.Entry(dialog)
        title_entry.pack(fill=tk.X)

        # Выбор категории заметки.
        tk.Label(dialog, text="Category:").pack()
        category_var = tk.StringVar(value=NoteCategory.MISC.value)
        category_menu = tk.OptionMenu(dialog, category_var, *[cat.value for cat in NoteCategory])
        category_menu.pack(fill=tk.X)

        # Ввод текста заметки.
        tk.Label(dialog, text="Content:").pack()
        content_text = tk.Text(dialog, height=10)
        content_text.pack(fill=tk.BOTH, expand=True)

        # Если это редактирование, то заполняем поля текущими значениями.
        if note:
            title_entry.insert(0, note.title)
            category_var.set(note.category.value)
            content_text.insert(1.0, note.content)

        def save():
            """
            Сохранение новой или отредактированной заметки.
            """
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Title cannot be empty!")
                return

            if len(title) > 50:
                messagebox.showerror("Error", "Title cannot exceed 50 characters!")
                return

            category = NoteCategory(category_var.get())  # Преобразуем выбранную категорию в объект enum.
            content = content_text.get(1.0, tk.END).strip()  # Текст заметки.

            if note:
                note.update(title=title, category=category, content=content)  # Обновление заметки.
            else:
                new_note = Note(title=title, category=category, content=content)  # Создание новой заметки.
                self.project.add_note(new_note)

            ProjectManager.save_project(self.project)  # Сохранение проекта в файл.
            self.refresh_notes_list()  # Обновление списка заметок.
            dialog.destroy()  # Закрытие окна редактирования.

        # Кнопки для подтверждения или отмены действия.
        tk.Button(dialog, text="OK", command=save).pack(side=tk.LEFT)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

    def add_note(self):
        """Открыть диалог для добавления новой заметки."""
        self.add_note_dialog()

    def edit_note(self):
        """Открыть диалог для редактирования выбранной заметки."""
        if self.current_note_index is None:
            messagebox.showwarning("Warning", "No note selected!")
            return
        self.add_note_dialog(self.project.notes[self.current_note_index])

    def remove_note(self):
        """Удаление выбранной заметки."""
        if self.current_note_index is None:
            messagebox.showwarning("Warning", "No note selected!")
            return

        note = self.project.notes[self.current_note_index]
        confirm = messagebox.askyesno("Confirm", f"Do you really want to remove this note: {note.title}?")
        if confirm:
            self.project.remove_note_by_index(self.current_note_index)
            self.current_note_index = None
            ProjectManager.save_project(self.project)
            self.refresh_notes_list()

    def display_note(self, event=None):
        """Отображение содержания выбранной заметки."""
        selected = self.notes_listbox.curselection()  # Получаем выбранный элемент в списке.
        if not selected:
            return

        index = selected[0]  # Индекс выбранной заметки.
        self.current_note_index = index  # Запоминаем индекс текущей заметки.
        note = self.project.notes[index]  # Извлекаем заметку по индексу.

        self.note_title_label.config(text=f"Title: {note.title}")  # Отображаем название заметки.
        self.note_content_text.config(state=tk.NORMAL)
        self.note_content_text.delete(1.0, tk.END)
        self.note_content_text.insert(1.0, note.content)  # Заполняем текстовое поле содержимым заметки.
        self.note_content_text.config(state=tk.DISABLED)

    def refresh_notes_list(self):
        """Обновление списка заметок в интерфейсе."""
        self.notes_listbox.delete(0, tk.END)  # Очищаем список.
        for note in self.project.notes:  # Добавляем заметки в список.
            self.notes_listbox.insert(tk.END, f"{note.title} ({note.category.value})")

    def show_about(self):
        """Показать информацию о приложении в диалоговом окне."""
        messagebox.showinfo("About", "NoteApp\nVersion 1.0\nDeveloped with Python and Tkinter.")

if __name__ == "__main__":
    root = tk.Tk()  # Создаем главное окно приложения.
    app = NoteApp(root)  # Инициализируем приложение.
    root.mainloop()  # Запускаем главный цикл приложения.

