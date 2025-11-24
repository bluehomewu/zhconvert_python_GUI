# main.py
import customtkinter
import tkinter as tk
from tkinter import messagebox
from api_client import fetch_service_info
from ui.main_window import App
import sys
import os


def hide_console():
    """
    在 Windows 系統上隱藏/釋放控制台視窗。
    """
    if sys.platform.startswith("win"):
        import ctypes

        try:
            # FreeConsole 會將目前的行程與控制台視窗「斷開連結」。
            # 如果該控制台視窗是專門為此程式開啟的（例如直接點擊 .exe），它就會關閉。
            # 如果是從現有 CMD 執行的，它會釋放控制權，讓 CMD 回到輸入狀態。
            ctypes.windll.kernel32.FreeConsole()
        except Exception as e:
            print(f"無法關閉控制台: {e}")


if __name__ == "__main__":
    # 1. 顯示連線訊息 (此時 Terminal 還在)
    print("正在連線繁化姬伺服器...")
    print("請稍候...")

    service_info = fetch_service_info()

    # 2. 根據 API 結果決定下一步
    if service_info:
        # --- 關鍵修改：成功後，立刻關閉 Terminal ---
        hide_console()

        # 啟動主程式
        app = App(service_info)
        app.mainloop()
    else:
        # 如果失敗，這裡不要關閉 Console，這樣使用者或許還能看到報錯訊息
        # 或者您也可以選擇在這裡也隱藏 Console，只顯示彈出視窗

        root = tk.Tk()
        root.overrideredirect(1)
        root.withdraw()

        messagebox.showerror(
            "啟動失敗", "無法從繁化姬伺服器取得設定。\n請檢查您的網路連線或稍後再試。"
        )

        root.destroy()
        sys.exit(1)
