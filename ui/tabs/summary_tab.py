# ui/tabs/summary_tab.py
import customtkinter
from html.parser import HTMLParser


# --- 新版：基於 Tab Stops 的高效能 HTML 解析器 ---
class DiffHTMLParser(HTMLParser):

    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox
        self.line_data = {}
        self.in_td = False
        self.current_td_class = ""
        self.current_data = ""

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'tr':
            self.line_data = {
                'old_n': '',
                'new_n': '',
                'sign': '',
                'content': '',
                'type': attributes.get('data-type', ' ')
            }
        elif tag == 'th' or tag == 'td':
            self.in_td = True
            self.current_td_class = attributes.get('class', '')

    def handle_endtag(self, tag):
        if tag == 'th' or tag == 'td':
            self.in_td = False
            if 'n-old' in self.current_td_class:
                self.line_data['old_n'] = self.current_data
            elif 'n-new' in self.current_td_class:
                self.line_data['new_n'] = self.current_data
            elif 'sign' in self.current_td_class:
                self.line_data['sign'] = self.current_data
            elif 'old' in self.current_td_class or 'new' in self.current_td_class:
                self.line_data['content'] = self.current_data.strip()
            self.current_data = ""

        elif tag == 'tr':
            self._render_line_to_textbox()

    def handle_data(self, data):
        if self.in_td:
            self.current_data += data

    def _render_line_to_textbox(self):
        """將收集到的 line_data 格式化為帶有 Tab 的字串，並插入 Textbox"""
        tags = []
        if self.line_data['type'] == '+':
            tags.append("add")
        elif self.line_data['type'] == '-':
            tags.append("remove")

        # 使用制表符 \t 分隔每個欄位
        formatted_line = (f"{self.line_data['old_n']}\t"
                          f"{self.line_data['new_n']}\t"
                          f"{self.line_data['sign']}\t"
                          f"{self.line_data['content']}\n")
        self.textbox.insert("end", formatted_line, tags)


class SummaryTab:

    def __init__(self, tab, service_info):
        self.tab = tab
        self.service_info = service_info

        self.tab.grid_columnconfigure(0, weight=1)
        self.tab.grid_columnconfigure(1, weight=4)
        self.tab.grid_rowconfigure(0, weight=1)

        params_card = customtkinter.CTkFrame(self.tab, border_width=1)
        params_card.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        params_card.grid_columnconfigure(0, weight=1)
        params_card.grid_rowconfigure(1, weight=1)
        self._create_header(params_card, "轉換參數")
        self.params_scroll_frame = customtkinter.CTkScrollableFrame(
            params_card, fg_color="transparent", corner_radius=0)
        self.params_scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.params_scroll_frame.grid_columnconfigure(0, weight=1)

        diff_card = customtkinter.CTkFrame(self.tab, border_width=1)
        diff_card.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        diff_card.grid_columnconfigure(0, weight=1)
        diff_card.grid_rowconfigure(1, weight=1)
        self._create_header(diff_card, "差異比較")

        # --- 關鍵修改 START ---
        # 1. 重新使用 CTkTextbox
        self.diff_textbox = customtkinter.CTkTextbox(diff_card,
                                                     font=("monospace", 12),
                                                     wrap="none",
                                                     corner_radius=0,
                                                     border_width=0)
        self.diff_textbox.grid(row=1, column=0, sticky="nsew")

        # 2. 設定 Tab Stops 來建立虛擬欄位
        # 格式為 (位置, 對齊方式, 位置, 對齊方式, ...)
        # 'right' 表示文字在定位點右對齊, 'center' 表示居中
        tabs = (40, 'right', 80, 'right', 100, 'center')
        self.diff_textbox.configure(tabs=tabs)

        # 3. 設定顏色標籤 (與之前相同)
        current_mode = customtkinter.get_appearance_mode()
        add_bg_color = "#dffbe2" if current_mode == "Light" else "#224029"
        remove_bg_color = "#fedfe2" if current_mode == "Light" else "#5c2424"
        self.diff_textbox.tag_config("add", background=add_bg_color)
        self.diff_textbox.tag_config("remove", background=remove_bg_color)
        # --- 關鍵修改 END ---

        self.update_content(None)

    def _create_header(self, parent, title):
        header = customtkinter.CTkFrame(parent,
                                        fg_color=("#a5c5e9", "#3a7ebf"),
                                        corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        title_label = customtkinter.CTkLabel(header,
                                             text=title,
                                             font=customtkinter.CTkFont(
                                                 size=14, weight="bold"))
        title_label.pack(side="left", padx=10, pady=8)

    def update_content(self, summary_data):
        for widget in self.params_scroll_frame.winfo_children():
            widget.destroy()
        self.diff_textbox.configure(state="normal")
        self.diff_textbox.delete("1.0", "end")

        if summary_data is None:
            customtkinter.CTkLabel(self.params_scroll_frame,
                                   text="請先執行一次轉換以查看總結。").pack(pady=20)
            self.diff_textbox.insert("end", "尚未執行差異比較。")
            self.diff_textbox.configure(state="disabled")
            return

        # 填充左側參數...
        converter_api_name = summary_data.get('converter')
        converter_display_name = self.service_info.get('converters', {}).get(
            converter_api_name, {}).get('name', converter_api_name)
        self._add_param("轉換模式", converter_display_name)
        text_format_api = summary_data.get('textFormat')
        text_format_display = self.service_info.get('textFormats', {}).get(
            text_format_api, text_format_api)
        self._add_param("文字格式", text_format_display)
        self._add_param("執行耗時", f"{summary_data.get('execTime', 0):.3f} 秒")
        self._add_section_header("使用模組")
        used_modules = summary_data.get('usedModules', [])
        if used_modules:
            modules_frame = customtkinter.CTkFrame(self.params_scroll_frame,
                                                   fg_color="transparent")
            modules_frame.pack(fill="x", padx=10, pady=5)
            modules_frame.grid_columnconfigure((0, 1, 2), weight=1)
            for i, api_name in enumerate(used_modules):
                module_info = self.service_info.get('modules',
                                                    {}).get(api_name, {})
                display_name = module_info.get('name', api_name)
                label = customtkinter.CTkLabel(modules_frame,
                                               text=display_name,
                                               fg_color=("#3B8ED0", "#1F6AA5"),
                                               corner_radius=6)
                label.grid(row=i // 3,
                           column=i % 3,
                           padx=2,
                           pady=2,
                           sticky="ew")
        else:
            self._add_param("", "未使用任何模組")

        # --- 使用新版 HTML 解析器來處理 Diff ---
        diff_content = summary_data.get('diff')
        if diff_content:
            parser = DiffHTMLParser(self.diff_textbox)
            parser.feed(diff_content)
        else:
            self.diff_textbox.insert("end", "轉換前後文字沒有任何改變，或未啟用差異比較。")

        self.diff_textbox.configure(state="disabled")

    def _add_param(self, label_text, value_text):
        if value_text is None: return
        container = customtkinter.CTkFrame(self.params_scroll_frame,
                                           fg_color=("#f0f0f0", "#2b2d30"))
        container.pack(fill="x", padx=10, pady=2, ipady=5)
        label = customtkinter.CTkLabel(container,
                                       text=label_text,
                                       font=customtkinter.CTkFont(
                                           weight="bold", size=12),
                                       text_color=("gray20", "gray80"))
        label.pack(padx=8, anchor="w")
        value = customtkinter.CTkLabel(container,
                                       text=str(value_text),
                                       font=customtkinter.CTkFont(size=14))
        value.pack(padx=8, anchor="w")

    def _add_section_header(self, text):
        customtkinter.CTkLabel(self.params_scroll_frame,
                               text=text,
                               font=customtkinter.CTkFont(weight="bold")).pack(
                                   fill="x", padx=10, pady=(15, 2))
