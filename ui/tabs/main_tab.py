# ui/tabs/main_tab.py
import customtkinter
import pyperclip


class MainTab:

    def __init__(self, tab, service_info, start_conversion_callback):
        self.tab = tab
        self.service_info = service_info
        self.start_conversion_callback = start_conversion_callback
        self.current_converter = "Traditional"  # 預設轉換模式
        self.converter_buttons = []

        # --- 關鍵修改：使用 uniform 選項來強制等寬 ---
        # 我們為第 0 欄和第 1 欄設定了相同的 uniform 群組名稱 "col_group"
        # 這會強制它們的寬度始終保持一致。
        self.tab.grid_columnconfigure(0, weight=1, uniform="col_group")
        self.tab.grid_columnconfigure(1, weight=1, uniform="col_group")

        self.tab.grid_rowconfigure(0, weight=1)  # 上方文字框區域可伸縮
        self.tab.grid_rowconfigure(1, weight=0)  # 下方設定區域固定高度

        # --- 以下程式碼與之前版本完全相同 ---
        self._create_input_block(self.tab, row=0, col=0)
        self._create_output_block(self.tab, row=0, col=1)
        self._create_mode_block(self.tab, row=1, col=0)
        self._create_subtitle_block(self.tab, row=1, col=1)

    def _create_input_block(self, parent, row, col):
        container = customtkinter.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row,
                       column=col,
                       padx=(10, 5),
                       pady=(10, 5),
                       sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        header = self._create_header(container, "轉換前文字",
                                     ("#f3f4f6", "#4b5563"))
        clear_btn = customtkinter.CTkButton(
            header,
            text="清空",
            width=60,
            fg_color=("#dbdbdb", "#4a4d50"),
            text_color=("#1f1f1f", "#d9d9d9"),
            command=lambda: self.input_textbox.delete("1.0", "end"))
        clear_btn.pack(side="right", padx=5)
        self.input_textbox = customtkinter.CTkTextbox(container,
                                                      font=("Arial", 16),
                                                      wrap="word",
                                                      border_width=1,
                                                      corner_radius=0)
        self.input_textbox.grid(row=1, column=0, sticky="nsew")
        self.input_textbox.insert("1.0", "請在此輸入想要進行轉換的文字")
        self.input_textbox.configure(text_color="gray50")
        self.input_textbox.bind("<KeyPress>", self._on_input_keypress)

    def _create_output_block(self, parent, row, col):
        container = customtkinter.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row,
                       column=col,
                       padx=(5, 10),
                       pady=(10, 5),
                       sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        header = self._create_header(container, "轉換後結果",
                                     ("#f3f4f6", "#4b5563"))
        copy_btn = customtkinter.CTkButton(header,
                                           text="複製到剪貼簿",
                                           width=120,
                                           fg_color=("#dbdbdb", "#4a4d50"),
                                           text_color=("#1f1f1f", "#d9d9d9"),
                                           command=self._copy_to_clipboard)
        copy_btn.pack(side="right", padx=5)
        self.output_textbox = customtkinter.CTkTextbox(container,
                                                       font=("Arial", 16),
                                                       wrap="word",
                                                       border_width=1,
                                                       corner_radius=0,
                                                       state="disabled")
        self.output_textbox.grid(row=1, column=0, sticky="nsew")

    def _create_mode_block(self, parent, row, col):
        container = customtkinter.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row,
                       column=col,
                       padx=(10, 5),
                       pady=(5, 10),
                       sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self._create_header(container, "轉換模式", ("#a5c5e9", "#3a7ebf"))
        body = customtkinter.CTkFrame(container,
                                      border_width=1,
                                      corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")

        grouped_converters = {}
        for api_name, conv_data in self.service_info['converters'].items():
            cat_id = conv_data.get('cat', 'misc')
            if cat_id not in grouped_converters:
                grouped_converters[cat_id] = []
            grouped_converters[cat_id].append({'api': api_name, **conv_data})

        for cat_id, conv_list in grouped_converters.items():
            row_frame = customtkinter.CTkFrame(body, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=5)
            for conv in conv_list:
                btn = customtkinter.CTkButton(row_frame,
                                              text=conv['name'],
                                              command=lambda c=conv['api']:
                                              self._on_mode_button_click(c))
                btn.pack(side="left", padx=5)
                self.converter_buttons.append({
                    'api': conv['api'],
                    'button': btn
                })
        self._set_active_converter_visuals(self.current_converter)

    def _create_subtitle_block(self, parent, row, col):
        container = customtkinter.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row,
                       column=col,
                       padx=(5, 10),
                       pady=(5, 10),
                       sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        header = self._create_header(container, "字幕樣式設定",
                                     ("#e9a5a5", "#c14242"))
        body = customtkinter.CTkFrame(container,
                                      border_width=1,
                                      corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)
        jp_frame = customtkinter.CTkFrame(body, fg_color="transparent")
        jp_frame.grid(row=0,
                      column=0,
                      columnspan=2,
                      padx=10,
                      pady=10,
                      sticky="ew")
        jp_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkCheckBox(jp_frame, text="日文樣式").grid(row=0, column=0)
        self.jp_styles_entry = customtkinter.CTkEntry(
            jp_frame, placeholder_text="在此輸入字幕樣式")
        self.jp_styles_entry.grid(row=0, column=1, padx=10, sticky="ew")
        ignore_frame = customtkinter.CTkFrame(body, fg_color="transparent")
        ignore_frame.grid(row=1,
                          column=0,
                          columnspan=2,
                          padx=10,
                          pady=10,
                          sticky="ew")
        ignore_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(ignore_frame, text="不要處理的樣式").grid(row=0,
                                                                  column=0)
        self.ignore_styles_entry = customtkinter.CTkEntry(
            ignore_frame, placeholder_text="在此輸入字幕樣式")
        self.ignore_styles_entry.grid(row=0, column=1, padx=10, sticky="ew")

    def _create_header(self, parent, title, color):
        header = customtkinter.CTkFrame(parent,
                                        fg_color=color,
                                        corner_radius=0,
                                        height=40)
        header.grid(row=0, column=0, sticky="ew")
        title_label = customtkinter.CTkLabel(header,
                                             text=title,
                                             font=customtkinter.CTkFont(
                                                 size=14, weight="bold"))
        title_label.pack(side="left", padx=10)
        return header

    def _set_active_converter_visuals(self, converter_api_name):
        self.current_converter = converter_api_name
        for item in self.converter_buttons:
            if item['api'] == converter_api_name:
                item['button'].configure(fg_color=("#3B8ED0", "#1F6AA5"))
            else:
                item['button'].configure(fg_color=customtkinter.ThemeManager.
                                         theme["CTkButton"]["fg_color"])

    def _on_mode_button_click(self, converter_api_name):
        self._set_active_converter_visuals(converter_api_name)
        self.start_conversion_callback(converter_api_name)

    def _on_input_keypress(self, event):
        if self.input_textbox.cget("text_color") == "gray50":
            self.input_textbox.delete("1.0", "end")
            self.input_textbox.configure(text_color=customtkinter.ThemeManager.
                                         theme["CTkTextbox"]["text_color"])

    def _copy_to_clipboard(self):
        try:
            pyperclip.copy(self.output_textbox.get("1.0", "end-1c"))
            print("Copied to clipboard.")
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
