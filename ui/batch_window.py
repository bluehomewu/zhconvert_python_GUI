# ui/batch_window.py
import customtkinter
import threading
import os
from tkinter import filedialog, messagebox
from pathlib import Path
from api_client import convert_text_online


class BatchWindow(customtkinter.CTkToplevel):
    def __init__(self, master_app):
        super().__init__(master_app)
        self.master_app = master_app

        self.title("批次轉換檔案")
        self.geometry("600x500")
        self.resizable(False, False)

        try:
            self.after(
                200,
                lambda: (
                    self.iconbitmap(master_app.icon_path)
                    if hasattr(master_app, "icon_path") and master_app.icon_path
                    else None
                ),
            )
        except:
            pass

        self.input_files = []
        self.output_dir = ""

        self.grid_columnconfigure(1, weight=1)

        # 1. 選擇輸入檔案
        customtkinter.CTkLabel(self, text="輸入檔案:").grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="w"
        )
        self.files_label = customtkinter.CTkLabel(
            self, text="尚未選擇任何檔案", fg_color="transparent", anchor="w"
        )
        self.files_label.grid(row=0, column=1, padx=10, pady=(20, 10), sticky="ew")
        customtkinter.CTkButton(
            self, text="選擇檔案...", command=self._select_files
        ).grid(row=0, column=2, padx=20, pady=(20, 10))

        # 2. 選擇輸出資料夾
        customtkinter.CTkLabel(self, text="輸出資料夾:").grid(
            row=1, column=0, padx=20, pady=10, sticky="w"
        )
        self.dir_label = customtkinter.CTkLabel(
            self, text="尚未選擇 (預設為原檔案位置)", fg_color="transparent", anchor="w"
        )
        self.dir_label.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        customtkinter.CTkButton(
            self, text="選擇目錄...", command=self._select_output_dir
        ).grid(row=1, column=2, padx=20, pady=10)

        # 3. 轉換模式 (下拉選單)
        customtkinter.CTkLabel(self, text="轉換模式:").grid(
            row=2, column=0, padx=20, pady=10, sticky="w"
        )

        # 從主視窗的 MainTab 取得所有可用的轉換選項 (顯示名稱)
        converter_options = list(self.master_app.main_tab.conversion_options.keys())

        self.converter_menu = customtkinter.CTkOptionMenu(
            self, values=converter_options
        )
        self.converter_menu.grid(
            row=2, column=1, columnspan=2, padx=20, pady=10, sticky="ew"
        )

        # 設定預設值為主視窗目前選中的模式
        current_api_name = self.master_app.main_tab.current_converter
        # 反查顯示名稱以設定預設值
        for name, api in self.master_app.main_tab.conversion_options.items():
            if api == current_api_name:
                self.converter_menu.set(name)
                break

        customtkinter.CTkLabel(
            self,
            text="(提示：批次轉換將套用主視窗目前所有的偏好設定與模組)",
            text_color="gray",
        ).grid(row=3, column=0, columnspan=3, padx=20, pady=(0, 20))

        # 4. 開始按鈕
        self.start_button = customtkinter.CTkButton(
            self,
            text="開始批次轉換",
            height=40,
            font=customtkinter.CTkFont(size=16, weight="bold"),
            command=self._start_batch_thread,
        )
        self.start_button.grid(
            row=4, column=0, columnspan=3, padx=20, pady=10, sticky="ew"
        )

        # 5. 進度顯示
        self.progress_label = customtkinter.CTkLabel(self, text="準備就緒")
        self.progress_label.grid(
            row=5, column=0, columnspan=3, padx=20, pady=(10, 5), sticky="ew"
        )
        self.progress_bar = customtkinter.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.grid(
            row=6, column=0, columnspan=3, padx=20, pady=10, sticky="ew"
        )

        # --- 關鍵修改：使用 transient 方法 ---
        # 這告訴視窗管理器：BatchWindow 是 master_app 的附屬視窗
        # 結果：BatchWindow 會永遠浮在 master_app 上面，但不會擋住其他應用程式
        self.transient(self.master_app)

        # 提升層級並取得焦點
        self.lift()
        self.focus()

    def _select_files(self):
        filepaths = filedialog.askopenfilenames(
            title="選擇要轉換的文字檔案",
            filetypes=(
                ("Text files", "*.txt;*.md;*.log;*.json;*.xml;*.odt;*.srt;*.ass;*.vtt"),
                ("All files", "*.*"),
            ),
        )
        if filepaths:
            self.input_files = filepaths
            self.files_label.configure(text=f"已選擇 {len(self.input_files)} 個檔案")

    def _select_output_dir(self):
        dirpath = filedialog.askdirectory(title="選擇儲存轉換後檔案的資料夾")
        if dirpath:
            self.output_dir = dirpath
            self.dir_label.configure(text=dirpath)

    def _start_batch_thread(self):
        if not self.input_files:
            messagebox.showwarning("警告", "請先選擇要轉換的檔案。")
            return

        self.start_button.configure(state="disabled", text="轉換中...")
        self.progress_bar.set(0)

        thread = threading.Thread(target=self._run_batch_conversion, daemon=True)
        thread.start()

    def _run_batch_conversion(self):
        total_files = len(self.input_files)
        success_count = 0

        base_payload = self.master_app._build_payload()

        selected_display_name = self.converter_menu.get()
        selected_api_name = self.master_app.main_tab.conversion_options[
            selected_display_name
        ]

        base_payload["converter"] = selected_api_name

        for i, filepath_str in enumerate(self.input_files):
            filepath = Path(filepath_str)
            self.after(
                0,
                self.progress_label.configure,
                {"text": f"正在處理 ({i+1}/{total_files}): {filepath.name} ..."},
            )

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                current_payload = base_payload.copy()
                current_payload["text"] = content

                result = convert_text_online(current_payload)

                if isinstance(result, dict):
                    converted_text = result.get("text", "")

                    if self.output_dir:
                        out_dir = Path(self.output_dir)
                    else:
                        out_dir = filepath.parent

                    output_filename = f"{filepath.stem}_converted{filepath.suffix}"
                    output_path = out_dir / output_filename

                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(converted_text)

                    success_count += 1
                else:
                    print(f"Convert failed for {filepath.name}: {result}")

            except Exception as e:
                print(f"Error processing {filepath.name}: {e}")

            progress = (i + 1) / total_files
            self.after(0, self.progress_bar.set, progress)

        self.after(
            0,
            self.progress_label.configure,
            {"text": f"完成！成功轉換 {success_count} / {total_files} 個檔案。"},
        )
        self.after(
            0, self.start_button.configure, {"state": "normal", "text": "開始批次轉換"}
        )
        self.after(
            0,
            lambda: messagebox.showinfo(
                "完成", f"批次轉換完成\n成功: {success_count}\n總數: {total_files}"
            ),
        )
