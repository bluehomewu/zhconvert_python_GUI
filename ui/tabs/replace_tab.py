# ui/tabs/replace_tab.py
import customtkinter


class ReplaceTab:

    def __init__(self, tab, save_callback, clear_callback):
        self.tab = tab

        self.placeholder_color = ("gray50", "gray50")
        self.normal_color = customtkinter.ThemeManager.theme["CTkTextbox"]["text_color"]

        self.placeholders = {
            "protect": "你可以在此輸入字詞來保護它們不被轉換，\n一行寫一個字詞。",
            "pre": "你可以在此輸入「路飛=魯夫」來進行自訂取代，\n一行寫一種取代。",
            "post": "你可以在此輸入「路飛=魯夫」來進行自訂取代，\n一行寫一種取代。",
        }

        # --- 介面佈局 (與之前相同) ---
        top_frame = customtkinter.CTkFrame(self.tab, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(5, 10))
        top_frame.grid_columnconfigure(1, weight=1)

        flow_text = "繁化姬的執行流程為： 輸入 → 保護字詞 → 轉換前取代 → 繁化姬轉換 → 轉換後取代 → 還原保護字詞 → 輸出"
        flow_label = customtkinter.CTkLabel(
            top_frame, text=flow_text, fg_color=("#e3eef9", "#212d3a"), corner_radius=6
        )
        flow_label.grid(row=0, column=0, padx=(0, 10), pady=10, ipady=10, sticky="w")

        save_button = customtkinter.CTkButton(
            top_frame, text="儲存設定", command=save_callback
        )
        save_button.grid(row=0, column=2, padx=5, pady=10)
        clear_button = customtkinter.CTkButton(
            top_frame,
            text="清除設定",
            command=clear_callback,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
        )
        clear_button.grid(row=0, column=3, padx=5, pady=10)

        content_frame = customtkinter.CTkFrame(self.tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        content_frame.grid_columnconfigure((0, 1, 2), weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        self.protect_replace_textbox = self._create_column(
            content_frame, 0, "保護字詞", "#3a7ebf", self.placeholders["protect"]
        )
        self.pre_replace_textbox = self._create_column(
            content_frame, 1, "轉換前取代", "#5f6b7b", self.placeholders["pre"]
        )
        self.post_replace_textbox = self._create_column(
            content_frame, 2, "轉換後取代", "#5f6b7b", self.placeholders["post"]
        )

    def _create_column(self, parent, col_index, title, header_color, placeholder_text):
        column_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        column_frame.grid(
            row=0, column=col_index, padx=(0, 10 if col_index < 2 else 0), sticky="nsew"
        )
        column_frame.grid_rowconfigure(1, weight=1)
        column_frame.grid_columnconfigure(0, weight=1)

        header_frame = customtkinter.CTkFrame(
            column_frame, fg_color=header_color, corner_radius=6
        )
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = customtkinter.CTkLabel(
            header_frame, text=title, font=customtkinter.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")

        textbox = customtkinter.CTkTextbox(
            column_frame, font=("Arial", 14), corner_radius=6, border_width=1
        )
        textbox.grid(row=1, column=0, pady=(5, 0), sticky="nsew")

        # --- 核心修改：綁定新的事件組合 ---
        textbox.insert("1.0", placeholder_text)
        textbox.configure(text_color=self.placeholder_color)

        # 1. <KeyPress> 事件：當使用者按下任何鍵時觸發
        textbox.bind(
            "<KeyPress>",
            lambda event, widget=textbox, placeholder=placeholder_text: self._on_key_press(
                widget, placeholder
            ),
        )

        # 2. <FocusOut> 事件：當使用者離開時，檢查是否需要復原提示文字
        textbox.bind(
            "<FocusOut>",
            lambda event, widget=textbox, placeholder=placeholder_text: self._on_focus_out(
                widget, placeholder
            ),
        )

        # 3. 清空按鈕的指令也需要更新
        clear_button = customtkinter.CTkButton(
            header_frame,
            text="清空",
            width=60,
            fg_color=("#dbdbdb", "#4a4d50"),
            text_color=("#1f1f1f", "#d9d9d9"),
            command=lambda t=textbox, p=placeholder_text: self._clear_textbox(t, p),
        )
        clear_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        return textbox

    # --- 新增/修改：事件處理函式 ---

    def _on_key_press(self, widget, placeholder):
        """當使用者開始打字時觸發"""
        # 只有在文字是提示文字時，才執行清空和變色
        if widget.cget("text_color") == self.placeholder_color:
            widget.delete("1.0", "end")
            widget.configure(text_color=self.normal_color)

    def _on_focus_out(self, widget, placeholder):
        """當使用者離開文字框時觸發"""
        # 如果使用者離開時，文字框是空的，則復原提示文字
        if not widget.get("1.0", "end-1c"):
            widget.configure(text_color=self.placeholder_color)
            widget.insert("1.0", placeholder)

    def _clear_textbox(self, widget, placeholder):
        """清空按鈕的指令，清空後復原提示文字"""
        widget.delete("1.0", "end")
        self._on_focus_out(widget, placeholder)  # 呼叫 on_focus_out 來復原提示

    # --- 智慧內容取得函式 ---

    def get_content(self, widget, placeholder):
        """取得文字框的真實內容，如果內容是提示文字，則回傳空字串"""
        # 使用 text_color 來判斷是否為提示文字，這比比較字串更可靠
        if widget.cget("text_color") == self.placeholder_color:
            return ""
        return widget.get("1.0", "end-1c")
