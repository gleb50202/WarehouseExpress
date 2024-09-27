import tkinter as tk
from tkinter import messagebox

def show_info(title, message):
    return messagebox.askyesno(title, message)

def show_error(title, message):
    messagebox.showerror(title, message)