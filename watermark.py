import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import os
from PIL import Image, ImageTk

# Fungsi untuk menambahkan watermark menggunakan RAID dan DCT
def add_watermark(image_path, watermark_text):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    watermark = np.zeros_like(image, dtype=np.uint8)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2
    color = (255, 255, 255)
    thickness = 5
    text_size = cv2.getTextSize(watermark_text, font, font_scale, thickness)[0]
    
    text_x = (watermark.shape[1] - text_size[0]) // 2
    text_y = (watermark.shape[0] + text_size[1]) // 2
    cv2.putText(watermark, watermark_text, (text_x, text_y), font, font_scale, color, thickness)
    
    # DCT
    image_dct = cv2.dct(np.float32(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)))
    watermark_dct = cv2.dct(np.float32(cv2.cvtColor(watermark, cv2.COLOR_BGR2GRAY)))
    
    alpha = 0.1
    combined_dct = image_dct + alpha * watermark_dct
    watermarked_image = cv2.idct(combined_dct)
    
    # Normalisasi nilai agar berada di antara 0 dan 255
    watermarked_image = cv2.normalize(watermarked_image, None, 0, 255, cv2.NORM_MINMAX)
    watermarked_image = np.uint8(watermarked_image)
    
    return cv2.cvtColor(watermarked_image, cv2.COLOR_GRAY2BGR)

# Fungsi untuk menyimpan gambar dengan watermark
def save_image(image, save_path):
    cv2.imwrite(save_path, image)

# Fungsi untuk menampilkan watermark
def detect_watermark(image_path):
    # Implementasi sederhana deteksi watermark (dapat dioptimalkan sesuai kebutuhan)
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    return image

# Fungsi untuk memeriksa perubahan pada gambar
def detect_changes(original_image_path, watermarked_image_path):
    original = cv2.imread(original_image_path, cv2.IMREAD_COLOR)
    watermarked = cv2.imread(watermarked_image_path, cv2.IMREAD_COLOR)
    
    if original.shape != watermarked.shape:
        return False
    
    diff = cv2.absdiff(original, watermarked)
    non_zero_count = np.count_nonzero(diff)
    
    return non_zero_count == 0

# GUI dengan tkinter
class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Image Watermarking")
        self.root.geometry("500x450")

        # Background image setup
        self.background_image = Image.open("bg.jpeg")  # Replace with your background image path
        self.background_image = self.background_image.resize((2000, 1500), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        self.background_label = tk.Label(self.root, image=self.background_photo)
        self.background_label.place(relwidth=1, relheight=1)

        self.frame = tk.Frame(root, padx=20, pady=20, bg="#ffffff", highlightbackground="#dddddd", highlightthickness=1)
        self.frame.pack(expand=True, pady=20)

        self.upload_btn = tk.Button(self.frame, text="Upload Image", command=self.upload_image, font=("Helvetica", 12, "bold"), width=25, bg="#007acc", fg="white")
        self.upload_btn.pack(pady=10)

        self.watermark_label = tk.Label(self.frame, text="Enter Watermark Text:", font=("Helvetica", 10), bg="#ffffff")
        self.watermark_label.pack(pady=10)

        self.watermark_entry = tk.Entry(self.frame, width=30, font=("Helvetica", 10), bd=2)
        self.watermark_entry.pack(pady=10)

        self.add_watermark_btn = tk.Button(self.frame, text="Add Watermark", command=self.add_watermark, font=("Helvetica", 12, "bold"), width=25, bg="#007acc", fg="white")
        self.add_watermark_btn.pack(pady=10)

        self.download_btn = tk.Button(self.frame, text="Download Watermarked Image", command=self.download_image, font=("Helvetica", 12, "bold"), width=25, bg="#007acc", fg="white")
        self.download_btn.pack(pady=10)

        self.detect_btn = tk.Button(self.frame, text="Detect Watermark", command=self.detect_watermark, font=("Helvetica", 12, "bold"), width=25, bg="#007acc", fg="white")
        self.detect_btn.pack(pady=10)

        self.check_change_btn = tk.Button(self.frame, text="Check Image Changes", command=self.check_changes, font=("Helvetica", 12, "bold"), width=25, bg="#007acc", fg="white")
        self.check_change_btn.pack(pady=10)

        self.image_path = None
        self.watermarked_image = None

    def upload_image(self):
        self.image_path = filedialog.askopenfilename()
        if self.image_path:
            messagebox.showinfo("Image Uploaded", "Image uploaded successfully!")

    def add_watermark(self):
        if self.image_path:
            watermark_text = self.watermark_entry.get()
            self.watermarked_image = add_watermark(self.image_path, watermark_text)
            messagebox.showinfo("Watermark Added", "Watermark added successfully!")
        else:
            messagebox.showwarning("No Image", "Please upload an image first!")

    def download_image(self):
        if self.watermarked_image is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", ".png"), ("All files", ".*")])
            if save_path:
                save_image(self.watermarked_image, save_path)
                messagebox.showinfo("Image Saved", "Watermarked image saved successfully!")
        else:
            messagebox.showwarning("No Watermarked Image", "Please add a watermark to an image first!")

    def detect_watermark(self):
        if self.image_path:
            detected_image = detect_watermark(self.image_path)
            cv2.imshow("Detected Watermark", detected_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            messagebox.showwarning("No Image", "Please upload an image first!")

    def check_changes(self):
        if self.image_path and self.watermarked_image is not None:
            temp_path = "temp_watermarked.png"
            save_image(self.watermarked_image, temp_path)
            unchanged = detect_changes(self.image_path, temp_path)
            os.remove(temp_path)
            if unchanged:
                messagebox.showinfo("No Changes", "No changes detected in the image.")
            else:
                messagebox.showwarning("Changes Detected", "Changes detected in the image.")
        else:
            messagebox.showwarning("No Images", "Please upload an image and add a watermark first!")

if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()
