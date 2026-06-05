# outlook_checker.py
# 受信メール確認アプリ — 通常はコンパクト表示、▼で詳細一覧を展開

import tkinter as tk
from tkinter import messagebox
import threading
import datetime
import ctypes

# コンソールウィンドウを非表示
try:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
except Exception:
    pass

# DPI対応（テキストのぼやけ防止）
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

try:
    import win32com.client
    import pythoncom
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

BLACKLIST_KEYWORDS = [
    "弊社", "ご提案", "営業", "サービスのご案内", "ご紹介させていただ",
    "ご連絡差し上げ", "セミナー", "キャンペーン", "お見積", "業務提携",
    "代理店", "ソリューション", "資料をお送り", "ご検討いただけ",
    "新サービス", "掲載のご", "広告", "SEO", "採用支援", "人材紹介",
    "保険のご", "投資", "融資", "ローンのご", "弊社製品",
    "無料でご利用", "初回無料", "お試し無料", "ご支援でき",
    "営業担当", "ご提供でき", "ご活用いただける",
]

REFRESH_INTERVAL_MS = 15 * 60 * 1000

COMPACT_W, COMPACT_H = 560, 114
EXPAND_W,  EXPAND_H  = 920, 740

C = {
    "bg":            "#0A0A18",
    "header":        "#161628",
    "bar_bg":        "#0D0D20",
    "accent_stripe": "#00C8FF",
    "subheader":     "#1A1A3A",
    "card_cust":     "#FFFFFF",
    "card_other":    "#F4F4F4",
    "border_cust":   "#00A8E0",
    "border_other":  "#CCCCCC",
    "accent":        "#00C8FF",
    "accent2":       "#0090CC",
    "text":          "#F0F4FF",
    "text_dim":      "#8090B8",
    "text_muted":    "#7080A8",
    "badge_cust_bg": "#E0F6FF",
    "badge_cust_fg": "#0080B0",
    "badge_oth_bg":  "#EEEEEE",
    "badge_oth_fg":  "#777777",
    "new_bg":        "#E63060",
    "divider":       "#181830",
    "btn_open_bg":   "#0A3060",
    "btn_open_fg":   "#00C8FF",
    "btn_open_hov":  "#0E3E7A",
    "btn_del_bg":    "#3A0A14",
    "btn_del_fg":    "#E63060",
    "btn_del_hov":   "#4E1020",
    "ico_btn_bg":    "#141430",
    "ico_btn_hov":   "#1E2248",
    "ico_btn_fg":    "#5060A0",
    "ico_btn_act":   "#00C8FF",
    "unread_dot":    "#00C8FF",
    "sep":           "#1A1A38",
    "count_total_fg":"#9AAACA",
    "count_cust_fg": "#00C8FF",
    "status_bg":     "#080816",
}


# ------------------------------------------------------------------ Outlook操作

def is_customer_email(body: str) -> bool:
    for kw in BLACKLIST_KEYWORDS:
        if kw in body:
            return False
    return True


def fetch_emails() -> list:
    if not HAS_WIN32:
        return _dummy_emails()
    try:
        pythoncom.CoInitialize()
        outlook = win32com.client.Dispatch("Outlook.Application")
        ns = outlook.GetNamespace("MAPI")
        inbox = ns.GetDefaultFolder(6)
        store_id = inbox.StoreID
        cutoff = datetime.datetime.now() - datetime.timedelta(days=7)
        items = inbox.Items
        items.Sort("[ReceivedTime]", True)
        result = []
        for msg in items:
            try:
                rt = msg.ReceivedTime
                received = datetime.datetime(rt.year, rt.month, rt.day,
                                             rt.hour, rt.minute, rt.second)
                if received < cutoff:
                    break
                body = msg.Body or ""
                preview = body.replace('\r', '').replace('\n', ' ').strip()
                preview = preview[:160] + ("…" if len(preview) > 160 else "")
                result.append({
                    "sender":       msg.SenderName or "不明",
                    "sender_email": msg.SenderEmailAddress or "",
                    "received":     received,
                    "preview":      preview,
                    "is_customer":  is_customer_email(body),
                    "unread":       bool(msg.UnRead),
                    "entry_id":     msg.EntryID,
                    "store_id":     store_id,
                })
            except Exception:
                continue
        return result
    except Exception:
        return []
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def outlook_open_email(entry_id, store_id):
    try:
        pythoncom.CoInitialize()
        outlook = win32com.client.Dispatch("Outlook.Application")
        ns = outlook.GetNamespace("MAPI")
        msg = ns.GetItemFromID(entry_id, store_id)
        msg.Display(False)
        return None
    except Exception as e:
        return str(e)
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def outlook_delete_email(entry_id, store_id):
    try:
        pythoncom.CoInitialize()
        outlook = win32com.client.Dispatch("Outlook.Application")
        ns = outlook.GetNamespace("MAPI")
        msg = ns.GetItemFromID(entry_id, store_id)
        msg.Delete()
        return None
    except Exception as e:
        return str(e)
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def _dummy_emails():
    now = datetime.datetime.now()
    return [
        {"sender": "山田 花子", "sender_email": "hanako@example.com",
         "received": now - datetime.timedelta(hours=1),
         "preview": "先日ホームページを拝見しました。来月の連休に家族4人で宿泊を検討しております。お部屋の空き状況と料金をお教えいただけますでしょうか。",
         "is_customer": True, "unread": True, "entry_id": "", "store_id": ""},
        {"sender": "株式会社〇〇システム", "sender_email": "sales@example-sys.co.jp",
         "received": now - datetime.timedelta(hours=3),
         "preview": "弊社の新サービスをご紹介させていただきたく、ご連絡差し上げました…",
         "is_customer": False, "unread": True, "entry_id": "", "store_id": ""},
        {"sender": "佐藤 次郎", "sender_email": "jiro@mail.com",
         "received": now - datetime.timedelta(hours=5),
         "preview": "2名で宿泊を考えておりますが、○月○日の空き状況を教えていただけますか。",
         "is_customer": True, "unread": False, "entry_id": "", "store_id": ""},
        {"sender": "○○広告代理店", "sender_email": "info@adagency.jp",
         "received": now - datetime.timedelta(days=1),
         "preview": "旅館業界向けSEO対策・広告掲載のご案内です。初回無料でご相談いただ…",
         "is_customer": False, "unread": False, "entry_id": "", "store_id": ""},
        {"sender": "鈴木 美咲", "sender_email": "misaki@gmail.com",
         "received": now - datetime.timedelta(days=2),
         "preview": "食物アレルギー（そば・えび）がある場合、お食事の対応は可能でしょう…",
         "is_customer": True, "unread": False, "entry_id": "", "store_id": ""},
        {"sender": "田中 健一", "sender_email": "kenichi@hotmail.com",
         "received": now - datetime.timedelta(days=3),
         "preview": "チェックインの時間は変更できますか？少し遅れそうで心配しております…",
         "is_customer": True, "unread": False, "entry_id": "", "store_id": ""},
        {"sender": "○○保険サービス", "sender_email": "hoken@service.co.jp",
         "received": now - datetime.timedelta(days=4),
         "preview": "旅館・ホテル向け保険のご提案です。弊社製品は業界最安値水準でご提供…",
         "is_customer": False, "unread": False, "entry_id": "", "store_id": ""},
    ]


# ------------------------------------------------------------------ カスタムボタン

def _rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    """Canvas上に角丸矩形を描画する"""
    pts = [
        x1+r, y1,   x2-r, y1,
        x2,   y1,   x2,   y1+r,
        x2,   y2-r, x2,   y2,
        x2-r, y2,   x1+r, y2,
        x1,   y2,   x1,   y2-r,
        x1,   y1+r, x1,   y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


def make_icon_btn(parent, icon, label, icon_color, bg, hover_bg, command, pady=6):
    frame = tk.Frame(parent, bg=bg, cursor="hand2", padx=10, pady=pady)

    ico_lbl = tk.Label(frame, text=icon,
                        font=("Yu Gothic UI", 11),
                        bg=bg, fg=icon_color)
    ico_lbl.pack(side="left", padx=(0, 5))

    txt_lbl = tk.Label(frame, text=label,
                        font=("Yu Gothic UI", 10),
                        bg=bg, fg=icon_color)
    txt_lbl.pack(side="left")

    def _click(e):
        command()

    def _enter(e):
        frame.config(bg=hover_bg)
        ico_lbl.config(bg=hover_bg)
        txt_lbl.config(bg=hover_bg)

    def _leave(e):
        frame.config(bg=bg)
        ico_lbl.config(bg=bg)
        txt_lbl.config(bg=bg)

    for w in (frame, ico_lbl, txt_lbl):
        w.bind("<Button-1>", _click)
        w.bind("<Enter>", _enter)
        w.bind("<Leave>", _leave)

    return frame


def _bind_drag_recursive(widget, drag_start_cb, drag_move_cb):
    """ウィジェットとその全子孫にドラッグをバインド"""
    widget.bind("<ButtonPress-1>", drag_start_cb, add="+")
    widget.bind("<B1-Motion>",     drag_move_cb,  add="+")
    for child in widget.winfo_children():
        _bind_drag_recursive(child, drag_start_cb, drag_move_cb)


# ------------------------------------------------------------------ アプリ本体

class OutlookCheckerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.overrideredirect(True)          # フレームレス
        self.root.configure(bg=C["bar_bg"])
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.emails: list = []
        self.prev_customer_count = -1
        self._refresh_job = None
        self.expanded = False
        self._drag_x = 0
        self._drag_y = 0

        self._build_compact_bar()
        self._build_detail_panel()
        self._set_compact()
        self._refresh()

    # ------------------------------------------------------------------ コンパクトバー
    def _build_compact_bar(self):
        bar = tk.Frame(self.root, bg=C["bar_bg"], height=COMPACT_H)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # 左端アクセントライン（全高に伸ばすため最初にpack）
        tk.Frame(bar, bg=C["accent_stripe"], width=3).pack(side="left", fill="y")

        # ---- 左: メールアイコン＋タイトル ----
        left = tk.Frame(bar, bg=C["bar_bg"])
        left.pack(side="left", padx=(14, 0), pady=16)

        ico = tk.Label(left, text="✉",
                        font=("Yu Gothic UI", 36),
                        bg=C["bar_bg"], fg=C["accent"])
        ico.pack(side="left", padx=(0, 10))

        title_block = tk.Frame(left, bg=C["bar_bg"])
        title_block.pack(side="left")

        tk.Label(title_block, text="受信メール確認",
                  font=("Yu Gothic UI", 12, "bold"),
                  bg=C["bar_bg"], fg=C["text"]).pack(anchor="w")

        self.lbl_updated = tk.Label(title_block, text="更新中…",
                                     font=("Yu Gothic UI", 9),
                                     bg=C["bar_bg"], fg=C["text_muted"])
        self.lbl_updated.pack(anchor="w")

        self.lbl_new = tk.Label(left, text="  NEW  ",
                                 font=("Yu Gothic UI", 8, "bold"),
                                 bg=C["new_bg"], fg="white", padx=4, pady=3)

        # ---- 中央: カウンター ----
        ctr = tk.Frame(bar, bg=C["bar_bg"])
        ctr.pack(side="left", padx=(24, 0))

        # 全件数
        total_box = tk.Frame(ctr, bg=C["bar_bg"])
        total_box.pack(side="left", padx=(0, 4))

        tk.Label(total_box, text="全メール",
                  font=("Yu Gothic UI", 8),
                  bg=C["bar_bg"], fg=C["text_muted"]).pack(anchor="center", pady=(6, 0))
        self.lbl_total = tk.Label(total_box, text="—",
                                   font=("Yu Gothic UI", 28, "bold"),
                                   bg=C["bar_bg"], fg=C["count_total_fg"])
        self.lbl_total.pack(anchor="center")

        # 区切り
        tk.Frame(ctr, bg=C["sep"], width=1).pack(
            side="left", fill="y", padx=12, pady=10)

        # お客様数（大・水色）
        cust_box = tk.Frame(ctr, bg=C["bar_bg"])
        cust_box.pack(side="left", padx=(4, 0))

        cust_hdr = tk.Frame(cust_box, bg=C["bar_bg"])
        cust_hdr.pack(anchor="center", pady=(6, 0))
        tk.Label(cust_hdr, text="●",
                  font=("Yu Gothic UI", 7),
                  bg=C["bar_bg"], fg=C["accent"]).pack(side="left", padx=(0, 3))
        tk.Label(cust_hdr, text="お客様",
                  font=("Yu Gothic UI", 8),
                  bg=C["bar_bg"], fg=C["accent"]).pack(side="left")

        self.lbl_cust = tk.Label(cust_box, text="—",
                                  font=("Yu Gothic UI", 28, "bold"),
                                  bg=C["bar_bg"], fg=C["count_cust_fg"])
        self.lbl_cust.pack(anchor="center")

        # ---- 右: アクションボタン ----
        right = tk.Frame(bar, bg=C["bar_bg"])
        right.pack(side="right", padx=(4, 8))

        # 閉じるボタン
        self._make_bar_btn(right, "×", C["ico_btn_fg"], "#4A1020", self._on_close).pack(
            side="right", padx=(2, 0))

        # 展開ボタン ▼
        self.btn_toggle = self._make_bar_btn(right, "▼", C["accent"], C["ico_btn_hov"],
                                              self._toggle)
        self.btn_toggle.pack(side="right", padx=2)

        # 更新ボタン ↻
        self._make_bar_btn(right, "↻", C["ico_btn_fg"], C["ico_btn_hov"],
                           self._manual_refresh).pack(side="right", padx=2)


        # バー内の全ウィジェットにドラッグをバインド
        self.root.after(100, lambda: _bind_drag_recursive(
            bar, self._drag_start, self._drag_move))

    def _make_bar_btn(self, parent, text, fg, hover_bg, command):
        btn = tk.Label(parent, text=text,
                        font=("Yu Gothic UI", 15),
                        bg=C["bar_bg"], fg=fg,
                        cursor="hand2", padx=10, pady=6)

        def _enter(e):
            btn.config(bg=hover_bg)

        def _leave(e):
            btn.config(bg=C["bar_bg"])

        btn.bind("<Enter>", _enter)
        btn.bind("<Leave>", _leave)
        btn.bind("<Button-1>", lambda e: command())
        return btn

    # ------------------------------------------------------------------ 詳細パネル
    def _build_detail_panel(self):
        self.detail_panel = tk.Frame(self.root, bg=C["bg"])

        sub = tk.Frame(self.detail_panel, bg=C["subheader"])
        sub.pack(fill="x")
        self.lbl_next = tk.Label(sub, text="",
                                  font=("Yu Gothic UI", 9),
                                  bg=C["subheader"], fg=C["text_muted"])
        self.lbl_next.pack(side="left", padx=16, pady=6)

        outer = tk.Frame(self.detail_panel, bg=C["bg"])
        outer.pack(fill="both", expand=True, padx=0, pady=0)

        self._sb = tk.Scrollbar(outer, orient="vertical")
        self._sb.pack(side="right", fill="y")
        self.canvas = tk.Canvas(outer, bg=C["bg"], highlightthickness=0,
                                yscrollcommand=self._sb.set)
        self._sb.config(command=self.canvas.yview)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.list_frame = tk.Frame(self.canvas, bg=C["bg"])
        self._win_id = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        self.list_frame.bind("<Configure>",
                              lambda e: self.canvas.configure(
                                  scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                          lambda e: self.canvas.itemconfig(self._win_id, width=e.width))
        def _on_mousewheel(e):
            first, last = self.canvas.yview()
            if last < 0.999:
                self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        self._on_mousewheel = _on_mousewheel
        self.canvas.bind("<MouseWheel>", _on_mousewheel)

        ft = tk.Frame(self.detail_panel, bg=C["header"])
        ft.pack(fill="x", side="bottom")

        ft_inner = tk.Frame(ft, bg=C["header"])
        ft_inner.pack(pady=7)
        tk.Label(ft_inner, text="●",
                  font=("Yu Gothic UI", 9),
                  bg=C["header"], fg=C["accent"]).pack(side="left", padx=(0, 4))
        tk.Label(ft_inner, text="水色 ＝ お客様メール",
                  font=("Yu Gothic UI", 9),
                  bg=C["header"], fg=C["text_muted"]).pack(side="left")
        tk.Label(ft_inner, text="　　",
                  bg=C["header"]).pack(side="left")
        tk.Label(ft_inner, text="○",
                  font=("Yu Gothic UI", 9),
                  bg=C["header"], fg=C["text_muted"]).pack(side="left", padx=(0, 4))
        tk.Label(ft_inner, text="グレー ＝ 営業・その他",
                  font=("Yu Gothic UI", 9),
                  bg=C["header"], fg=C["text_muted"]).pack(side="left")

    # ------------------------------------------------------------------ 展開/収納
    def _toggle(self):
        if self.expanded:
            self._set_compact()
        else:
            self._set_expanded()

    def _set_compact(self):
        self.expanded = False
        self.detail_panel.pack_forget()
        self.btn_toggle.config(text="▼")
        self.root.attributes("-topmost", True)
        # 現在のウィンドウ中心を基準に縮小
        cx = self.root.winfo_x() + self.root.winfo_width() // 2
        cy = self.root.winfo_y() + self.root.winfo_height() // 2
        x = cx - COMPACT_W // 2
        y = cy - COMPACT_H // 2
        self.root.geometry(f"{COMPACT_W}x{COMPACT_H}+{x}+{y}")
        self.root.resizable(False, False)

    def _set_expanded(self):
        self.expanded = True
        self.detail_panel.pack(fill="both", expand=True)
        self.btn_toggle.config(text="▲")
        self.root.attributes("-topmost", False)
        # 現在のウィンドウ中心を基準に拡大
        cx = self.root.winfo_x() + COMPACT_W // 2
        cy = self.root.winfo_y() + COMPACT_H // 2
        x = max(0, cx - EXPAND_W // 2)
        y = max(0, cy - EXPAND_H // 2)
        # 画面外にはみ出さないよう補正
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = min(x, sw - EXPAND_W)
        y = min(y, sh - EXPAND_H)
        self.root.geometry(f"{EXPAND_W}x{EXPAND_H}+{x}+{y}")
        self.root.resizable(True, True)

    def _on_close(self):
        self.root.destroy()

    def _drag_start(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _drag_move(self, event):
        self.root.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    # ------------------------------------------------------------------ カード描画
    def _render_emails(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        # スクロール位置をリセット
        self.canvas.yview_moveto(0)

        # 上部余白
        tk.Frame(self.list_frame, bg=C["bg"], height=10).pack(fill="x")

        if not self.emails:
            tk.Label(self.list_frame, text="メールが見つかりませんでした",
                      font=("Yu Gothic UI", 12),
                      bg=C["bg"], fg=C["text_muted"], pady=60).pack()
            return

        ordered = sorted(self.emails,
                          key=lambda x: (not x["is_customer"],
                                         -x["received"].timestamp()))
        for email in ordered:
            self._render_card(email)

        # 下部余白
        tk.Frame(self.list_frame, bg=C["bg"], height=10).pack(fill="x")

        # カード内の全ウィジェットにもマウスホイールをバインド
        def _bind_wheel(widget):
            widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
            for child in widget.winfo_children():
                _bind_wheel(child)
        self.root.after(50, lambda: _bind_wheel(self.list_frame))

    def _render_card(self, email: dict):
        is_cust    = email["is_customer"]
        unread     = email.get("unread", False)
        card_bg    = C["card_cust"] if is_cust else C["card_other"]
        border_col = C["border_cust"] if is_cust else C["border_other"]
        sender_fg  = "#0070A0" if is_cust else "#222222"

        # カードを包むラッパー
        wrapper = tk.Frame(self.list_frame, bg=C["bg"])
        wrapper.pack(fill="x", padx=12, pady=(0, 10))

        R = 16  # 角丸半径

        # 角丸描画用Canvas
        cv = tk.Canvas(wrapper, bg=C["bg"], highlightthickness=0, bd=0)
        cv.pack(fill="x")

        # コンテンツフレームはR分内側に配置（四隅の角丸を見せるため）
        inner = tk.Frame(cv, bg=card_bg)
        inner_win = cv.create_window(R, R, anchor="nw", window=inner)

        # コンテンツ配置
        body = tk.Frame(inner, bg=card_bg)
        body.pack(side="left", fill="x", expand=True, padx=12, pady=8)

        row1 = tk.Frame(body, bg=card_bg)
        row1.pack(fill="x")

        badge_ibg = C["badge_cust_bg"] if is_cust else C["badge_oth_bg"]
        badge_ifg = C["badge_cust_fg"] if is_cust else C["badge_oth_fg"]
        badge_txt = "お客様" if is_cust else "その他"

        badge_frame = tk.Frame(row1, bg=badge_ibg, padx=6, pady=2)
        badge_frame.pack(side="left", padx=(0, 10))
        tk.Label(badge_frame, text=badge_txt,
                  font=("Yu Gothic UI", 9, "bold") if is_cust else ("Yu Gothic UI", 9),
                  bg=badge_ibg, fg=badge_ifg).pack(side="left")

        if unread:
            tk.Label(row1, text="●",
                      font=("Yu Gothic UI", 10),
                      bg=card_bg, fg=C["unread_dot"]).pack(side="left", padx=(0, 5))

        sender_weight = "bold" if unread else "normal"
        tk.Label(row1, text=email["sender"],
                  font=("Yu Gothic UI", 13, sender_weight),
                  bg=card_bg, fg=sender_fg).pack(side="left")

        tk.Label(row1, text=email["received"].strftime("%m/%d  %H:%M"),
                  font=("Yu Gothic UI", 10),
                  bg=card_bg, fg="#555555").pack(side="right")

        row2 = tk.Frame(body, bg=card_bg)
        row2.pack(fill="x", pady=(3, 0))
        tk.Label(row2, text=email["sender_email"],
                  font=("Yu Gothic UI", 9),
                  bg=card_bg, fg="#666666").pack(side="left")

        row3 = tk.Frame(body, bg=card_bg)
        row3.pack(fill="x", pady=(7, 0))
        tk.Label(row3, text=email["preview"],
                  font=("Yu Gothic UI", 10),
                  bg=card_bg, fg="#111111",
                  anchor="w", justify="left", wraplength=620).pack(fill="x", anchor="w")

        entry_id = email.get("entry_id", "")
        store_id = email.get("store_id", "")

        btn_area = tk.Frame(inner, bg=card_bg)
        btn_area.pack(side="right", padx=10, pady=8)

        make_icon_btn(
            btn_area,
            icon="↗", label="開く",
            icon_color=C["btn_open_fg"],
            bg=C["btn_open_bg"], hover_bg=C["btn_open_hov"],
            command=lambda eid=entry_id, sid=store_id: self._on_open(eid, sid)
        ).pack(fill="x", pady=(0, 6))

        make_icon_btn(
            btn_area,
            icon="✕", label="削除",
            icon_color=C["btn_del_fg"],
            bg=C["btn_del_bg"], hover_bg=C["btn_del_hov"],
            command=lambda eid=entry_id, sid=store_id, e=email: self._on_delete(eid, sid, e),
            pady=8
        ).pack(fill="x")

        # 角丸描画
        def _redraw(cw=None, event=None):
            cv.delete("rr")
            if cw is None:
                cw = cv.winfo_width()
            if cw < 10:
                return
            ih = inner.winfo_reqheight()
            total_h = ih + R * 2    # 上下R分の余白

            cv.config(height=total_h)
            cv.itemconfig(inner_win, width=cw - R * 2)
            cv.coords(inner_win, R, R)

            # 左アクセント（角丸ごと）
            _rounded_rect(cv, 0, 0, R + 6, total_h, R,
                          fill=border_col, outline="", tags="rr")
            # カード本体（左5pxでアクセントを露出）
            _rounded_rect(cv, 5, 0, cw, total_h, R,
                          fill=card_bg, outline="", tags="rr")
            cv.tag_lower("rr")

        inner.bind("<Configure>",   lambda e: _redraw(cv.winfo_width()))
        cv.bind("<Configure>",      lambda e: _redraw(e.width))

    # ------------------------------------------------------------------ ボタン操作
    def _on_open(self, entry_id, store_id):
        if not entry_id:
            messagebox.showinfo("確認", "デモモードのためOutlookを開けません。\n（実機では正常に開きます）")
            return
        threading.Thread(
            target=lambda: self._open_thread(entry_id, store_id), daemon=True).start()

    def _open_thread(self, entry_id, store_id):
        err = outlook_open_email(entry_id, store_id)
        if err:
            self.root.after(0, lambda: messagebox.showerror("エラー", f"メールを開けませんでした:\n{err}"))

    def _on_delete(self, entry_id, store_id, email):
        sender  = email.get("sender", "")
        preview = email.get("preview", "")[:30]
        if not messagebox.askyesno("削除の確認",
                                    f"このメールをゴミ箱に移動しますか？\n\n送信者: {sender}\n内容: {preview}…",
                                    icon="warning"):
            return
        if not entry_id:
            self.emails = [e for e in self.emails if e is not email]
            self._update_counts()
            self._render_emails()
            return
        threading.Thread(
            target=lambda: self._delete_thread(entry_id, store_id, email), daemon=True).start()

    def _delete_thread(self, entry_id, store_id, email):
        err = outlook_delete_email(entry_id, store_id)
        if err:
            self.root.after(0, lambda: messagebox.showerror("エラー", f"削除できませんでした:\n{err}"))
        else:
            self.root.after(0, lambda: self._remove_email(email))

    def _remove_email(self, email):
        self.emails = [e for e in self.emails if e is not email]
        self._update_counts()
        self._render_emails()

    def _update_counts(self):
        total = len(self.emails)
        cust  = sum(1 for e in self.emails if e["is_customer"])
        self.lbl_total.config(text=str(total))
        self.lbl_cust.config(text=str(cust))

    # ------------------------------------------------------------------ 更新ロジック
    def _refresh(self):
        self.lbl_updated.config(text="更新中…")
        threading.Thread(target=self._fetch_thread, daemon=True).start()

    def _fetch_thread(self):
        emails = fetch_emails()
        self.root.after(0, lambda: self._apply_update(emails))

    def _apply_update(self, emails):
        self.emails = emails
        cust = sum(1 for e in emails if e["is_customer"])

        if self.prev_customer_count >= 0 and cust > self.prev_customer_count:
            self._show_badge()
        self.prev_customer_count = cust

        self._update_counts()

        now_str = datetime.datetime.now().strftime("%H:%M 更新")
        self.lbl_updated.config(text=now_str)
        self.lbl_next.config(text="次回自動更新: 15分後")

        self._render_emails()

        if self._refresh_job:
            self.root.after_cancel(self._refresh_job)
        self._refresh_job = self.root.after(REFRESH_INTERVAL_MS, self._refresh)

    def _show_badge(self):
        self.lbl_new.pack(side="left", padx=8)
        self.root.after(15000, lambda: self.lbl_new.pack_forget())

    def _manual_refresh(self):
        if self._refresh_job:
            self.root.after_cancel(self._refresh_job)
        self._refresh()


def main():
    if not HAS_WIN32:
        print("注意: pywin32 が見つかりません。ダミーデータで起動します。")

    root = tk.Tk()
    # 画面右下に初期配置
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = sw - COMPACT_W - 24
    y = sh - COMPACT_H - 60
    root.geometry(f"{COMPACT_W}x{COMPACT_H}+{x}+{y}")
    OutlookCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
