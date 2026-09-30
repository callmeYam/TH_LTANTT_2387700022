import tkinter as tk
from tkinter import filedialog
from securecrypto import aes_utils

def encrypt():
    file = filedialog.askopenfilename()
    if not file:
        return
    pw = password_entry.get()
    key = aes_utils.encrypt_file_aes(file, pw)
    result_label.config(text=f"Key: {key}")

def decrypt():
    file = filedialog.askopenfilename()
    if not file:
        return
    pw = password_entry.get()
    out = aes_utils.decrypt_file_aes(file, pw)
    result_label.config(text=f"Output: {out}")

root = tk.Tk()
root.title("SecureCrypto GUI")
root.geometry("450x180")

tk.Label(root, text="Password / Base64 Key:").pack(pady=5)
password_entry = tk.Entry(root, show="*", width=45)
password_entry.pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Encrypt", width=12, command=encrypt).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Decrypt", width=12, command=decrypt).pack(side=tk.LEFT, padx=5)

result_label = tk.Label(root, text="", wraplength=420)
result_label.pack(pady=10)

if __name__ == '__main__':
    root.mainloop()
