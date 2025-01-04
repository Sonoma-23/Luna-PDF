import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import fitz  # PyMuPDF for rendering PDF pages as images


class LunaPDF:
    def __init__(self, root):
        self.root = root
        self.root.title("Luna PDF")
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)

        # PDF Variables
        self.pdf_document = None
        self.total_pages = 0
        self.current_page = 0
        self.zoom_level = 1.0
        self.cache = {}

        # UI Elements
        self.create_menu_bar()
        self.create_canvas()
        self.bind_shortcuts()
        self.bind_mouse_events()

        # Scrolling Throttle
        self.scroll_delay = 100  # Milliseconds
        self.last_scroll_time = 0

    def create_menu_bar(self):
        menu_bar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.quit)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="View Controls", command=self.show_help)

        # View Menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=lambda: self.zoom(1.2))
        view_menu.add_command(label="Zoom Out", command=lambda: self.zoom(0.8))
        view_menu.add_command(label="Center PDF", command=self.center_pdf)

        # Add menus to the menu bar
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="View", menu=view_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, bg="gray", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.configure(scrollregion=(0, 0, 0, 0))

    def bind_shortcuts(self):
        self.root.bind("<Control-=>", lambda event: self.zoom(1.2))  # Ctrl + =
        self.root.bind("<Control-minus>", lambda event: self.zoom(0.8))  # Ctrl + -
        self.root.bind("i", lambda event: self.zoom(1.2))  # Zoom In (I key)
        self.root.bind("o", lambda event: self.zoom(0.8))  # Zoom Out (O key)
        self.root.bind("c", lambda event: self.center_pdf())  # Center PDF (C key)
        self.root.bind("<Left>", lambda event: self.change_page(-1))  # Left Arrow
        self.root.bind("<Right>", lambda event: self.change_page(1))  # Right Arrow

    def bind_mouse_events(self):
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_canvas)
        self.canvas.bind("<MouseWheel>", self.scroll_canvas)  # For Windows
        self.canvas.bind("<Button-4>", self.scroll_canvas)  # For Linux (Scroll Up)
        self.canvas.bind("<Button-5>", self.scroll_canvas)  # For Linux (Scroll Down)

    def start_drag(self, event):
        self.drag_start = (event.x, event.y)

    def drag_canvas(self, event):
        if hasattr(self, "drag_start"):
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.drag_start = (event.x, event.y)
            self.canvas.move("page", dx, dy)

    def scroll_canvas(self, event):
        """Adjust scroll sensitivity using a time-based throttle."""
        from time import time

        current_time = time() * 1000  # Convert to milliseconds
        if current_time - self.last_scroll_time < self.scroll_delay:
            return
        self.last_scroll_time = current_time

        direction = -1 if event.num in [4, 5] or event.delta > 0 else 1
        self.change_page(direction)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            try:
                self.pdf_document = fitz.open(file_path)
                self.total_pages = len(self.pdf_document)
                self.current_page = 0
                self.cache = {}
                self.zoom_level = 1.0
                self.display_page()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF: {e}")

    def cache_page(self, page_num):
        if page_num not in self.cache:
            page = self.pdf_document[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom_level, self.zoom_level))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            self.cache[page_num] = ImageTk.PhotoImage(img)
        return self.cache[page_num]

    def display_page(self):
        if self.pdf_document and 0 <= self.current_page < self.total_pages:
            image = self.cache_page(self.current_page)
            self.canvas.delete("all")
            self.canvas.create_image(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                anchor="center",
                image=image,
                tags="page",
            )
            self.root.title(f"Luna PDF - Page {self.current_page + 1} of {self.total_pages}")
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def zoom(self, factor):
        self.zoom_level *= factor
        self.cache = {}
        self.display_page()

    def center_pdf(self):
        self.zoom_level = 1.0
        self.display_page()

    def change_page(self, direction):
        new_page = self.current_page + direction
        if 0 <= new_page < self.total_pages:
            self.current_page = new_page
            self.display_page()

    def show_help(self):
        help_text = """
Luna PDF Controls:
- Open: Ctrl + O
- Zoom In: Ctrl + = or I
- Zoom Out: Ctrl + - or O
- Next Page: Right Arrow
- Previous Page: Left Arrow
- Center PDF: C
Why Luna PDF? 
A simple, fast, and elegant PDF reader built to prioritize ease of use.
"""
        messagebox.showinfo("Help - Luna PDF", help_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = LunaPDF(root)
    root.mainloop()
