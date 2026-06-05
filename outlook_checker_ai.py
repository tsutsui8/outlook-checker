# outlook_checker_ai.py
# 受信メール確認アプリ — AI版（Claude APIでお客様メールを判定）

import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
import datetime
import ctypes
import os
import json

# コンソールウィンドウを非表示
try:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
except Exception:
    pass

# DPI対応
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
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

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# 設定・キャッシュファイル
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".outlook_checker_config.json")
CACHE_PATH  = os.path.join(os.path.expanduser("~"), ".outlook_checker_cache.json")

REFRESH_INTERVAL_MS = 15 * 60 * 1000
COMPACT_W = 700
EXPAND_EXTRA_H = 552
EXPAND_W,  EXPAND_H  = 920, 740

C = {
    "bg":            "#0A0A18",
    "header":        "#0D0D20",
    "bar_bg":        "#0D0D20",
    "accent_stripe": "#00C8FF",
    "subheader":     "#1A1A3A",
    "card_cust":     "#FFFFFF",
    "card_other":    "#F4F4F4",
    "card_ai":       "#F0F8FF",   # AI判定中カード（薄い青白）
    "border_cust":   "#00A8E0",
    "border_other":  "#CCCCCC",
    "border_ai":     "#FFB800",   # AI判定中（オレンジ）
    "accent":        "#00C8FF",
    "text":          "#F0F4FF",
    "text_dim":      "#8090B8",
    "text_muted":    "#7080A8",
    "badge_cust_bg": "#E0F6FF",
    "badge_cust_fg": "#0080B0",
    "badge_oth_bg":  "#EEEEEE",
    "badge_oth_fg":  "#777777",
    "badge_ai_bg":   "#FFF4E0",
    "badge_ai_fg":   "#CC8800",
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
}


# ------------------------------------------------------------------ APIキー管理

def load_api_key() -> str:
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f).get("api_key", "")
    except Exception:
        return ""


def save_api_key(key: str):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump({"api_key": key}, f)
    except Exception:
        pass


# ------------------------------------------------------------------ AI判定

_ai_cache: dict = {}   # キャッシュ（メモリ）

def _load_cache():
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_cache():
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(_ai_cache, f, ensure_ascii=False)
    except Exception:
        pass

# 起動時にキャッシュをファイルから読み込む
_ai_cache.update(_load_cache())


def _cache_key(email: dict) -> str:
    """メールの安定したキャッシュキーを返す（entry_id優先）"""
    if email.get("entry_id"):
        return f"id:{email['entry_id']}"
    return f"{email['sender']}:{email.get('body', email['preview'])[:80]}"


def classify_with_ai(email: dict, api_key: str) -> bool:
    """Claude APIでお客様メールか判定。True=お客様、False=その他"""
    sender = email["sender"]
    body   = email.get("body", email["preview"])

    if not HAS_ANTHROPIC or not api_key:
        return _keyword_fallback(body)

    cache_key = _cache_key(email)
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]

    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""以下のメールを読んで、これが「旅館・ホテルへの宿泊問い合わせや予約・質問をしているお客様からのメール」かどうかを判定してください。

送信者: {sender}
本文（先頭300字）:
{body[:300]}

判定基準:
- お客様: 宿泊予約・問い合わせ・質問・キャンセル・アレルギー確認など
- その他: 営業・広告・サービス案内・SEO・採用・投資・保険など

「YES」か「NO」の1単語だけで答えてください。"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}]
        )
        result = "YES" in message.content[0].text.upper()
        _ai_cache[cache_key] = result
        _save_cache()
        return result
    except Exception:
        return _keyword_fallback(body)



BLACKLIST_KEYWORDS = [
    "弊社", "ご提案", "営業", "サービスのご案内", "ご紹介させていただ",
    "ご連絡差し上げ", "セミナー", "キャンペーン", "業務提携",
    "代理店", "ソリューション", "資料をお送り", "ご検討いただけ",
    "新サービス", "掲載のご", "広告", "SEO", "採用支援", "人材紹介",
    "保険のご", "投資", "融資", "ローンのご", "弊社製品",
    "無料でご利用", "初回無料", "お試し無料", "営業担当",
]


def _keyword_fallback(body: str) -> bool:
    for kw in BLACKLIST_KEYWORDS:
        if kw in body:
            return False
    return True

def _cache_size_info() -> str:
    return f"{len(_ai_cache)}件キャッシュ済み"


# ------------------------------------------------------------------ Outlook操作

def fetch_emails(api_key: str) -> list:
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
                sender = msg.SenderName or "不明"

                result.append({
                    "sender":       sender,
                    "sender_email": msg.SenderEmailAddress or "",
                    "received":     received,
                    "preview":      preview,
                    "body":         body,
                    "is_customer":  None,   # AI判定待ち
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


def classify_emails_async(emails: list, api_key: str, callback):
    """各メールをAIで判定してcallbackに通知（バックグラウンドスレッド）"""
    def _worker():
        for email in emails:
            if email["is_customer"] is None:
                result = classify_with_ai(email, api_key)
                email["is_customer"] = result
                # 判定結果を必ずキャッシュ保存
                key = _cache_key(email)
                _ai_cache[key] = result
                _save_cache()
                callback(email)
    threading.Thread(target=_worker, daemon=True).start()


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
        {"sender": "山田 花子", "sender_email": "hanako@gmail.com",
         "received": now - datetime.timedelta(hours=1),
         "preview": "先日ホームページを拝見しました。来月の連休に家族4人で宿泊を検討しております。お部屋の空き状況と料金をお教えいただけますでしょうか。",
         "body": "先日ホームページを拝見しました。来月の連休に家族4人で宿泊を検討しております。",
         "is_customer": None, "unread": True, "entry_id": "", "store_id": ""},
        {"sender": "株式会社〇〇システム", "sender_email": "sales@example-sys.co.jp",
         "received": now - datetime.timedelta(hours=3),
         "preview": "弊社の新サービスをご紹介させていただきたく、ご連絡差し上げました。",
         "body": "弊社の新サービスをご紹介させていただきたく、ご連絡差し上げました。",
         "is_customer": None, "unread": True, "entry_id": "", "store_id": ""},
        {"sender": "佐藤 次郎", "sender_email": "jiro@hotmail.com",
         "received": now - datetime.timedelta(hours=5),
         "preview": "お見積もりをお願いしたいのですが、2名で○月○日から2泊の場合はいくらになりますか？",
         "body": "お見積もりをお願いしたいのですが、2名で○月○日から2泊の場合はいくらになりますか？",
         "is_customer": None, "unread": False, "entry_id": "", "store_id": ""},
        {"sender": "鈴木 美咲", "sender_email": "misaki@gmail.com",
         "received": now - datetime.timedelta(days=1),
         "preview": "食物アレルギー（そば・えび）がある場合、お食事の対応は可能でしょうか。来月の予約を考えております。",
         "body": "食物アレルギー（そば・えび）がある場合、お食事の対応は可能でしょうか。",
         "is_customer": None, "unread": False, "entry_id": "", "store_id": ""},
    ]


# ------------------------------------------------------------------ ヘルパー

def _rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
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
    ico_lbl = tk.Label(frame, text=icon, font=("Yu Gothic UI", 11),
                        bg=bg, fg=icon_color)
    ico_lbl.pack(side="left", padx=(0, 5))
    txt_lbl = tk.Label(frame, text=label, font=("Yu Gothic UI", 10),
                        bg=bg, fg=icon_color)
    txt_lbl.pack(side="left")

    def _enter(e):
        frame.config(bg=hover_bg); ico_lbl.config(bg=hover_bg); txt_lbl.config(bg=hover_bg)
    def _leave(e):
        frame.config(bg=bg); ico_lbl.config(bg=bg); txt_lbl.config(bg=bg)
    for w in (frame, ico_lbl, txt_lbl):
        w.bind("<Button-1>", lambda e: command())
        w.bind("<Enter>", _enter)
        w.bind("<Leave>", _leave)
    return frame


def _bind_drag_recursive(widget, start_cb, move_cb):
    widget.bind("<ButtonPress-1>", start_cb, add="+")
    widget.bind("<B1-Motion>",     move_cb,  add="+")
    for child in widget.winfo_children():
        _bind_drag_recursive(child, start_cb, move_cb)


# ------------------------------------------------------------------ アプリ本体

class OutlookCheckerAI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.overrideredirect(True)
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.emails: list = []
        self.prev_customer_count = -1
        self._refresh_job = None
        self.expanded = False
        self._drag_x = 0
        self._drag_y = 0
        self._win_x = 0
        self._win_y = 0
        self._compact_h = 0
        self.api_key = load_api_key()

        self._build_compact_bar()
        self._build_detail_panel()   # status_area + detail_panel を生成
        self.detail_panel.pack_forget()  # カードリストは初期非表示

        # APIキーが未設定なら初回に確認
        if not self.api_key:
            self.root.after(500, self._ask_api_key)
        else:
            self._refresh()

    # ------------------------------------------------------------------ APIキー
    def _ask_api_key(self):
        key = simpledialog.askstring(
            "Claude APIキー設定",
            "Anthropic APIキーを入力してください。\n"
            "（未入力でもキーワード判定で動作します）\n\n"
            "APIキー取得: https://console.anthropic.com/",
            parent=self.root
        )
        if key and key.strip():
            self.api_key = key.strip()
            save_api_key(self.api_key)
        self._refresh()

    # ------------------------------------------------------------------ コンパクトバー
    def _build_compact_bar(self):
        bar = tk.Frame(self.root, bg=C["bar_bg"], height=124)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Frame(bar, bg=C["accent_stripe"], width=3).pack(side="left", fill="y")

        left = tk.Frame(bar, bg=C["bar_bg"])
        left.pack(side="left", padx=(14, 0), pady=16)

        ico = tk.Label(left, text="✉", font=("Yu Gothic UI", 36),
                        bg=C["bar_bg"], fg=C["accent"])
        ico.pack(side="left", padx=(0, 10))

        title_block = tk.Frame(left, bg=C["bar_bg"])
        title_block.pack(side="left")
        tk.Label(title_block, text="受信メール確認  AI版",
                  font=("Yu Gothic UI", 12, "bold"),
                  bg=C["bar_bg"], fg=C["text"]).pack(anchor="w")
        self.lbl_updated = tk.Label(title_block, text="更新中…",
                                     font=("Yu Gothic UI", 9),
                                     bg=C["bar_bg"], fg=C["text_muted"])
        self.lbl_updated.pack(anchor="w")

        self.lbl_new = tk.Label(left, text="  NEW  ",
                                 font=("Yu Gothic UI", 8, "bold"),
                                 bg=C["new_bg"], fg="white", padx=4, pady=3)

        ctr = tk.Frame(bar, bg=C["bar_bg"])
        ctr.pack(side="left", padx=(24, 0))

        total_box = tk.Frame(ctr, bg=C["bar_bg"])
        total_box.pack(side="left", padx=(0, 4))
        tk.Label(total_box, text="全メール", font=("Yu Gothic UI", 8),
                  bg=C["bar_bg"], fg=C["text_muted"]).pack(anchor="center", pady=(6, 0))
        self.lbl_total = tk.Label(total_box, text="—",
                                   font=("Yu Gothic UI", 28, "bold"),
                                   bg=C["bar_bg"], fg=C["count_total_fg"])
        self.lbl_total.pack(anchor="center")

        tk.Frame(ctr, bg=C["sep"], width=1).pack(side="left", fill="y", padx=12, pady=10)

        cust_box = tk.Frame(ctr, bg=C["bar_bg"])
        cust_box.pack(side="left", padx=(4, 0))
        cust_hdr = tk.Frame(cust_box, bg=C["bar_bg"])
        cust_hdr.pack(anchor="center", pady=(6, 0))
        tk.Label(cust_hdr, text="●", font=("Yu Gothic UI", 7),
                  bg=C["bar_bg"], fg=C["accent"]).pack(side="left", padx=(0, 3))
        tk.Label(cust_hdr, text="お客様", font=("Yu Gothic UI", 8),
                  bg=C["bar_bg"], fg=C["accent"]).pack(side="left")
        self.lbl_cust = tk.Label(cust_box, text="—",
                                  font=("Yu Gothic UI", 28, "bold"),
                                  bg=C["bar_bg"], fg=C["count_cust_fg"])
        self.lbl_cust.pack(anchor="center")

        right = tk.Frame(bar, bg=C["bar_bg"])
        right.pack(side="right", padx=(4, 12))

        self._make_bar_btn(right, "×", "#6070A0", "#4A1020",
                           self._on_close).pack(side="right", padx=4)
        self.btn_toggle = self._make_bar_btn(right, "▼", C["accent"],
                                              C["ico_btn_hov"], self._toggle)
        self.btn_toggle.pack(side="right", padx=4)
        self._make_bar_btn(right, "↻", "#6070A0", C["ico_btn_hov"],
                           self._manual_refresh).pack(side="right", padx=4)
        self._make_bar_btn(right, "⌫", "#6070A0", "#3A1A1A",
                           self._clear_all).pack(side="right", padx=4)

        self.root.after(100, lambda: _bind_drag_recursive(
            bar, self._drag_start, self._drag_move))

    def _make_bar_btn(self, parent, text, fg, hover_bg, command):
        btn = tk.Label(parent, text=text, font=("Segoe UI Symbol", 18),
                        bg=C["bar_bg"], fg=fg, cursor="hand2", padx=12, pady=10)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=C["bar_bg"]))
        btn.bind("<Button-1>", lambda e: command())
        return btn

    # ------------------------------------------------------------------ 詳細パネル
    def _build_detail_panel(self):
        # ── 常時表示エリア（AIステータス＋次回更新） ──
        self.status_area = tk.Frame(self.root, bg=C["bg"])
        self.status_area.pack(fill="x")

        ai_bar = tk.Frame(self.status_area, bg="#0A2040")
        ai_bar.pack(fill="x")
        self.lbl_ai_status = tk.Label(ai_bar, text="🤖 起動中…",
                                       font=("Yu Gothic UI", 9),
                                       bg="#0A2040", fg="#00C8FF")
        self.lbl_ai_status.pack(side="left", padx=16, pady=5)

        sub = tk.Frame(self.status_area, bg=C["subheader"])
        sub.pack(fill="x")
        self.lbl_next = tk.Label(sub, text="次回自動更新: --:--", font=("Yu Gothic UI", 9),
                                  bg=C["subheader"], fg=C["text_muted"])
        self.lbl_next.pack(side="left", padx=16, pady=6)

        # ── 展開時のみ表示エリア（カードリスト） ──
        self.detail_panel = tk.Frame(self.root, bg=C["bg"])

        outer = tk.Frame(self.detail_panel, bg=C["bg"])
        outer.pack(fill="both", expand=True)

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
            if first > 0.001 or last < 0.999:
                self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        self._on_mousewheel = _on_mousewheel
        self.canvas.bind("<MouseWheel>", _on_mousewheel)

        ft = tk.Frame(self.detail_panel, bg=C["header"])
        ft.pack(fill="x", side="bottom")
        ft_inner = tk.Frame(ft, bg=C["header"])
        ft_inner.pack(pady=7)
        tk.Label(ft_inner, text="● 水色 ＝ お客様（AI判定）",
                  font=("Yu Gothic UI", 9), bg=C["header"], fg=C["accent"]).pack(side="left")
        tk.Label(ft_inner, text="　○ グレー ＝ 営業・その他",
                  font=("Yu Gothic UI", 9), bg=C["header"], fg=C["text_muted"]).pack(side="left")

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
        self.root.resizable(False, False)
        self.root.update_idletasks()
        self._compact_h = self.root.winfo_reqheight()
        self.root.geometry(f"{COMPACT_W}x{self._compact_h}+{self._win_x}+{self._win_y}")

    def _set_expanded(self):
        self.expanded = True
        self.detail_panel.pack(fill="both", expand=True)
        self.btn_toggle.config(text="▲")
        self.root.attributes("-topmost", False)
        self.root.resizable(True, True)
        self.root.update_idletasks()
        total_h = self._compact_h + EXPAND_EXTRA_H
        sh = self.root.winfo_screenheight()
        y = self._win_y
        if y + total_h > sh - 40:
            y = sh - total_h - 40
            self._win_y = y
        self.root.geometry(f"{EXPAND_W}x{total_h}+{self._win_x}+{self._win_y}")

    def _on_close(self):
        _save_cache()
        self.root.destroy()

    def _drag_start(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _drag_move(self, event):
        self._win_x = event.x_root - self._drag_x
        self._win_y = event.y_root - self._drag_y
        self.root.geometry(f"+{self._win_x}+{self._win_y}")

    # ------------------------------------------------------------------ カード描画
    def _render_emails(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.canvas.yview_moveto(0)
        tk.Frame(self.list_frame, bg=C["bg"], height=10).pack(fill="x")

        if not self.emails:
            tk.Label(self.list_frame, text="メールが見つかりませんでした",
                      font=("Yu Gothic UI", 12), bg=C["bg"],
                      fg=C["text_muted"], pady=60).pack()
            return

        ordered = sorted(self.emails,
                          key=lambda x: (
                              0 if x["is_customer"] is True else
                              2 if x["is_customer"] is False else 1,
                              -x["received"].timestamp()
                          ))
        for email in ordered:
            self._render_card(email)

        tk.Frame(self.list_frame, bg=C["bg"], height=10).pack(fill="x")

        def _bind_wheel(widget):
            widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
            for child in widget.winfo_children():
                _bind_wheel(child)
        self.root.after(50, lambda: _bind_wheel(self.list_frame))

    def _render_card(self, email: dict):
        is_cust   = email["is_customer"]
        pending   = is_cust is None
        unread    = email.get("unread", False)

        if pending:
            card_bg    = C["card_ai"]
            border_col = C["border_ai"]
            sender_fg  = "#886600"
        elif is_cust:
            card_bg    = C["card_cust"]
            border_col = C["border_cust"]
            sender_fg  = "#0070A0"
        else:
            card_bg    = C["card_other"]
            border_col = C["border_other"]
            sender_fg  = "#222222"

        wrapper = tk.Frame(self.list_frame, bg=C["bg"])
        wrapper.pack(fill="x", padx=12, pady=(0, 10))

        R = 16
        cv = tk.Canvas(wrapper, bg=C["bg"], highlightthickness=0, bd=0)
        cv.pack(fill="x")
        inner = tk.Frame(cv, bg=card_bg)
        inner_win = cv.create_window(R, R, anchor="nw", window=inner)

        body = tk.Frame(inner, bg=card_bg)
        body.pack(side="left", fill="x", expand=True, padx=12, pady=8)

        row1 = tk.Frame(body, bg=card_bg)
        row1.pack(fill="x")

        if pending:
            badge_ibg, badge_ifg, badge_txt = C["badge_ai_bg"], C["badge_ai_fg"], "AI判定中…"
        elif is_cust:
            badge_ibg, badge_ifg, badge_txt = C["badge_cust_bg"], C["badge_cust_fg"], "お客様"
        else:
            badge_ibg, badge_ifg, badge_txt = C["badge_oth_bg"], C["badge_oth_fg"], "その他"

        badge_frame = tk.Frame(row1, bg=badge_ibg, padx=6, pady=2)
        badge_frame.pack(side="left", padx=(0, 10))
        tk.Label(badge_frame, text=badge_txt,
                  font=("Yu Gothic UI", 9, "bold") if is_cust else ("Yu Gothic UI", 9),
                  bg=badge_ibg, fg=badge_ifg).pack(side="left")

        if unread:
            tk.Label(row1, text="●", font=("Yu Gothic UI", 10),
                      bg=card_bg, fg=C["unread_dot"]).pack(side="left", padx=(0, 5))

        tk.Label(row1, text=email["sender"],
                  font=("Yu Gothic UI", 13, "bold" if unread else "normal"),
                  bg=card_bg, fg=sender_fg).pack(side="left")
        tk.Label(row1, text=email["received"].strftime("%m/%d  %H:%M"),
                  font=("Yu Gothic UI", 10), bg=card_bg, fg="#555555").pack(side="right")

        row2 = tk.Frame(body, bg=card_bg)
        row2.pack(fill="x", pady=(3, 0))
        tk.Label(row2, text=email["sender_email"], font=("Yu Gothic UI", 9),
                  bg=card_bg, fg="#666666").pack(side="left")

        row3 = tk.Frame(body, bg=card_bg)
        row3.pack(fill="x", pady=(7, 0))
        tk.Label(row3, text=email["preview"], font=("Yu Gothic UI", 10),
                  bg=card_bg, fg="#111111", anchor="w", justify="left",
                  wraplength=620).pack(fill="x", anchor="w")

        entry_id = email.get("entry_id", "")
        store_id = email.get("store_id", "")
        btn_area = tk.Frame(inner, bg=card_bg)
        btn_area.pack(side="right", padx=10, pady=8)

        make_icon_btn(btn_area, "↗", "開く", C["btn_open_fg"],
                      C["btn_open_bg"], C["btn_open_hov"],
                      lambda eid=entry_id, sid=store_id: self._on_open(eid, sid)
                      ).pack(fill="x", pady=(0, 6))
        make_icon_btn(btn_area, "✕", "削除", C["btn_del_fg"],
                      C["btn_del_bg"], C["btn_del_hov"],
                      lambda eid=entry_id, sid=store_id, e=email: self._on_delete(eid, sid, e),
                      pady=8).pack(fill="x")

        def _redraw(cw=None, event=None):
            cv.delete("rr")
            if cw is None:
                cw = cv.winfo_width()
            if cw < 10:
                return
            ih = inner.winfo_reqheight()
            total_h = ih + R * 2
            cv.config(height=total_h)
            cv.itemconfig(inner_win, width=cw - R * 2)
            cv.coords(inner_win, R, R)
            _rounded_rect(cv, 0, 0, R + 6, total_h, R,
                          fill=border_col, outline="", tags="rr")
            _rounded_rect(cv, 5, 0, cw, total_h, R,
                          fill=card_bg, outline="", tags="rr")
            cv.tag_lower("rr")

        inner.bind("<Configure>",  lambda e: _redraw(cv.winfo_width()))
        cv.bind("<Configure>",     lambda e: _redraw(e.width))

    # ------------------------------------------------------------------ ボタン操作
    def _on_open(self, entry_id, store_id):
        if not entry_id:
            messagebox.showinfo("確認", "デモモードのためOutlookを開けません。")
            return
        threading.Thread(target=lambda: self._open_thread(entry_id, store_id),
                          daemon=True).start()

    def _open_thread(self, entry_id, store_id):
        err = outlook_open_email(entry_id, store_id)
        if err:
            self.root.after(0, lambda: messagebox.showerror("エラー", f"メールを開けませんでした:\n{err}"))

    def _on_delete(self, entry_id, store_id, email):
        sender = email.get("sender", "")
        if not messagebox.askyesno("削除の確認",
                                    f"このメールをゴミ箱に移動しますか？\n\n送信者: {sender}",
                                    icon="warning"):
            return
        if not entry_id:
            self.emails = [e for e in self.emails if e is not email]
            self._update_counts()
            self._render_emails()
            return
        threading.Thread(
            target=lambda: self._delete_thread(entry_id, store_id, email),
            daemon=True).start()

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
        cust  = sum(1 for e in self.emails if e["is_customer"] is True)
        self.lbl_total.config(text=str(total))
        self.lbl_cust.config(text=str(cust))

    # ------------------------------------------------------------------ 更新ロジック
    def _refresh(self):
        self.lbl_updated.config(text="更新中…")
        threading.Thread(target=self._fetch_thread, daemon=True).start()

    def _fetch_thread(self):
        emails = fetch_emails(self.api_key)
        self.root.after(0, lambda: self._apply_update(emails))

    def _apply_update(self, emails):
        # キャッシュ済みのメールは即座に復元（API再呼び出しなし）
        for email in emails:
            key = _cache_key(email)
            if key in _ai_cache:
                email["is_customer"] = _ai_cache[key]

        self.emails = emails
        self._update_counts()
        self._render_emails()

        now_str = datetime.datetime.now().strftime("%H:%M 更新")
        self.lbl_updated.config(text=now_str)
        next_time = (datetime.datetime.now() + datetime.timedelta(milliseconds=REFRESH_INTERVAL_MS)).strftime("%H:%M")
        self.lbl_next.config(text=f"次回自動更新: {next_time}")

        pending = sum(1 for e in emails if e["is_customer"] is None)
        if pending > 0:
            self.lbl_ai_status.config(text=f"🤖 AI判定中… {pending}件")
            classify_emails_async(emails, self.api_key, self._on_email_classified)
        else:
            self.lbl_ai_status.config(text=f"🤖 AI判定完了（{_cache_size_info()}）")

        if self._refresh_job:
            self.root.after_cancel(self._refresh_job)
        self._refresh_job = self.root.after(REFRESH_INTERVAL_MS, self._refresh)

    def _on_email_classified(self, email):
        """1通判定完了 → UI更新"""
        def _update():
            pending = sum(1 for e in self.emails if e["is_customer"] is None)
            if pending == 0:
                self.lbl_ai_status.config(text="🤖 AI判定完了")
                cust = sum(1 for e in self.emails if e["is_customer"] is True)
                if self.prev_customer_count >= 0 and cust > self.prev_customer_count:
                    self._show_badge()
                self.prev_customer_count = cust
            else:
                self.lbl_ai_status.config(text=f"🤖 AI判定中… {pending}件")
            self._update_counts()
            self._render_emails()
        self.root.after(0, _update)

    def _show_badge(self):
        self.lbl_new.pack(side="left", padx=8)
        self.root.after(15000, lambda: self.lbl_new.pack_forget())

    def _manual_refresh(self):
        if self._refresh_job:
            self.root.after_cancel(self._refresh_job)
        self._refresh()

    def _clear_all(self):
        if not messagebox.askyesno("全クリア確認",
                                    "AIキャッシュとメール一覧をすべて消去します。\n次回更新時に全件再判定されます。\n\nよろしいですか？",
                                    icon="warning"):
            return
        # メモリとファイル両方クリア
        _ai_cache.clear()
        try:
            import os
            if os.path.exists(CACHE_PATH):
                os.remove(CACHE_PATH)
        except Exception:
            pass
        self.emails = []
        self.prev_customer_count = -1
        self._update_counts()
        self._render_emails()
        self.lbl_ai_status.config(text="🤖 キャッシュ消去済み")
        self._manual_refresh()


def main():
    if not HAS_WIN32:
        print("注意: pywin32 が見つかりません。ダミーデータで起動します。")
    if not HAS_ANTHROPIC:
        print("注意: anthropic が見つかりません。pip install anthropic を実行してください。")

    root = tk.Tk()
    app = OutlookCheckerAI(root)
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    h = root.winfo_reqheight()
    x = sw - COMPACT_W - 24
    y = sh - h - 60
    app._win_x = x
    app._win_y = y
    app._compact_h = h
    root.geometry(f"{COMPACT_W}x{h}+{x}+{y}")
    root.mainloop()


if __name__ == "__main__":
    main()
