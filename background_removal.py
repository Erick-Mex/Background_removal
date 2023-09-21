import customtkinter as ct
from tkinter import messagebox
from rembg import remove
from PIL import Image
import os

ct.set_appearance_mode("light")
ct.set_default_color_theme("blue")

script_dir = os.path.dirname(os.path.abspath(__file__))
relative_image_path = "image\\icon_image.png"
absolute_img_path = os.path.join(script_dir, relative_image_path)


new_window_available = True

def resize_image(img: Image.Image) -> tuple[int, int]:
    max_dimension = 400
    w, h = img.size

    if w > h:
        new_w = max_dimension
        new_h = int(max_dimension * h / w)
    else:
        new_h = max_dimension
        new_w = int(max_dimension * w / h)

    return new_w, new_h

class NewWindow(ct.CTkToplevel):
    def __init__(self, master: ct.CTk = None, img_path = None):
        super().__init__()

        self.title(f"background removed")
        self.geometry("480x480")
        self.resizable(False, False)

        self.downloable_image = None
        self.name: str = os.path.basename(img_path)[:-4]

        img = self.process_image(img_path)
        self.image_display = ct.CTkLabel(self, text="", image=img)
        self.image_display.pack(padx=10, pady=10)

        self.button_downloader = ct.CTkButton(self, text="Descargar Imagen", height=36, command=self.download_image)
        self.button_downloader.pack(padx=10, pady=10, fill='x', side="bottom")
    
        self.protocol("WM_DELETE_WINDOW", self.check_window_status)
    
    def check_window_status(self):
        global new_window_available
        new_window_available = True
        self.destroy()
    
    def process_image(self, img_path):
        img = Image.open(img_path)
        if img.format == 'PNG' and img.mode != 'RGBA':
            img = img.convert("RGBA")
        output = remove(img)
        self.downloable_image = output
        w, h = resize_image(output)
        output = output.resize((w, h), Image.LANCZOS)
        output = ct.CTkImage(light_image=output, size=(w, h))
        img.close()
        return output

    def download_image(self):
        save_path = ct.filedialog.asksaveasfilename(initialfile=f"{self.name.replace(' ', '_')}_background_removed",title="Guardar imagen", defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if save_path:
            self.downloable_image.save(save_path)

class App(ct.CTk):
    def __init__(self):
        super().__init__()

        self.title("Quitar Fondo de Imagenes")
        self.geometry("600x600")
        self.resizable(False, False)
        self.rowconfigure(index=0, weight=1)
        self.columnconfigure(index=0, weight=1)

        self.filepath = None

        self.create_window()
    
    def create_window(self):
        self.frame = ct.CTkFrame(master=self)
        self.frame.grid(row=0, column=0, pady=20, padx=10, sticky="nsew")
        self.frame.columnconfigure([0,1], weight=2)
        self.frame.rowconfigure(1, weight=2)

        self.icon_image = ct.CTkImage(Image.open(absolute_img_path))

        self.button_file = ct.CTkButton(master=self.frame, text="Cargar Imagen", image=self.icon_image, height=36, command=self.upload_image)
        self.button_file.grid(row=0, column=0, padx=15, pady=10, columnspan=2, sticky="ew")

        self.image_display = ct.CTkLabel(self.frame, text="")
        self.image_display.grid(row=1, column=0, columnspan=2)

        self.button_remove_background = ct.CTkButton(self.frame, text="Previsualizar", height=42, command=self.preview_image, state='disabled')
        self.button_remove_background.grid(row=2, column=0, padx=15, pady=10, columnspan=2, sticky="ew")

    def upload_image(self):
        self.filepath = ct.filedialog.askopenfilename(filetypes=[("Image files (*.jpg *.jpeg *.png)", "*.jpg *.jpeg *.png")])

        img = Image.open(self.filepath)
        if img.format == 'PNG' and img.mode != 'RGBA':
            img = img.convert("RGBA")
        w, h = resize_image(img)
        img = img.resize((w, h), Image.LANCZOS) # Cambiar la imagen a dimensiones de 400 de ancho o alto
        photo = ct.CTkImage(light_image=img, size=(w,h))

        self.image_display.configure(image=photo) # Insertar la imagen seleccionada
        self.button_remove_background.configure(state="normal") # Desbloquear el boton para la preview de la imagen
        img.close()
    
    def preview_image(self):
        global new_window_available

        if self.filepath is not None:
            if new_window_available is not True:
                messagebox.showwarning("Ventana en ejecucion", "La ventana de previsualizacion sigue abierta")
                return
            new_window_available = False
            NewWindow(self, self.filepath)

if __name__ == "__main__":
    app = App()
    app.mainloop()