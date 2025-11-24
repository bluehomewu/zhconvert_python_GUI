# ui/tabs/preferences_tab.py
import customtkinter


class PreferencesTab:

    def __init__(self, tab, service_info):
        self.tab = tab
        self.service_info = service_info
        self.preferences_vars = {}

        self.tab.grid_columnconfigure((0, 1, 2), weight=1, uniform="pref_group")
        self.tab.grid_rowconfigure(0, weight=1)

        self._create_general_column(self.tab, col=0)
        self._create_tidy_column(self.tab, col=1)
        self._create_diff_column(self.tab, col=2)

    def _create_header(self, parent, title):
        header = customtkinter.CTkFrame(
            parent, fg_color=("#a5c5e9", "#3a7ebf"), corner_radius=6
        )
        header.pack(fill="x", padx=1, pady=1)
        title_label = customtkinter.CTkLabel(
            header, text=title, font=customtkinter.CTkFont(size=14, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=8)
        return header

    def _create_general_column(self, parent, col):
        container = customtkinter.CTkFrame(parent, fg_color="transparent")
        container.grid(row=0, column=col, padx=(10, 5), pady=10, sticky="nsew")
        card = customtkinter.CTkFrame(container, border_width=1)
        card.pack(fill="both", expand=True)
        self._create_header(card, "一般設定")
        body = customtkinter.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=10, pady=10)
        jp_strategy_values = ["protect", "protectOnlySameOrigin", "fix", "none"]
        customtkinter.CTkLabel(body, text="一般日文的處理策略").pack(
            anchor="w", pady=(5, 0)
        )
        self.jp_text_strategy_menu = customtkinter.CTkOptionMenu(
            body, values=jp_strategy_values
        )
        self.jp_text_strategy_menu.pack(fill="x", pady=(0, 10))
        self.jp_text_strategy_menu.set("protectOnlySameOrigin")
        customtkinter.CTkLabel(body, text="日文樣式的處理策略").pack(anchor="w")
        self.jp_style_strategy_menu = customtkinter.CTkOptionMenu(
            body, values=jp_strategy_values
        )
        self.jp_style_strategy_menu.pack(fill="x", pady=(0, 20))
        self.jp_style_strategy_menu.set("protectOnlySameOrigin")
        api_server_frame = customtkinter.CTkFrame(body, fg_color="transparent")
        api_server_frame.pack(fill="x", pady=5)
        api_server_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(api_server_frame, text="API 伺服器").grid(
            row=0, column=0, padx=(0, 10)
        )
        self.api_server_entry = customtkinter.CTkEntry(
            api_server_frame, placeholder_text="https://api.zhconvert.org"
        )
        self.api_server_entry.grid(row=0, column=1, sticky="ew")
        api_key_frame = customtkinter.CTkFrame(body, fg_color="transparent")
        api_key_frame.pack(fill="x", pady=5)
        api_key_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(api_key_frame, text="API 金鑰").grid(
            row=0, column=0, padx=(0, 10)
        )
        self.api_key_entry = customtkinter.CTkEntry(api_key_frame, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky="ew")

    def _create_tidy_column(self, parent, col):
        container = customtkinter.CTkFrame(parent, fg_color="transparent")
        container.grid(row=0, column=col, padx=5, pady=10, sticky="nsew")
        card = customtkinter.CTkFrame(container, border_width=1)
        card.pack(fill="both", expand=True)
        self._create_header(card, "整理相關")
        body = customtkinter.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=10, pady=10)
        tidy_options = {
            "cleanUpText": "移除文字中無用的內容",
            "trimTrailingWhiteSpaces": "移除行末的多餘空格",
            "ensureNewlineAtEof": "轉換結果總是以單個空行做為結尾",
            "unifyLeadingHyphen": "統一說話人連字號為半形減號",
        }
        for key, text in tidy_options.items():
            self._add_checkbox(body, key, text)
        tab_frame = customtkinter.CTkFrame(body, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(15, 5))
        tab_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(tab_frame, text="將 Tab 轉換為數個空格").grid(
            row=0, column=0, padx=(0, 10)
        )
        self.translate_tabs_menu = customtkinter.CTkOptionMenu(
            tab_frame, width=80, values=[str(i) for i in range(-1, 9)]
        )
        self.translate_tabs_menu.grid(row=0, column=1, sticky="w")
        self.translate_tabs_menu.set("-1")

    def _create_diff_column(self, parent, col):
        container = customtkinter.CTkFrame(parent, fg_color="transparent")
        container.grid(row=0, column=col, padx=(5, 10), pady=10, sticky="nsew")
        card = customtkinter.CTkFrame(container, border_width=1)
        card.pack(fill="both", expand=True)
        self._create_header(card, "差異比較")
        body = customtkinter.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=10, pady=10)

        diff_options = {
            "diffEnable": "啟用差異比較",
            "diffCharLevel": "使用精確比較模式",
            "diffSmartForLocalization": "使用智慧型在地化差異比較",
            "diffIgnoreCase": "忽略大小寫的差異",
            "diffIgnoreWhiteSpaces": "忽略空格的差異",
        }
        for key, text in diff_options.items():
            self._add_checkbox(body, key, text)

        option_frame = customtkinter.CTkFrame(body, fg_color="transparent")
        option_frame.pack(fill="x", pady=(15, 5))
        option_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(option_frame, text="前後文行數").grid(
            row=0, column=0, padx=(0, 10)
        )
        self.diff_context_menu = customtkinter.CTkOptionMenu(
            option_frame, values=[str(i) for i in range(0, 5)]
        )
        self.diff_context_menu.grid(row=0, column=1, sticky="w")
        self.diff_context_menu.set("1")
        customtkinter.CTkLabel(option_frame, text="輸出樣板").grid(
            row=1, column=0, padx=(0, 10), pady=5
        )
        self.diff_template_menu = customtkinter.CTkOptionMenu(
            option_frame, values=list(self.service_info["diffTemplates"].keys())
        )
        self.diff_template_menu.grid(row=1, column=1, sticky="w", pady=5)
        self.diff_template_menu.set("Inline")
        self._add_checkbox(body, "diffHideTedious", "隱藏不重要的差異")
        self.tedious_keywords_textbox = customtkinter.CTkTextbox(body, height=80)
        self.tedious_keywords_textbox.pack(fill="x", pady=5)

        # --- 關鍵修改：在這裡設定預設勾選狀態 ---
        self.preferences_vars["diffEnable"].set("on")
        self.preferences_vars["diffSmartForLocalization"].set("on")
        self.preferences_vars["diffHideTedious"].set("on")

    def _add_checkbox(self, parent, key, text):
        var = customtkinter.StringVar(value="off")
        cb = customtkinter.CTkCheckBox(
            parent, text=text, variable=var, onvalue="on", offvalue="off"
        )
        cb.pack(anchor="w", padx=0, pady=5)
        self.preferences_vars[key] = var
