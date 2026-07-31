"""
Componentes de UI customizados
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Callable, Optional, List, Tuple
from config import get_colors


class ModernCard(ctk.CTkFrame):
    def __init__(self, master, title: str = None, theme: str = "dark", **kwargs):
        colors = get_colors(theme)
        super().__init__(master, fg_color=colors["bg_card"], corner_radius=12,
                         border_width=1, border_color=colors["border"], **kwargs)
        if title:
            ctk.CTkLabel(self, text=title,
                         font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                         text_color=colors["text_primary"]).pack(anchor="w", padx=16, pady=(16, 8))


class ModernButton(ctk.CTkButton):
    def __init__(self, master, text: str = "", icon: str = None, variant: str = "primary",
                 theme: str = "light", width: int = 100, height: int = 32, **kwargs):
        colors = get_colors(theme)
        variants = {
            "primary":   {"fg_color": colors["accent"],      "hover_color": colors["accent_hover"],  "text_color": "#ffffff"},
            "secondary": {"fg_color": colors["bg_tertiary"], "hover_color": colors["border"],        "text_color": colors["text_primary"]},
            "success":   {"fg_color": colors["success"],     "hover_color": colors["success_light"], "text_color": "#ffffff"},
            "danger":    {"fg_color": colors["danger"],      "hover_color": colors["danger_light"],  "text_color": "#ffffff"},
            "ghost":     {"fg_color": "transparent",         "hover_color": colors["bg_tertiary"],   "text_color": colors["text_primary"]},
        }
        style = variants.get(variant, variants["primary"])
        super().__init__(master, text=f"{icon} {text}" if icon else text,
                         font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                         corner_radius=6, width=width, height=height, **style, **kwargs)


class ModernEntry(ctk.CTkEntry):
    def __init__(self, master, placeholder: str = "", icon: str = None, theme: str = "light",
                 width: int = 200, height: int = 32, **kwargs):
        colors = get_colors(theme)
        super().__init__(master, placeholder_text=placeholder,
                         font=ctk.CTkFont(family="Segoe UI", size=11),
                         fg_color=colors["bg_secondary"], border_color=colors["border"],
                         text_color=colors["text_primary"], placeholder_text_color=colors["text_muted"],
                         corner_radius=6, width=width, height=height, border_width=1, **kwargs)
        self.bind("<FocusIn>",  lambda e: self.configure(border_color=colors["accent"]))
        self.bind("<FocusOut>", lambda e: self.configure(border_color=colors["border"]))


class ModernSwitch(ctk.CTkSwitch):
    def __init__(self, master, text: str = "", theme: str = "dark", **kwargs):
        colors = get_colors(theme)
        super().__init__(master, text=text,
                         font=ctk.CTkFont(family="Segoe UI", size=13),
                         text_color=colors["text_primary"], fg_color=colors["bg_tertiary"],
                         progress_color=colors["accent"], button_color=colors["text_primary"],
                         button_hover_color=colors["accent_hover"], **kwargs)


class StatusBadge(ctk.CTkFrame):
    def __init__(self, master, status: str = "unknown", theme: str = "dark", **kwargs):
        colors = get_colors(theme)
        status_config = {
            "free":     {"text": "🔵 LIVRE",   "bg": colors["free_bg"],    "fg": colors["free"]},
            "occupied": {"text": "🟢 OCUPADO", "bg": colors["occupied_bg"],"fg": colors["occupied"]},
            "online":   {"text": "🟢 ONLINE",  "bg": colors["success_bg"], "fg": colors["success"]},
            "offline":  {"text": "🔴 OFFLINE", "bg": colors["danger_bg"],  "fg": colors["danger"]},
        }
        config = status_config.get(status, {"text": "⚪ N/A", "bg": colors["bg_tertiary"], "fg": colors["text_muted"]})
        super().__init__(master, fg_color=config["bg"], corner_radius=6, **kwargs)
        ctk.CTkLabel(self, text=config["text"],
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                     text_color=config["fg"]).pack(padx=10, pady=4)


class StatCard(ctk.CTkFrame):
    """Card de estatística compacto."""

    def __init__(self, master, title: str, value: str = "0", icon: str = "",
                 color: str = None, theme: str = "dark", **kwargs):
        colors = get_colors(theme)
        super().__init__(master, fg_color=colors["bg_card"], corner_radius=10,
                         border_width=1, border_color=colors["border"], **kwargs)
        self.color = color or colors["accent"]

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=14, pady=10)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x")

        if icon:
            ctk.CTkLabel(header, text=icon, font=ctk.CTkFont(size=15),
                         text_color=self.color).pack(side="left")
        ctk.CTkLabel(header, text=title,
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=colors["text_secondary"]).pack(
            side="left", padx=(5, 0) if icon else 0)

        self.value_label = ctk.CTkLabel(container, text=value,
                                         font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                                         text_color=self.color)
        self.value_label.pack(anchor="w", pady=(3, 0))

    def set_value(self, value: str):
        self.value_label.configure(text=value)


class ProgressIndicator(ctk.CTkFrame):
    def __init__(self, master, theme: str = "dark", **kwargs):
        colors = get_colors(theme)
        super().__init__(master, fg_color="transparent", **kwargs)
        self.progress_bar = ctk.CTkProgressBar(self, fg_color=colors["bg_tertiary"],
                                                progress_color=colors["accent"], height=6, corner_radius=3)
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.progress_bar.set(0)
        self.status_label = ctk.CTkLabel(self, text="Aguardando...",
                                          font=ctk.CTkFont(family="Segoe UI", size=12),
                                          text_color=colors["text_secondary"])
        self.status_label.pack()

    def set_progress(self, value: float, message: str = None):
        self.progress_bar.set(value)
        if message:
            self.status_label.configure(text=message)

    def reset(self):
        self.progress_bar.set(0)
        self.status_label.configure(text="Aguardando...")


# ─────────────────────────────────────────────────────────────────────────────
# ModernTable — 1 painel por coluna com bordas reais em todas as células
# ─────────────────────────────────────────────────────────────────────────────

class ModernTable(ctk.CTkFrame):
    """
    Tabela de alto desempenho — cada coluna é seu próprio ttk.Treeview.

    Bordas de célula:
        • Horizontal: rowheight = ROW_HEIGHT + 1, fieldbackground = BORDER_COLOR
          → o pixel extra de fundo aparece como divisória entre linhas.
        • Vertical:  separadores tk.Frame(width=1) entre cada painel.
        → Resultado: grade completa em torno de cada célula.

    Destaque:
        • Somente IP ADDRESS recebe cor escura, texto branco, bold.
        • Todas as outras colunas (inclusive STATUS) usam estilo uniforme.
    """

    # Cores das colunas normais (todas menos IP ADDRESS)
    STATUS_COLORS = {
        "occupied": {"bg": "#f0fdf4", "bg_blink": "#dcfce7", "fg": "#166534"},
        "free":     {"bg": "#eff6ff", "bg_blink": "#dbeafe", "fg": "#1e3a8a"},
        "unknown":  {"bg": "#f8fafc", "bg_blink": "#f1f5f9", "fg": "#475569"},
    }

    # Cores exclusivas do painel IP ADDRESS (escuro, pisca entre dois tons escuros)
    IP_COLORS = {
        "occupied": {"bg": "#15803d", "bg_blink": "#166534", "fg": "#ffffff"},
        "free":     {"bg": "#1e40af", "bg_blink": "#1e3a8a", "fg": "#ffffff"},
        "unknown":  {"bg": "#475569", "bg_blink": "#334155", "fg": "#ffffff"},
    }

    HIGHLIGHT_COL = "IP ADDRESS"
    ROW_HEIGHT    = 26
    BORDER_COLOR  = "#cbd5e1"
    FONT          = ("Segoe UI", 9)
    FONT_BOLD     = ("Segoe UI", 9, "bold")
    HEADING_FONT  = ("Segoe UI", 9, "bold")

    # Colunas que devem expandir para preencher espaço restante
    _EXPAND_COLS  = {"NAME", "MANUFACTURER", "MODEL", "SYSTEM", "RAM", "LAST INVENTORY"}

    def __init__(self, master, columns: List[Tuple[str, int]], theme: str = "light",
                 on_row_click: Callable = None, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=8, **kwargs)

        self._columns = columns          # lista original [(name, width), ...]
        self.on_row_click = on_row_click
        self._ip_to_iid: dict = {}
        self._row_counter = 0
        self.blink_state  = False
        self._is_building = False
        self._syncing     = False
        self._vsb         = None

        # Lista de (col_name, treeview, is_highlight) — 1 por coluna
        self._col_trees: List[tuple] = []

        self._setup_styles()
        self._build_widgets()

    # ── Estilos ────────────────────────────────────────────────────────────

    def _setup_styles(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except Exception:
            pass

        common = dict(
            font=self.FONT,
            rowheight=self.ROW_HEIGHT + 1,   # +1 → pixel de borda horizontal
            borderwidth=0, relief="flat",
            background="#ffffff",
            fieldbackground=self.BORDER_COLOR,
            foreground="#374151",
        )
        heading = dict(font=self.HEADING_FONT, background="#1e293b",
                       foreground="#f8fafc", relief="flat", borderwidth=0)

        for i in range(len(self._columns)):
            name = f"Col{i}.Treeview"
            s.configure(name, **common)
            s.configure(f"{name}.Heading", **heading)
            s.map(f"{name}.Heading", background=[("active", "#334155")])
            s.map(name,
                  background=[("selected", "#2563eb")],
                  foreground=[("selected", "#ffffff")])
            s.layout(name, [(f"{name}.treearea", {"sticky": "nswe"})])

    # ── Construção dos widgets ─────────────────────────────────────────────

    def _build_widgets(self):
        outer = tk.Frame(self, bg=self.BORDER_COLOR)
        outer.pack(fill="both", expand=True)

        # Scrollbar vertical (compartilhada)
        self._vsb = ttk.Scrollbar(outer, orient="vertical", command=self._scroll_all)
        self._vsb.pack(side="right", fill="y")

        for i, (col_name, width) in enumerate(self._columns):
            # Separador de 1px entre cada coluna (borda vertical)
            if i > 0:
                tk.Frame(outer, width=1, bg=self.BORDER_COLOR).pack(side="left", fill="y")

            is_highlight = (col_name == self.HIGHLIGHT_COL)
            should_expand = col_name in self._EXPAND_COLS

            frame = tk.Frame(outer, width=width, bg="#1e293b")
            if should_expand:
                frame.pack(side="left", fill="both", expand=True)
            else:
                frame.pack(side="left", fill="y")
            frame.pack_propagate(False)

            style_name = f"Col{i}.Treeview"

            tree = ttk.Treeview(
                frame, columns=[col_name], show="headings",
                style=style_name, selectmode="browse",
            )

            # Apenas a primeira árvore envia yscroll → evita loops
            if i == 0:
                tree.configure(yscrollcommand=self._on_yscroll)

            tree.pack(fill="both", expand=True)
            tree.heading(col_name, text=col_name, anchor="center")
            tree.column(col_name, width=width,
                        minwidth=max(width // 2, 30),
                        anchor="center", stretch=should_expand)

            # Configurar tags de cor
            if is_highlight:
                for status, cfg in self.IP_COLORS.items():
                    tree.tag_configure(
                        f"ip_{status}",
                        background=cfg["bg"], foreground=cfg["fg"],
                        font=self.FONT_BOLD,
                    )
            else:
                for status, cfg in self.STATUS_COLORS.items():
                    tree.tag_configure(
                        status,
                        background=cfg["bg"], foreground=cfg["fg"],
                        font=self.FONT,
                    )

            # Bindings
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                tree.bind(seq, self._redirect_scroll)
            tree.bind("<<TreeviewSelect>>",
                      lambda e, idx=i: self._on_col_select(e, idx))

            self._col_trees.append((col_name, tree, is_highlight))

    # ── Scroll sync ────────────────────────────────────────────────────────

    def _on_yscroll(self, first, last):
        """Chamado apenas pela 1ª árvore; sincroniza todas as outras."""
        if self._syncing:
            return
        self._syncing = True
        if self._vsb:
            self._vsb.set(first, last)
        for i, (_, tree, _) in enumerate(self._col_trees):
            if i != 0:
                tree.yview_moveto(first)
        self._syncing = False

    def _scroll_all(self, *args):
        """Chamado pela scrollbar vertical."""
        for _, tree, _ in self._col_trees:
            tree.yview(*args)

    def _redirect_scroll(self, event):
        """Mouse wheel em qualquer painel → scroll na 1ª árvore (propaga)."""
        first_tree = self._col_trees[0][1]
        if event.num == 4:
            first_tree.yview_scroll(-1, "units")
        elif event.num == 5:
            first_tree.yview_scroll(1, "units")
        else:
            first_tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    # ── Seleção sincronizada ───────────────────────────────────────────────

    def _on_col_select(self, event, col_idx: int):
        """Seleciona a mesma linha em todos os painéis."""
        src_tree = self._col_trees[col_idx][1]
        sel = src_tree.selection()
        if not sel:
            return
        iid = sel[0]

        for i, (_, tree, _) in enumerate(self._col_trees):
            if i != col_idx:
                try:
                    tree.selection_set(iid)
                except Exception:
                    pass

        if self.on_row_click:
            all_vals = []
            for _, tree, _ in self._col_trees:
                vals = tree.item(iid, "values")
                all_vals.extend(vals)
            tags = src_tree.item(iid, "tags")
            status_tag = tags[0] if tags else "unknown"
            if status_tag.startswith("ip_"):
                status_tag = status_tag[3:]
            self.on_row_click(list(all_vals), status_tag)

    # ── API pública ────────────────────────────────────────────────────────

    def set_building(self, building: bool):
        self._is_building = building

    def clear(self):
        for _, tree, _ in self._col_trees:
            tree.delete(*tree.get_children())
        self._ip_to_iid.clear()
        self._row_counter = 0

    def add_row(self, data: List[str], status: str = "unknown", ip: str = None):
        """Insere uma linha em todos os painéis com mesmo iid."""
        iid = str(self._row_counter)
        self._row_counter += 1

        for i, (col_name, tree, is_highlight) in enumerate(self._col_trees):
            value = data[i] if i < len(data) else ""
            if is_highlight:
                tag = f"ip_{status}" if status in self.IP_COLORS else "ip_unknown"
            else:
                tag = status if status in self.STATUS_COLORS else "unknown"
            tree.insert("", "end", iid=iid, values=[value], tags=(tag,))

        if ip:
            self._ip_to_iid[ip] = iid
        return iid

    def update_row(self, ip: str, data: List[str], status: str) -> bool:
        """Atualiza uma linha existente em todos os painéis."""
        if ip not in self._ip_to_iid:
            return False
        iid = self._ip_to_iid[ip]

        for i, (col_name, tree, is_highlight) in enumerate(self._col_trees):
            value = data[i] if i < len(data) else ""
            if is_highlight:
                tag = f"ip_{status}" if status in self.IP_COLORS else "ip_unknown"
            else:
                tag = status if status in self.STATUS_COLORS else "unknown"
            tree.item(iid, values=[value], tags=(tag,))
        return True

    def toggle_blink(self):
        """
        Blink O(1) — alterna cor de fundo via tag_configure.
        • Colunas normais: blink suave (tons claros)
        • IP ADDRESS: blink escuro (tons escuros)
        """
        if self._is_building:
            return
        self.blink_state = not self.blink_state

        for col_name, tree, is_highlight in self._col_trees:
            if is_highlight:
                for status, cfg in self.IP_COLORS.items():
                    color = cfg["bg_blink"] if self.blink_state else cfg["bg"]
                    tree.tag_configure(f"ip_{status}", background=color)
            else:
                for status, cfg in self.STATUS_COLORS.items():
                    color = cfg["bg_blink"] if self.blink_state else cfg["bg"]
                    tree.tag_configure(status, background=color)