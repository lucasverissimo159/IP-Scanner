"""
View Principal: Interface gráfica do IP Scanner
- Tela cheia ao iniciar
- Auto-scan a cada 10 segundos
- Tabela estática com ttk.Treeview (dois painéis, scroll suave)
- Exportação de PDF funcional
"""

import customtkinter as ctk
import platform
from typing import List, Set, Dict
from datetime import datetime
from app.models import IPInfo, IPStatus
from app.controllers import ScanController
from app.views.components import (
    ModernCard, ModernButton, ModernEntry, ModernSwitch,
    StatCard, ModernTable
)
from config import get_colors, load_settings


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.settings = load_settings()
        self.theme = self.settings.get("interface", {}).get("theme", "light")
        self.colors = get_colors(self.theme)

        self.controller = ScanController()
        self.controller.on_progress = self.on_scan_progress
        self.controller.on_complete = self.on_scan_complete
        self.controller.on_error = self.on_scan_error

        self.current_filter = "all"
        self.search_term = ""
        self._cached_results: Dict[str, IPInfo] = {}
        self._is_first_scan = True

        self.setup_window()
        self.create_ui()
        self.setup_bindings()

        self.start_blink_timer()
        self.start_auto_refresh_timer()

        self.after(500, self.start_scan)

    def setup_window(self):
        self.title("IP Scanner Pro")
        ctk.set_appearance_mode(self.theme)
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=self.colors["bg_primary"])

        # Ícone na barra de título e na barra de tarefas
        try:
            import sys, os
            if getattr(sys, 'frozen', False):
                # Executável PyInstaller: recursos extraídos em _MEIPASS
                icon_path = os.path.join(sys._MEIPASS, "resources", "icon", "icon.ico")
            else:
                # Modo desenvolvimento: relativo à raiz do projeto
                icon_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "resources", "icon", "icon.ico"
                )
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

        self.after(100, self._set_fullscreen)

    def _set_fullscreen(self):
        try:
            if platform.system() == "Windows":
                self.state('zoomed')
            else:
                self.attributes('-zoomed', True)
        except Exception:
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

    def create_ui(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=16, pady=16)

        self.create_header()
        self.create_config_section()
        self.create_stats_section()
        self.create_filter_bar()
        self.create_table()
        self.create_footer()

    # ==================== UI Sections ====================

    def create_header(self):
        header = ctk.CTkFrame(self.main_container, fg_color="transparent", height=55)
        header.pack(fill="x", pady=(0, 10))
        header.pack_propagate(False)

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="y")
        ctk.CTkLabel(title_frame, text="🌐", font=ctk.CTkFont(size=32)).pack(side="left")

        text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_frame.pack(side="left", padx=(8, 0))
        ctk.CTkLabel(text_frame, text="IP Scanner Pro",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color=self.colors["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(text_frame, text="Monitoramento em tempo real • Auto-refresh: 10s",
                     font=ctk.CTkFont(family="Segoe UI", size=10),
                     text_color=self.colors["text_secondary"]).pack(anchor="w")

        buttons_frame = ctk.CTkFrame(header, fg_color="transparent")
        buttons_frame.pack(side="right", fill="y")

        self.theme_btn = ModernButton(
            buttons_frame, text="Claro" if self.theme == "dark" else "Escuro",
            icon="☀️" if self.theme == "dark" else "🌙",
            variant="ghost", theme=self.theme, width=100,
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="left", padx=(0, 6))

        self.settings_btn = ModernButton(
            buttons_frame, text="Conexões", icon="🔐",
            variant="ghost", theme=self.theme, width=110,
            command=self.open_settings
        )
        self.settings_btn.pack(side="left")

    def create_config_section(self):
        config_frame = ModernCard(self.main_container, title="📡 Configuração", theme=self.theme)
        config_frame.pack(fill="x", pady=(0, 10))

        inner = ctk.CTkFrame(config_frame, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=(0, 14))

        inputs_row = ctk.CTkFrame(inner, fg_color="transparent")
        inputs_row.pack(fill="x")

        # Faixa IP
        ip_frame = ctk.CTkFrame(inputs_row, fg_color="transparent")
        ip_frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(ip_frame, text="Faixa de IP",
                     font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0, 3))

        scan_config = self.settings.get("scan", {})
        ip_base  = scan_config.get("ip_base", "203.0.113")
        start_ip = scan_config.get("start_ip", 1)
        end_ip   = scan_config.get("end_ip", 254)

        self.ip_range_entry = ModernEntry(ip_frame, placeholder="203.0.113.1-254",
                                          theme=self.theme, width=200)
        self.ip_range_entry.pack(anchor="w")
        self.ip_range_entry.insert(0, f"{ip_base}.{start_ip}-{end_ip}")

        # Excluir
        exclude_frame = ctk.CTkFrame(inputs_row, fg_color="transparent")
        exclude_frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(exclude_frame, text="Excluir",
                     font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0, 3))

        exclude_ranges = scan_config.get("exclude_ranges", [])
        exclude_str = ", ".join([f"{s}-{e}" for s, e in exclude_ranges])

        self.exclude_entry = ModernEntry(exclude_frame, placeholder="100-199",
                                         theme=self.theme, width=150)
        self.exclude_entry.pack(anchor="w")
        if exclude_str:
            self.exclude_entry.insert(0, exclude_str)

        # Auto-refresh
        auto_frame = ctk.CTkFrame(inputs_row, fg_color="transparent")
        auto_frame.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(auto_frame, text="Auto",
                     font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0, 3))

        self.auto_refresh_switch = ModernSwitch(auto_frame, text="10s", theme=self.theme,
                                                 command=self.toggle_auto_refresh)
        self.auto_refresh_switch.pack(anchor="w")
        if self.settings.get("interface", {}).get("auto_refresh", True):
            self.auto_refresh_switch.select()

        # Botões de ação
        buttons_frame = ctk.CTkFrame(inputs_row, fg_color="transparent")
        buttons_frame.pack(side="right")

        self.scan_btn = ModernButton(
            buttons_frame, text="Iniciar Varredura", icon="🔍",
            variant="primary", theme=self.theme, width=150, command=self.start_scan
        )
        self.scan_btn.pack(side="left", pady=(15, 0))

        self.cancel_btn = ModernButton(
            buttons_frame, text="Parar", icon="⏹",
            variant="danger", theme=self.theme, width=80, command=self.cancel_scan
        )
        self.cancel_btn.pack(side="left", padx=(8, 0), pady=(15, 0))
        self.cancel_btn.configure(state="disabled")

    def create_stats_section(self):
        stats_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 10))
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.stat_total = StatCard(stats_frame, title="Total", value="0", icon="📊",
                                    color=self.colors["accent"], theme=self.theme)
        self.stat_total.grid(row=0, column=0, sticky="ew", padx=(0, 5), ipady=0)

        self.stat_occupied = StatCard(stats_frame, title="Ocupados", value="0", icon="🟢",
                                       color="#16a34a", theme=self.theme)
        self.stat_occupied.grid(row=0, column=1, sticky="ew", padx=5, ipady=0)

        self.stat_free = StatCard(stats_frame, title="Livres", value="0", icon="🔵",
                                   color="#1d4ed8", theme=self.theme)
        self.stat_free.grid(row=0, column=2, sticky="ew", padx=5, ipady=0)

        self.stat_percent = StatCard(stats_frame, title="Utilização", value="0%", icon="📈",
                                      color=self.colors["warning"], theme=self.theme)
        self.stat_percent.grid(row=0, column=3, sticky="ew", padx=(5, 0), ipady=0)

    def create_filter_bar(self):
        filter_frame = ctk.CTkFrame(
            self.main_container, fg_color=self.colors["bg_card"],
            corner_radius=6, border_width=1, border_color=self.colors["border"], height=48
        )
        filter_frame.pack(fill="x", pady=(0, 6))
        filter_frame.pack_propagate(False)

        inner = ctk.CTkFrame(filter_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=4)

        ctk.CTkLabel(inner, text="Status:",
                     font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                     text_color=self.colors["text_secondary"]).pack(side="left")

        self.filter_buttons = {}
        for filter_id, label in [("all", "Todos"), ("occupied", "Ocupados"), ("free", "Livres")]:
            btn = ModernButton(
                inner, text=label,
                variant="primary" if filter_id == "all" else "ghost",
                theme=self.theme, width=75, height=26,
                command=lambda f=filter_id: self.apply_filter(f)
            )
            btn.pack(side="left", padx=(6, 0))
            self.filter_buttons[filter_id] = btn

        ctk.CTkFrame(inner, fg_color=self.colors["border"], width=1).pack(
            side="left", fill="y", padx=12, pady=2)

        ctk.CTkLabel(inner, text="Buscar:",
                     font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                     text_color=self.colors["text_secondary"]).pack(side="left")

        self.search_entry = ModernEntry(inner, placeholder="IP, Nome, Sistema...",
                                         theme=self.theme, width=180, height=26)
        self.search_entry.pack(side="left", padx=(6, 0))
        self.search_entry.bind("<Return>", lambda e: self.do_filter())

        ModernButton(inner, text="Filtrar", variant="secondary", theme=self.theme,
                     width=65, height=26, command=self.do_filter).pack(side="left", padx=(6, 0))

        ModernButton(inner, text="Limpar", variant="ghost", theme=self.theme,
                     width=55, height=26, command=self.clear_filter).pack(side="left", padx=(4, 0))

        ctk.CTkFrame(inner, fg_color=self.colors["border"], width=1).pack(
            side="left", fill="y", padx=12, pady=2)

        self.pdf_btn = ctk.CTkButton(
            inner, text="📄 Exportar PDF",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#1e40af", hover_color="#1e3a8a", text_color="#ffffff",
            corner_radius=6, width=130, height=26,
            command=self.open_export_dialog
        )
        self.pdf_btn.pack(side="left")
        self.pdf_btn.configure(state="disabled")

        self.csv_btn = ctk.CTkButton(
            inner, text="📊 Exportar CSV",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#065f46", hover_color="#064e3b", text_color="#ffffff",
            corner_radius=6, width=130, height=26,
            command=self.open_csv_export_dialog
        )
        self.csv_btn.pack(side="left", padx=(8, 0))
        self.csv_btn.configure(state="disabled")

        # ── Visor de contagem (lado direito) ──────────────────────────────
        counter_frame = ctk.CTkFrame(
            inner, fg_color=self.colors["bg_tertiary"],
            corner_radius=6, border_width=1, border_color=self.colors["border"]
        )
        counter_frame.pack(side="right", padx=(0, 4), pady=2)

        ctk.CTkLabel(
            counter_frame, text="Exibindo",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=self.colors["text_muted"]
        ).pack(side="left", padx=(10, 4))

        self.counter_value = ctk.CTkLabel(
            counter_frame, text="—",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.colors["accent"]
        )
        self.counter_value.pack(side="left")

        self.counter_suffix = ctk.CTkLabel(
            counter_frame, text="",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=self.colors["text_muted"]
        )
        self.counter_suffix.pack(side="left", padx=(4, 10))

    def create_table(self):
        columns = [
            ("STATUS", 80), ("IP ADDRESS", 120), ("LATENCY", 90), ("LOSS", 55),
            ("NAME", 150), ("MANUFACTURER", 110), ("MODEL", 130),
            ("SYSTEM", 130), ("RAM", 70), ("SOURCE", 70), ("LAST INVENTORY", 130)
        ]
        self.table = ModernTable(
            self.main_container, columns=columns,
            theme=self.theme, on_row_click=self.on_row_click
        )
        self.table.pack(fill="both", expand=True)

    def create_footer(self):
        footer = ctk.CTkFrame(self.main_container, fg_color=self.colors["bg_card"],
                               corner_radius=6, height=30)
        footer.pack(fill="x", pady=(6, 0))
        footer.pack_propagate(False)

        inner = ctk.CTkFrame(footer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12)

        self.status_label = ctk.CTkLabel(inner, text="Iniciando...",
                                          font=ctk.CTkFont(family="Segoe UI", size=10),
                                          text_color=self.colors["text_secondary"])
        self.status_label.pack(side="left", pady=4)

        self.time_label = ctk.CTkLabel(inner, text="",
                                        font=ctk.CTkFont(family="Segoe UI", size=10),
                                        text_color=self.colors["text_muted"])
        self.time_label.pack(side="right", pady=4)

    def setup_bindings(self):
        self.bind("<F5>",      lambda e: self.start_scan())
        self.bind("<Escape>",  lambda e: self.cancel_scan())
        self.bind("<Control-f>", lambda e: self.search_entry.focus())

    # ==================== Scan ====================

    def start_scan(self):
        if self.controller.is_scanning:
            return

        try:
            ip_range = self.ip_range_entry.get().strip()
            if ip_range:
                parsed = self.controller.parse_ip_range(ip_range)

                exclude_str = self.exclude_entry.get().strip()
                exclude_ranges = []
                if exclude_str:
                    for part in exclude_str.split(","):
                        part = part.strip()
                        if "-" in part:
                            s, e = part.split("-")
                            exclude_ranges.append([int(s.strip()), int(e.strip())])

                parsed["exclude_ranges"] = exclude_ranges
                self.controller.update_settings("scan", parsed)

        except ValueError as e:
            self.show_error(str(e))
            return

        self.scan_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        # Mantém PDF/CSV habilitado se já há resultados anteriores
        if not self._cached_results:
            self.pdf_btn.configure(state="disabled")
            self.csv_btn.configure(state="disabled")
        self.status_label.configure(text="🔄 Escaneando...")

        self.controller.start_scan()

    def cancel_scan(self):
        self.controller.cancel_scan()
        self.table.set_building(False)
        self.scan_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.status_label.configure(text="⏹ Parado")

    def on_scan_progress(self, current: int, total: int, message: str):
        self.after(0, lambda: self.status_label.configure(
            text=f"🔄 {current}/{total} — {message}"))

    def on_scan_complete(self, results: List[IPInfo], free_ips: Set[str], occupied_ips: Set[str]):
        self.after(0, lambda: self._update_results(results))

    def _update_results(self, results: List[IPInfo]):
        new_cache = {ip_info.ip_address: ip_info for ip_info in results}

        if self._is_first_scan or set(new_cache.keys()) != set(self._cached_results.keys()):
            self._cached_results = new_cache
            self._rebuild_table()
            self._is_first_scan = False
        else:
            self._cached_results = new_cache
            self._update_table_inplace()

        total    = len(results)
        occupied = sum(1 for r in results if r.status == IPStatus.OCCUPIED)
        free     = total - occupied

        self.stat_total.set_value(str(total))
        self.stat_occupied.set_value(str(occupied))
        self.stat_free.set_value(str(free))
        self.stat_percent.set_value(f"{(occupied / total * 100):.1f}%" if total > 0 else "0%")

        self.scan_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.pdf_btn.configure(state="normal")
        self.csv_btn.configure(state="normal")
        self.status_label.configure(
            text=f"✅ {total} IPs • {occupied} ocupados • {free} livres")
        self.time_label.configure(text=datetime.now().strftime('%H:%M:%S'))

    # ── Tabela ────────────────────────────────────────────────────────────

    def _update_counter(self, shown: int):
        """Atualiza o visor de contagem na barra de filtros."""
        total = len(self._cached_results)
        self.counter_value.configure(text=str(shown))
        if shown == total or total == 0:
            self.counter_suffix.configure(text=f"de {total} IPs")
            self.counter_value.configure(text_color=self.colors["accent"])
        else:
            self.counter_suffix.configure(text=f"de {total} IPs")
            # Destaca em laranja quando é uma visão parcial (filtrada)
            self.counter_value.configure(text_color=self.colors["warning"])

    def _rebuild_table(self):
        self.table.set_building(True)
        self.table.clear()
        filtered = self._get_filtered_results()
        for ip_info in filtered:
            self._add_row_from_info(ip_info)
        self.table.set_building(False)
        self._update_counter(len(filtered))

    def _update_table_inplace(self):
        if self.current_filter != "all" or self.search_term:
            self._rebuild_table()
            return
        for ip, ip_info in self._cached_results.items():
            if not self.table.update_row(ip, self._get_row_data(ip_info), ip_info.status.value):
                self._add_row_from_info(ip_info)
        self._update_counter(len(self._cached_results))

    def _get_filtered_results(self) -> List[IPInfo]:
        results = list(self._cached_results.values())

        if self.current_filter == "free":
            results = [r for r in results if r.status == IPStatus.FREE]
        elif self.current_filter == "occupied":
            results = [r for r in results if r.status == IPStatus.OCCUPIED]

        if self.search_term:
            term = self.search_term.lower()
            results = [r for r in results
                       if (term in r.ip_address.lower()                          or
                           term in r.name.lower()                                or
                           term in r.manufacturer.lower()                        or
                           term in r.model.lower()                               or
                           term in r.system.lower()                              or
                           term in r.ram.lower()                                 or
                           term in r.source.lower()                              or
                           term in r.mac.lower()                                 or
                           term in getattr(r, 'last_inventory', '').lower()      or
                           term in getattr(r, 'first_seen', '').lower()          or
                           term in getattr(r, 'last_seen', '').lower()           or
                           term in r.latency.lower()                             or
                           term in r.packet_loss.lower()                         or
                           term in (r.status.value).lower())]

        results.sort(key=lambda x: [int(p) for p in x.ip_address.split('.')])
        return results

    def _get_row_data(self, ip_info: IPInfo) -> List[str]:
        status = ip_info.status.value
        return [
            "LIVRE" if status == "free" else "OCUPADO",
            ip_info.ip_address, ip_info.latency, ip_info.packet_loss,
            ip_info.name, ip_info.manufacturer, ip_info.model,
            ip_info.system, ip_info.ram, ip_info.source,
            getattr(ip_info, 'last_inventory', 'N/A'),
        ]

    def _add_row_from_info(self, ip_info: IPInfo):
        self.table.add_row(self._get_row_data(ip_info), ip_info.status.value, ip_info.ip_address)

    # ==================== Filtros ====================

    def apply_filter(self, filter_id: str):
        self.current_filter = filter_id
        for fid, btn in self.filter_buttons.items():
            if fid == filter_id:
                btn.configure(fg_color=self.colors["accent"],
                               hover_color=self.colors["accent_hover"], text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent",
                               hover_color=self.colors["bg_tertiary"],
                               text_color=self.colors["text_primary"])
        if self._cached_results:
            self._rebuild_table()

    def do_filter(self):
        self.search_term = self.search_entry.get().strip()
        if self._cached_results:
            self._rebuild_table()

    def clear_filter(self):
        self.search_entry.delete(0, "end")
        self.search_term = ""
        if self._cached_results:
            self._rebuild_table()

    # ==================== PDF Export ====================

    def open_export_dialog(self):
        filtered = self._get_filtered_results()
        parts = []
        if self.current_filter != "all":
            parts.append("Ocupados" if self.current_filter == "occupied" else "Livres")
        if self.search_term:
            parts.append(f'"{self.search_term}"')
        filter_label = " + ".join(parts) if parts else None
        ExportPDFDialog(self, self._cached_results, self.colors,
                        filtered_results=filtered, filter_label=filter_label)

    def open_csv_export_dialog(self):
        filtered = self._get_filtered_results()
        parts = []
        if self.current_filter != "all":
            parts.append("Ocupados" if self.current_filter == "occupied" else "Livres")
        if self.search_term:
            parts.append(f'"{self.search_term}"')
        filter_label = " + ".join(parts) if parts else None
        ExportCSVDialog(self, self._cached_results, self.colors,
                        filtered_results=filtered, filter_label=filter_label)

    # ==================== Callbacks ====================

    def on_scan_error(self, error: str):
        self.after(0, lambda: self.show_error(error))

    def show_error(self, message: str):
        self.table.set_building(False)
        self.scan_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.status_label.configure(text=f"❌ {message}")

    def on_row_click(self, data: List[str], status: str):
        pass

    def toggle_auto_refresh(self):
        auto = self.auto_refresh_switch.get() == 1
        self.controller.update_settings("interface", {"auto_refresh": auto})
        self.status_label.configure(text="✅ Auto ON" if auto else "⏸ Auto OFF")

    def open_settings(self):
        SettingsWindow(self, self.controller, self.theme)

    def toggle_theme(self):
        """Alterna entre tema claro e escuro, recria a UI com as novas cores."""
        self.theme = "dark" if self.theme == "light" else "light"
        self.colors = get_colors(self.theme)

        # Persiste a preferência
        self.controller.update_settings("interface", {"theme": self.theme})

        # Aplica o modo no customtkinter
        ctk.set_appearance_mode(self.theme)
        self.configure(fg_color=self.colors["bg_primary"])

        # Preserva dados em cache antes de recriar a UI
        cached = dict(self._cached_results)
        is_first = self._is_first_scan

        # Destrói e recria toda a interface com as novas cores
        self.main_container.destroy()
        self.create_ui()
        self.setup_bindings()

        # Restaura os dados na nova tabela
        self._cached_results = cached
        self._is_first_scan = is_first
        if cached:
            self._rebuild_table()

    def start_blink_timer(self):
        def blink():
            if self._cached_results:
                self.table.toggle_blink()
            self.after(800, blink)
        self.after(800, blink)

    def start_auto_refresh_timer(self):
        def auto_refresh():
            if self.auto_refresh_switch.get() == 1 and not self.controller.is_scanning:
                self.start_scan()
            self.after(10000, auto_refresh)
        self.after(10000, auto_refresh)


# ============================================================
# Janela de exportação PDF
# ============================================================

class ExportPDFDialog(ctk.CTkToplevel):
    def __init__(self, parent, cached_results: Dict[str, IPInfo], colors: dict,
                 filtered_results: List[IPInfo] = None, filter_label: str = None):
        super().__init__(parent)
        self._cached          = cached_results
        self._filtered        = filtered_results or []
        self._filter_label    = filter_label      # None = sem filtro ativo
        self.colors           = colors

        self.title("📄 Exportar PDF")
        self.geometry("420x340")
        self.configure(fg_color=colors["bg_primary"])
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - 210
        y = (self.winfo_screenheight() // 2) - 170
        self.geometry(f"420x340+{x}+{y}")

        # Garantir que a janela apareça na frente da janela principal (fullscreen)
        self.lift()
        self.attributes('-topmost', True)
        self.after(50, lambda: self.attributes('-topmost', False))
        self.focus_force()

        self._build_ui()

    def _build_ui(self):
        pad = ctk.CTkFrame(self, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(pad, text="📄 Exportar relatório de IPs",
                     font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                     text_color=self.colors["text_primary"]).pack(anchor="w", pady=(0, 16))

        ctk.CTkLabel(pad, text="Selecione o que exportar:",
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0, 8))

        self._export_var = ctk.StringVar(value="filtered" if self._filter_label else "all")
        for value, label in [
            ("all",      "📊  Todos os IPs"),
            ("free",     "🔵  Somente IPs Livres"),
            ("occupied", "🟢  Somente IPs Ocupados"),
        ]:
            ctk.CTkRadioButton(
                pad, text=label, variable=self._export_var, value=value,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=self.colors["text_primary"],
                fg_color=self.colors["accent"],
                hover_color=self.colors["accent_hover"],
            ).pack(anchor="w", padx=8, pady=4)

        # Opção "Filtro atual" — sempre visível; desabilitada quando não há filtro ativo
        filtered_count = len(self._filtered)
        if self._filter_label:
            filter_desc = f"🔍  Filtro atual: {self._filter_label}  ({filtered_count} registro{'s' if filtered_count != 1 else ''})"
            filter_fg   = self.colors["text_primary"]
        else:
            filter_desc = "🔍  Filtro atual  (nenhum filtro aplicado)"
            filter_fg   = self.colors["text_muted"]

        filter_radio = ctk.CTkRadioButton(
            pad, text=filter_desc, variable=self._export_var, value="filtered",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=filter_fg,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            state="normal" if self._filter_label else "disabled",
        )
        filter_radio.pack(anchor="w", padx=8, pady=4)

        btn_row = ctk.CTkFrame(pad, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom", pady=(16, 0))

        ctk.CTkButton(btn_row, text="💾 Salvar PDF", width=140, height=38,
                      fg_color="#16a34a", hover_color="#14532d", text_color="#ffffff",
                      corner_radius=8, font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._do_export).pack(side="right")

        ctk.CTkButton(btn_row, text="Cancelar", width=100, height=38,
                      fg_color=self.colors["bg_tertiary"], hover_color=self.colors["border"],
                      text_color=self.colors["text_primary"], corner_radius=8,
                      font=ctk.CTkFont(size=12), command=self.destroy).pack(side="right", padx=(0, 10))

    def _do_export(self):
        from tkinter import filedialog, messagebox

        choice = self._export_var.get()
        default_names = {
            "all":      "ips_todos.pdf",
            "free":     "ips_livres.pdf",
            "occupied": "ips_ocupados.pdf",
            "filtered": "ips_filtrados.pdf",
        }

        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=default_names[choice],
            title="Salvar relatório PDF"
        )
        if not path:
            return

        all_ips = sorted(
            self._cached.values(),
            key=lambda x: [int(p) for p in x.ip_address.split('.')]
        )

        if choice == "free":
            data        = [ip for ip in all_ips if ip.status == IPStatus.FREE]
            label_extra = None
        elif choice == "occupied":
            data        = [ip for ip in all_ips if ip.status == IPStatus.OCCUPIED]
            label_extra = None
        elif choice == "filtered":
            data        = sorted(self._filtered,
                                 key=lambda x: [int(p) for p in x.ip_address.split('.')])
            label_extra = self._filter_label
        else:
            data        = all_ips
            label_extra = None

        try:
            _generate_pdf(path, data, choice, label_extra)
            self.destroy()
            if platform.system() == "Windows":
                import subprocess
                subprocess.Popen(["explorer", "/select,", path])
        except Exception as e:
            messagebox.showerror("Erro ao gerar PDF", str(e), parent=self)


# ============================================================
# Gerador de PDF
# ============================================================

def _generate_pdf(path: str, ips: List[IPInfo], filter_type: str, label_extra: str = None):
    """Gera relatório PDF com reportlab."""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors as rc
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle,
        Paragraph, Spacer, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    PAGE = landscape(A4)
    doc = SimpleDocTemplate(path, pagesize=PAGE,
                             leftMargin=1.5*cm, rightMargin=1.5*cm,
                             topMargin=1.5*cm, bottomMargin=1.5*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("T2", parent=styles["Normal"],
                                  fontSize=16, fontName="Helvetica-Bold",
                                  textColor=rc.HexColor("#1a202c"), spaceAfter=4)
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"],
                                fontSize=9, fontName="Helvetica",
                                textColor=rc.HexColor("#4a5568"))

    filter_labels = {
        "all":      "Todos os IPs",
        "free":     "IPs Livres",
        "occupied": "IPs Ocupados",
        "filtered": f"Filtro: {label_extra}" if label_extra else "Filtro Atual",
    }
    label = filter_labels.get(filter_type, "IPs")

    elements = []
    elements.append(Paragraph(f"IP Scanner Pro — {label}", title_style))
    elements.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  •  Total: {len(ips)} registros",
        sub_style))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=rc.HexColor("#cbd5e0")))
    elements.append(Spacer(1, 0.4*cm))

    # ── Tabela ────────────────────────────────────────────────────────────
    headers = ["Status", "IP", "Latência", "Perda", "Nome",
               "Fabricante", "Modelo", "Sistema", "RAM", "Fonte", "Último Inventário"]
    col_w = [1.7*cm, 2.3*cm, 1.7*cm, 1.1*cm, 3.8*cm,
             2.8*cm, 2.8*cm, 3.2*cm, 1.4*cm, 1.6*cm, 2.8*cm]
    # Total ≈ 25.2 cm — cabe em A4 paisagem (26.7 cm úteis c/ margens de 1.5 cm)

    # Cores
    occ_bg   = rc.HexColor("#dcfce7")
    free_bg  = rc.HexColor("#dbeafe")
    occ_alt  = rc.HexColor("#f0fdf4")
    free_alt = rc.HexColor("#eff6ff")
    occ_fg   = rc.HexColor("#14532d")
    free_fg  = rc.HexColor("#1e3a8a")
    ip_occ   = rc.HexColor("#16a34a")   # verde sólido para coluna IP de ocupados
    ip_free  = rc.HexColor("#1d4ed8")   # azul sólido para coluna IP de livres

    table_data = [headers]
    per_row_cmds = []

    for idx, ip in enumerate(ips):
        r = idx + 1  # row index (0 = header)
        is_free = ip.status == IPStatus.FREE

        bg     = (free_bg  if is_free else occ_bg)  if idx % 2 == 0 else (free_alt if is_free else occ_alt)
        fg     = free_fg  if is_free else occ_fg

        per_row_cmds += [
            # Fundo da linha inteira (incluindo STATUS) — cor suave por status
            ("BACKGROUND",  (0, r), (-1, r), bg),
            # Somente coluna IP (col 1) recebe destaque com fundo escuro
            ("BACKGROUND",  (1, r), (1,  r), ip_free if is_free else ip_occ),
            ("TEXTCOLOR",   (1, r), (1,  r), rc.white),
            ("FONTNAME",    (1, r), (1,  r), "Helvetica-Bold"),
            # Texto normal para todas as outras colunas (incluindo STATUS)
            ("TEXTCOLOR",   (0, r), (0,  r), fg),
            ("TEXTCOLOR",   (2, r), (-1, r), fg),
            ("FONTNAME",    (0, r), (0,  r), "Helvetica-Bold"),
        ]

        last_inv = getattr(ip, 'last_inventory', 'N/A')
        status_lbl = "LIVRE" if is_free else "OCUPADO"

        table_data.append([
            status_lbl,
            ip.ip_address,
            ip.latency,
            ip.packet_loss,
            (ip.name[:32]         if ip.name         != "N/A" else "—"),
            (ip.manufacturer[:28] if ip.manufacturer  != "N/A" else "—"),
            (ip.model[:28]        if ip.model         != "N/A" else "—"),
            (ip.system[:28]       if getattr(ip, 'system', 'N/A') != "N/A" else "—"),
            (ip.ram               if getattr(ip, 'ram', 'N/A')    != "N/A" else "—"),
            ip.source,
            (last_inv[:18]        if last_inv         != "N/A" else "—"),
        ])

    base_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0), rc.HexColor("#1e293b")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), rc.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
        ("GRID",          (0, 0), (-1, -1), 0.5, rc.HexColor("#94a3b8")),
        ("BOX",           (0, 0), (-1, -1), 1.0, rc.HexColor("#64748b")),
        ("LINEBELOW",     (0, 0), (-1, 0), 1.5, rc.HexColor("#334155")),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [None]),  # desativa zebra padrão
    ]

    style = TableStyle(base_cmds)
    for cmd in per_row_cmds:
        style.add(*cmd)

    table = Table(table_data, colWidths=col_w, repeatRows=1)
    table.setStyle(style)
    elements.append(table)

    doc.build(elements)


# ============================================================
# Janela de exportação CSV
# ============================================================

class ExportCSVDialog(ctk.CTkToplevel):
    def __init__(self, parent, cached_results: Dict[str, IPInfo], colors: dict,
                 filtered_results: List[IPInfo] = None, filter_label: str = None):
        super().__init__(parent)
        self._cached       = cached_results
        self._filtered     = filtered_results or []
        self._filter_label = filter_label
        self.colors        = colors

        self.title("📊 Exportar CSV")
        self.geometry("420x340")
        self.configure(fg_color=colors["bg_primary"])
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - 210
        y = (self.winfo_screenheight() // 2) - 170
        self.geometry(f"420x340+{x}+{y}")

        self.lift()
        self.attributes('-topmost', True)
        self.after(50, lambda: self.attributes('-topmost', False))
        self.focus_force()

        self._build_ui()

    def _build_ui(self):
        pad = ctk.CTkFrame(self, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(pad, text="📊 Exportar relatório CSV",
                     font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                     text_color=self.colors["text_primary"]).pack(anchor="w", pady=(0, 16))

        ctk.CTkLabel(pad, text="Selecione o que exportar:",
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0, 8))

        self._export_var = ctk.StringVar(value="filtered" if self._filter_label else "all")
        for value, label in [
            ("all",      "📊  Todos os IPs"),
            ("free",     "🔵  Somente IPs Livres"),
            ("occupied", "🟢  Somente IPs Ocupados"),
        ]:
            ctk.CTkRadioButton(
                pad, text=label, variable=self._export_var, value=value,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=self.colors["text_primary"],
                fg_color="#065f46",
                hover_color="#064e3b",
            ).pack(anchor="w", padx=8, pady=4)

        filtered_count = len(self._filtered)
        if self._filter_label:
            filter_desc = f"🔍  Filtro atual: {self._filter_label}  ({filtered_count} registro{'s' if filtered_count != 1 else ''})"
            filter_fg   = self.colors["text_primary"]
        else:
            filter_desc = "🔍  Filtro atual  (nenhum filtro aplicado)"
            filter_fg   = self.colors["text_muted"]

        ctk.CTkRadioButton(
            pad, text=filter_desc, variable=self._export_var, value="filtered",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=filter_fg,
            fg_color="#065f46",
            hover_color="#064e3b",
            state="normal" if self._filter_label else "disabled",
        ).pack(anchor="w", padx=8, pady=4)

        btn_row = ctk.CTkFrame(pad, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom", pady=(16, 0))

        ctk.CTkButton(btn_row, text="💾 Salvar CSV", width=140, height=38,
                      fg_color="#065f46", hover_color="#064e3b", text_color="#ffffff",
                      corner_radius=8, font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._do_export).pack(side="right")

        ctk.CTkButton(btn_row, text="Cancelar", width=100, height=38,
                      fg_color=self.colors["bg_tertiary"], hover_color=self.colors["border"],
                      text_color=self.colors["text_primary"], corner_radius=8,
                      font=ctk.CTkFont(size=12), command=self.destroy).pack(side="right", padx=(0, 10))

    def _do_export(self):
        from tkinter import filedialog, messagebox

        choice = self._export_var.get()
        default_names = {
            "all":      "ips_todos.csv",
            "free":     "ips_livres.csv",
            "occupied": "ips_ocupados.csv",
            "filtered": "ips_filtrados.csv",
        }

        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos os arquivos", "*.*")],
            initialfile=default_names[choice],
            title="Salvar relatório CSV"
        )
        if not path:
            return

        all_ips = sorted(
            self._cached.values(),
            key=lambda x: [int(p) for p in x.ip_address.split('.')]
        )

        if choice == "free":
            data = [ip for ip in all_ips if ip.status == IPStatus.FREE]
        elif choice == "occupied":
            data = [ip for ip in all_ips if ip.status == IPStatus.OCCUPIED]
        elif choice == "filtered":
            data = sorted(self._filtered,
                          key=lambda x: [int(p) for p in x.ip_address.split('.')])
        else:
            data = all_ips

        try:
            _generate_csv(path, data)
            self.destroy()
            if platform.system() == "Windows":
                import subprocess
                subprocess.Popen(["explorer", "/select,", path])
        except Exception as e:
            messagebox.showerror("Erro ao gerar CSV", str(e), parent=self)


# ============================================================
# Gerador de CSV
# ============================================================

def _generate_csv(path: str, ips: List[IPInfo]):
    """
    Gera relatório CSV com os dados dos IPs.
    O campo IP Address usa o prefixo de fórmula ="valor" para forçar o Excel
    a tratar o conteúdo como texto puro, evitando que o locale pt-BR interprete
    o ponto como separador de milhar e desloque as colunas.
    """
    import csv

    headers = [
        "Status", "IP Address", "Latência", "Perda de Pacotes",
        "Nome", "Fabricante", "Modelo", "Sistema", "RAM",
        "Fonte", "Primeiro Acesso", "Último Acesso", "Último Inventário", "MAC"
    ]

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_ALL)
        writer.writerow(headers)
        for ip in ips:
            status_lbl = "LIVRE" if ip.status == IPStatus.FREE else "OCUPADO"
            # ="192.168.x.x" → Excel avalia como fórmula e exibe o texto exato
            ip_cell = f'="{ip.ip_address}"'
            writer.writerow([
                status_lbl,
                ip_cell,
                ip.latency,
                ip.packet_loss,
                ip.name,
                ip.manufacturer,
                ip.model,
                ip.system,
                ip.ram,
                ip.source,
                getattr(ip, 'first_seen',      'N/A'),
                getattr(ip, 'last_seen',        'N/A'),
                getattr(ip, 'last_inventory',   'N/A'),
                ip.mac,
            ])


# ============================================================
# Settings Window
# ============================================================

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, controller: ScanController, theme: str):
        super().__init__(parent)
        self.controller = controller
        self.colors = get_colors()

        self.title("🔐 Conexões")
        self.geometry("500x620")
        self.configure(fg_color=self.colors["bg_primary"])
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - 250
        y = (self.winfo_screenheight() // 2) - 310
        self.geometry(f"500x620+{x}+{y}")
        self.create_ui()

    def create_ui(self):
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="🔐 Configurações de Conexão",
                     font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                     text_color=self.colors["text_primary"]).pack(anchor="w", pady=(0, 15))

        # UniFi
        unifi_card = ModernCard(container, title="🌐 UniFi Controller", theme="light")
        unifi_card.pack(fill="x", pady=(0, 12))
        unifi_inner = ctk.CTkFrame(unifi_card, fg_color="transparent")
        unifi_inner.pack(fill="x", padx=14, pady=(0, 14))
        unifi_config = self.controller.get_setting("unifi")

        ctk.CTkLabel(unifi_inner, text="Host (ex: https://192.0.2.1:8443):",
                     font=ctk.CTkFont(size=11), text_color=self.colors["text_secondary"]).pack(anchor="w")
        self.unifi_host = ctk.CTkEntry(unifi_inner, font=ctk.CTkFont(size=12), height=36, corner_radius=6)
        self.unifi_host.pack(fill="x", pady=(4, 8))
        self.unifi_host.insert(0, unifi_config.get("host", ""))

        row_u = ctk.CTkFrame(unifi_inner, fg_color="transparent")
        row_u.pack(fill="x")
        for attr, label, key in [("unifi_user", "Usuário:", "username"), ("unifi_pass", "Senha:", "password")]:
            col = ctk.CTkFrame(row_u, fg_color="transparent")
            col.pack(side="left", fill="x", expand=True, padx=(0, 6) if attr == "unifi_user" else (6, 0))
            ctk.CTkLabel(col, text=label, font=ctk.CTkFont(size=11),
                         text_color=self.colors["text_secondary"]).pack(anchor="w")
            kw = {"show": "•"} if attr == "unifi_pass" else {}
            entry = ctk.CTkEntry(col, font=ctk.CTkFont(size=12), height=36, corner_radius=6, **kw)
            entry.pack(fill="x", pady=(4, 0))
            entry.insert(0, unifi_config.get(key, ""))
            setattr(self, attr, entry)

        # OCS
        ocs_card = ModernCard(container, title="📋 OCS Inventory", theme="light")
        ocs_card.pack(fill="x", pady=(0, 12))
        ocs_inner = ctk.CTkFrame(ocs_card, fg_color="transparent")
        ocs_inner.pack(fill="x", padx=14, pady=(0, 14))
        ocs_config = self.controller.get_setting("ocs")

        ctk.CTkLabel(ocs_inner, text="URL Base (ex: http://198.51.100.245/ocsreports):",
                     font=ctk.CTkFont(size=11), text_color=self.colors["text_secondary"]).pack(anchor="w")
        self.ocs_url = ctk.CTkEntry(ocs_inner, font=ctk.CTkFont(size=12), height=36, corner_radius=6)
        self.ocs_url.pack(fill="x", pady=(4, 8))
        self.ocs_url.insert(0, ocs_config.get("base_url", ""))

        row_o = ctk.CTkFrame(ocs_inner, fg_color="transparent")
        row_o.pack(fill="x")
        for attr, label, key in [("ocs_user", "Usuário:", "username"), ("ocs_pass", "Senha:", "password")]:
            col = ctk.CTkFrame(row_o, fg_color="transparent")
            col.pack(side="left", fill="x", expand=True, padx=(0, 6) if attr == "ocs_user" else (6, 0))
            ctk.CTkLabel(col, text=label, font=ctk.CTkFont(size=11),
                         text_color=self.colors["text_secondary"]).pack(anchor="w")
            kw = {"show": "•"} if attr == "ocs_pass" else {}
            entry = ctk.CTkEntry(col, font=ctk.CTkFont(size=12), height=36, corner_radius=6, **kw)
            entry.pack(fill="x", pady=(4, 0))
            entry.insert(0, ocs_config.get(key, ""))
            setattr(self, attr, entry)

        # Proxy
        proxy_card = ModernCard(container, title="🌐 Proxy Corporativo", theme="light")
        proxy_card.pack(fill="x", pady=(0, 12))
        proxy_inner = ctk.CTkFrame(proxy_card, fg_color="transparent")
        proxy_inner.pack(fill="x", padx=14, pady=(0, 14))
        proxy_config = self.controller.get_setting("proxy")

        # Switch habilitar proxy
        proxy_top = ctk.CTkFrame(proxy_inner, fg_color="transparent")
        proxy_top.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(proxy_top, text="Usar proxy:",
                     font=ctk.CTkFont(size=11), text_color=self.colors["text_secondary"]).pack(side="left")
        self.proxy_enabled = ModernSwitch(proxy_top, text="", theme="light")
        self.proxy_enabled.pack(side="left", padx=(8, 0))
        if proxy_config.get("enabled", False):
            self.proxy_enabled.select()

        # Bypass local
        ctk.CTkLabel(proxy_top, text="   Ignorar proxy para IPs locais:",
                     font=ctk.CTkFont(size=11), text_color=self.colors["text_secondary"]).pack(side="left")
        self.proxy_bypass = ModernSwitch(proxy_top, text="", theme="light")
        self.proxy_bypass.pack(side="left", padx=(8, 0))
        if proxy_config.get("bypass_local", True):
            self.proxy_bypass.select()

        ctk.CTkLabel(proxy_inner, text="Host (ex: http://proxy.empresa.com:3128):",
                     font=ctk.CTkFont(size=11), text_color=self.colors["text_secondary"]).pack(anchor="w")
        self.proxy_host = ctk.CTkEntry(proxy_inner, font=ctk.CTkFont(size=12), height=36, corner_radius=6)
        self.proxy_host.pack(fill="x", pady=(4, 8))
        self.proxy_host.insert(0, proxy_config.get("host", ""))

        row_p = ctk.CTkFrame(proxy_inner, fg_color="transparent")
        row_p.pack(fill="x")
        for attr, label, key in [("proxy_user", "Usuário:", "username"), ("proxy_pass", "Senha:", "password")]:
            col = ctk.CTkFrame(row_p, fg_color="transparent")
            col.pack(side="left", fill="x", expand=True, padx=(0, 6) if attr == "proxy_user" else (6, 0))
            ctk.CTkLabel(col, text=label, font=ctk.CTkFont(size=11),
                         text_color=self.colors["text_secondary"]).pack(anchor="w")
            kw = {"show": "•"} if attr == "proxy_pass" else {}
            entry = ctk.CTkEntry(col, font=ctk.CTkFont(size=12), height=36, corner_radius=6, **kw)
            entry.pack(fill="x", pady=(4, 0))
            entry.insert(0, proxy_config.get(key, ""))
            setattr(self, attr, entry)

        # Botões
        buttons = ctk.CTkFrame(container, fg_color="transparent", height=60)
        buttons.pack(fill="x", pady=(20, 0))
        buttons.pack_propagate(False)

        ctk.CTkButton(buttons, text="💾 Salvar", width=140, height=44,
                      fg_color="#22c55e", hover_color="#16a34a", text_color="#ffffff",
                      corner_radius=8, font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.save_settings).pack(side="right")
        ctk.CTkButton(buttons, text="Cancelar", width=110, height=44,
                      fg_color=self.colors["bg_tertiary"], hover_color=self.colors["border"],
                      text_color=self.colors["text_primary"], corner_radius=8,
                      font=ctk.CTkFont(size=13), command=self.destroy).pack(side="right", padx=(0, 12))

    def save_settings(self):
        self.controller.update_settings("unifi", {
            "host": self.unifi_host.get(),
            "username": self.unifi_user.get(),
            "password": self.unifi_pass.get()
        })
        self.controller.update_settings("ocs", {
            "base_url": self.ocs_url.get(),
            "username": self.ocs_user.get(),
            "password": self.ocs_pass.get()
        })
        self.controller.update_settings("proxy", {
            "enabled": self.proxy_enabled.get() == 1,
            "host": self.proxy_host.get(),
            "username": self.proxy_user.get(),
            "password": self.proxy_pass.get(),
            "bypass_local": self.proxy_bypass.get() == 1
        })
        self.destroy()