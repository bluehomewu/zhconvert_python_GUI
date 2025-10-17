# ui/main_window.py
import customtkinter
import threading
import json
import sys  # 引入 sys 模組
import os   # 引入 os 模組
from pathlib import Path
from tkinter import messagebox
from api_client import convert_text_online
from ui.tabs.main_tab import MainTab
from ui.tabs.preferences_tab import PreferencesTab
from ui.tabs.replace_tab import ReplaceTab
from ui.tabs.modules_tab import ModulesTab
from ui.tabs.summary_tab import SummaryTab

def resource_path(relative_path):
    """
    取得資源的絕對路徑，無論是作為腳本執行還是作為打包後的 .exe 執行。
    """
    try:
        # PyInstaller 建立一個臨時資料夾，並將路徑儲存在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是打包後執行，則使用普通的相對路徑
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class App(customtkinter.CTk):

    def __init__(self, service_info: dict):
        super().__init__()
        self.service_info = service_info
        self.title("繁化姬桌面版")
        self.geometry("1200x900")
        # 確保您的圖示檔案 (例如 'favicon.ico') 與 main.py 放在同一個目錄下
        try:
            icon_path = resource_path("./pictures/favicon/favicon.ico")
            self.iconbitmap(icon_path)
        except Exception as e:
            # 如果找不到圖示檔案或格式不對，打印一個錯誤訊息但不會讓程式崩潰
            print(f"Error setting icon: {e}")

        self.settings_file = Path("zhconvert_settings.json")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.tab_view = customtkinter.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        for name in ["轉換", "偏好設定", "自訂取代", "詞語模組", "轉換總結"]:
            self.tab_view.add(name)

        self.main_tab = MainTab(self.tab_view.tab("轉換"), self.service_info,
                                self.start_conversion_thread)
        self.preferences_tab = PreferencesTab(self.tab_view.tab("偏好設定"),
                                              self.service_info)
        self.replace_tab = ReplaceTab(self.tab_view.tab("自訂取代"),
                                      save_callback=self._save_settings,
                                      clear_callback=self._clear_settings)
        self.modules_tab = ModulesTab(self.tab_view.tab("詞語模組"),
                                      self.service_info,
                                      save_callback=self._save_settings,
                                      clear_callback=self._clear_settings)
        self.summary_tab = SummaryTab(self.tab_view.tab("轉換總結"),
                                      self.service_info)

        self._load_settings()

    # --- 關鍵修改：徹底重構 payload 的組裝方式 ---
    def _build_payload(self) -> dict:
        payload = {
            'text': self.main_tab.input_textbox.get("1.0", "end-1c").strip(),
            'converter': self.main_tab.current_converter
        }

        prefs = self.preferences_tab

        # 1. 讀取所有核取方塊，並直接合併到 payload 中
        payload.update({
            key: True
            for key, var in prefs.preferences_vars.items() if var.get() == "on"
        })

        # 2. 讀取所有下拉選單，並直接合併到 payload 中
        payload.update({
            'jpTextConversionStrategy':
            prefs.jp_text_strategy_menu.get(),
            'jpStyleConversionStrategy':
            prefs.jp_style_strategy_menu.get(),
            'translateTabsToSpaces':
            int(prefs.translate_tabs_menu.get()),
            'diffContextLines':
            int(prefs.diff_context_menu.get()),
            'diffTemplate':
            prefs.diff_template_menu.get()
        })

        # 3. 讀取字幕樣式，並直接加入 payload
        if jp_styles := self.main_tab.jp_styles_entry.get().strip():
            payload['jpTextStyles'] = jp_styles
        if ignore_styles := self.main_tab.ignore_styles_entry.get().strip():
            payload['ignoreTextStyles'] = ignore_styles

        # 4. 讀取「隱藏不重要差異」文字框，並直接加入 payload
        if tedious_text := prefs.tedious_keywords_textbox.get(
                "1.0", "end-1c").strip():
            payload['userTediousKeywords'] = tedious_text

        # 5. 讀取自訂取代，並直接加入 payload
        repl_tab = self.replace_tab
        if protect := repl_tab.get_content(repl_tab.protect_replace_textbox,
                                           repl_tab.placeholders["protect"]):
            payload['userProtectReplace'] = protect
        if pre := repl_tab.get_content(repl_tab.pre_replace_textbox,
                                       repl_tab.placeholders["pre"]):
            payload['userPreReplace'] = pre
        if post := repl_tab.get_content(repl_tab.post_replace_textbox,
                                        repl_tab.placeholders["post"]):
            payload['userPostReplace'] = post

        # 6. 讀取模組設定，並直接加入 payload
        status_map = {"自動": -1, "啟用": 1, "停用": 0}
        modules_payload_dict = {
            api: status_map[menu.get()]
            for api, menu in self.modules_tab.module_menus.items()
            if menu.get() != "自動"
        }
        if modules_payload_dict:
            payload['modules'] = json.dumps(modules_payload_dict)

        return payload

    # --- 其他函式均無需修改 ---
    def perform_conversion(self):
        payload = self._build_payload()
        result = "請先輸入要轉換的文字。" if not payload.get(
            'text') else convert_text_online(payload)
        if isinstance(result, dict):
            self.after(0, self.update_output_text, result.get('text', ''))
            self.after(0, self.summary_tab.update_content, result)
            self.after(100, self.tab_view.set, "轉換總結")
        else:
            self.after(0, self.update_output_text, result)

    def _load_settings(self):
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    repl_tab = self.replace_tab
                    if protect_text := settings.get("userProtectReplace", ""):
                        repl_tab.protect_replace_textbox.delete("1.0", "end")
                        repl_tab.protect_replace_textbox.insert(
                            "1.0", protect_text)
                        repl_tab.protect_replace_textbox.configure(
                            text_color=repl_tab.normal_color)
                    if pre_text := settings.get("userPreReplace", ""):
                        repl_tab.pre_replace_textbox.delete("1.0", "end")
                        repl_tab.pre_replace_textbox.insert("1.0", pre_text)
                        repl_tab.pre_replace_textbox.configure(
                            text_color=repl_tab.normal_color)
                    if post_text := settings.get("userPostReplace", ""):
                        repl_tab.post_replace_textbox.delete("1.0", "end")
                        repl_tab.post_replace_textbox.insert("1.0", post_text)
                        repl_tab.post_replace_textbox.configure(
                            text_color=repl_tab.normal_color)
                    mod_tab = self.modules_tab
                    status_map_rev = {"-1": "自動", "0": "停用", "1": "啟用"}
                    if saved_modules := settings.get("modules", {}):
                        for api_name, status in saved_modules.items():
                            if api_name in mod_tab.module_menus:
                                mod_tab.module_menus[api_name].set(
                                    status_map_rev.get(str(status), "自動"))
        except Exception as e:
            print(f"Error loading settings: {e}")

    def _save_settings(self):
        try:
            repl_tab = self.replace_tab
            settings = {
                "userProtectReplace":
                repl_tab.get_content(repl_tab.protect_replace_textbox,
                                     repl_tab.placeholders["protect"]),
                "userPreReplace":
                repl_tab.get_content(repl_tab.pre_replace_textbox,
                                     repl_tab.placeholders["pre"]),
                "userPostReplace":
                repl_tab.get_content(repl_tab.post_replace_textbox,
                                     repl_tab.placeholders["post"])
            }
            mod_tab = self.modules_tab
            status_map = {"自動": -1, "啟用": 1, "停用": 0}
            modules_to_save = {
                api_name: status_map[menu.get()]
                for api_name, menu in mod_tab.module_menus.items()
                if menu.get() != ("停用" if mod_tab.service_info['modules'].
                                  get(api_name, {}).get('isManual') else "自動")
            }
            if modules_to_save: settings["modules"] = modules_to_save
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("成功", "設定已成功儲存！")
        except Exception as e:
            messagebox.showerror("錯誤", f"儲存設定時發生錯誤:\n{e}")

    def _clear_settings(self):
        if messagebox.askyesno("確認清除",
                               "您確定要清除所有自訂取代和詞語模組設定嗎？\n此操作將會刪除已儲存的設定檔。"):
            try:
                repl_tab = self.replace_tab
                repl_tab._clear_textbox(repl_tab.protect_replace_textbox,
                                        repl_tab.placeholders["protect"])
                repl_tab._clear_textbox(repl_tab.pre_replace_textbox,
                                        repl_tab.placeholders["pre"])
                repl_tab._clear_textbox(repl_tab.post_replace_textbox,
                                        repl_tab.placeholders["post"])
                mod_tab = self.modules_tab
                for api_name, menu in mod_tab.module_menus.items():
                    is_manual = mod_tab.service_info['modules'].get(
                        api_name, {}).get('isManual', False)
                    menu.set("停用" if is_manual else "自動")
                if self.settings_file.exists(): self.settings_file.unlink()
                messagebox.showinfo("成功", "設定已清除。")
            except Exception as e:
                messagebox.showerror("錯誤", f"清除設定時發生錯誤:\n{e}")

    def start_conversion_thread(self, converter_name):
        self.main_tab.current_converter = converter_name
        threading.Thread(target=self.perform_conversion, daemon=True).start()

    def update_output_text(self, text):
        self.main_tab.output_textbox.configure(state="normal")
        self.main_tab.output_textbox.delete("1.0", "end")
        self.main_tab.output_textbox.insert("1.0", text)
        self.main_tab.output_textbox.configure(state="disabled")
