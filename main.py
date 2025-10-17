# main.py
import customtkinter
import tkinter as tk
from tkinter import messagebox
from api_client import fetch_service_info
from ui.main_window import App

if __name__ == "__main__":
    # 使用一個短暫的 customtkinter 視窗作為載入提示
    # 這樣可以確保在主應用程式啟動前，字體和縮放已經初始化
    loading_window = customtkinter.CTk()
    loading_window.geometry("300x100")
    loading_window.title("載入中")
    loading_window.resizable(False, False)
    customtkinter.CTkLabel(loading_window,
                           text="正在從伺服器獲取最新設定...",
                           font=("", 14)).pack(pady=20, expand=True)

    # 強制更新視窗，然後執行 API 請求
    loading_window.update()
    service_info = fetch_service_info()

    # 銷毀載入視窗
    loading_window.destroy()

    # 根據 API 結果決定下一步
    if service_info:
        # 如果成功，啟動主應用程式
        app = App(service_info)
        app.mainloop()
    else:
        # 如果失敗，使用標準 tkinter 顯示錯誤訊息後退出
        # 這樣做更穩定，即使 customtkinter 初始化有問題也能顯示錯誤
        root = tk.Tk()
        root.withdraw()  # 隱藏空的 tkinter 主視窗
        messagebox.showerror("啟動失敗", "無法從繁化姬伺服器獲取設定。\n請檢查您的網路連線或稍後再試。")
