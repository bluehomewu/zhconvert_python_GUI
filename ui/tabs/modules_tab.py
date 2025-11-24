# ui/tabs/modules_tab.py
import customtkinter


class ModulesTab:

    def __init__(self, tab, service_info, save_callback, clear_callback):
        self.tab = tab
        self.service_info = service_info
        self.module_menus = {}

        # --- 頂部框架 ---
        top_frame = customtkinter.CTkFrame(self.tab, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(5, 10))
        top_frame.grid_columnconfigure(0, weight=1)

        clear_button = customtkinter.CTkButton(
            top_frame,
            text="清除設定",
            command=clear_callback,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
        )
        clear_button.pack(side="right", padx=5)
        save_button = customtkinter.CTkButton(
            top_frame, text="儲存設定", command=save_callback
        )
        save_button.pack(side="right", padx=5)

        # --- 內容框架 ---
        scrollable_frame = customtkinter.CTkScrollableFrame(self.tab)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- 欄位權重 ---
        scrollable_frame.grid_columnconfigure(0, weight=2)  # 名稱
        scrollable_frame.grid_columnconfigure(1, weight=1)  # 狀態
        scrollable_frame.grid_columnconfigure(2, weight=1)  # 分類
        scrollable_frame.grid_columnconfigure(3, weight=4)  # 描述
        scrollable_frame.grid_columnconfigure(4, weight=2)  # API 名稱

        # --- 表頭 ---
        headers = ["名稱", "狀態", "分類", "描述", "API 名稱"]
        for i, header_text in enumerate(headers):
            header_label = customtkinter.CTkLabel(
                scrollable_frame,
                text=header_text,
                font=customtkinter.CTkFont(weight="bold"),
            )
            header_label.grid(row=0, column=i, padx=10, pady=10, sticky="w")

        # --- 關鍵修改：簡化表格內容的建立邏輯 ---
        module_cats = self.service_info.get("moduleCategories", {})

        for row_idx, (api_name, module_data) in enumerate(
            self.service_info.get("modules", {}).items(), start=1
        ):

            # --- 不再為每個儲存格建立 Frame ---
            # 將 Label 和 Menu 直接 grid 到 scrollable_frame 中

            # 名稱
            name_label = customtkinter.CTkLabel(
                scrollable_frame, text=module_data.get("name", "")
            )
            name_label.grid(row=row_idx, column=0, padx=10, pady=8, sticky="w")

            # 狀態
            menu = customtkinter.CTkOptionMenu(
                scrollable_frame, width=100, values=["自動", "啟用", "停用"]
            )
            menu.grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
            self.module_menus[api_name] = menu
            if module_data.get("isManual", False):
                menu.set("停用")
            else:
                menu.set("自動")

            # 分類
            cat_id = module_data.get("cat", "misc")
            cat_name = module_cats.get(cat_id, "其他")
            cat_label = customtkinter.CTkLabel(scrollable_frame, text=cat_name)
            cat_label.grid(row=row_idx, column=2, padx=10, pady=8, sticky="w")

            # 描述 (為了能同時顯示描述和手動標註，這裡仍然使用一個輕量級 Frame)
            desc_container = customtkinter.CTkFrame(
                scrollable_frame, fg_color="transparent"
            )
            desc_container.grid(row=row_idx, column=3, padx=10, pady=5, sticky="w")

            desc_label = customtkinter.CTkLabel(
                desc_container,
                text=module_data.get("desc", ""),
                wraplength=300,
                justify="left",
            )
            desc_label.pack(anchor="w")

            if module_data.get("isManual", False):
                manual_label = customtkinter.CTkLabel(
                    desc_container, text="(必須手動啟用)", text_color="#E57373"
                )
                manual_label.pack(anchor="w")

            # API 名稱
            api_label = customtkinter.CTkLabel(
                scrollable_frame,
                text=api_name,
                font=customtkinter.CTkFont(family="monospace"),
            )
            api_label.grid(row=row_idx, column=4, padx=10, pady=8, sticky="w")
