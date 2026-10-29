
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

APP = Path(__file__).resolve().parent
CSV_FILE = APP / "expenses.csv"
LOGO_FILE = APP / "assets" / "spendly_logo.png"
PROMO_FILE = APP / "assets" / "better_choices.png"

PURPLE = "#6D3DF5"
PURPLE_DARK = "#4D2DB6"
NAVY = "#0C1233"
BG = "#F6F8FF"
WHITE = "#FFFFFF"
TEXT = "#182A4D"
MUTED = "#7D8CAB"
BORDER = "#DDE4F1"
GREEN = "#16B889"
ORANGE = "#F4A623"
BLUE = "#2D98F3"
RED = "#F05B69"

CATEGORIES = ["Education", "Food", "Shopping", "Bills", "Health", "Travel", "Entertainment", "Other"]
PAYMENTS = ["UPI", "Card", "Cash", "Net Banking"]

class SpendlyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spendly - Personal Expense Tracker")
        self.geometry("1668x916")
        self.minsize(1200, 760)
        self.configure(bg=BG)

        self.df = self.load_data()
        self.logo_img = None
        self.promo_img = None
        self.chart_canvases = []

        self.build_styles()
        self.build_shell()
        self.navigate("Dashboard")

    def build_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Spendly.Treeview",
            background=WHITE,
            fieldbackground=WHITE,
            foreground=TEXT,
            rowheight=38,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Spendly.Treeview.Heading",
            background="#F3F6FC",
            foreground="#6C7B99",
            font=("Segoe UI Semibold", 9),
            relief="flat",
        )
        style.map(
            "Spendly.Treeview",
            background=[("selected", "#ECE5FF")],
            foreground=[("selected", TEXT)],
        )

    def load_data(self):
        if not CSV_FILE.exists():
            return pd.DataFrame(columns=["Date", "Category", "Description", "Amount", "Payment"])
        try:
            df = pd.read_csv(CSV_FILE)
        except Exception:
            return pd.DataFrame(columns=["Date", "Category", "Description", "Amount", "Payment"])
        needed = ["Date", "Category", "Description", "Amount", "Payment"]
        for c in needed:
            if c not in df.columns:
                df[c] = ""
        df = df[needed].copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
        df["Category"] = df["Category"].fillna("Other").astype(str)
        df["Description"] = df["Description"].fillna("").astype(str)
        df["Payment"] = df["Payment"].fillna("UPI").astype(str)
        return df.dropna(subset=["Date"]).reset_index(drop=True)

    def save_data(self):
        save_df = self.df.copy()
        save_df["Date"] = pd.to_datetime(save_df["Date"]).dt.strftime("%Y-%m-%d")
        save_df.to_csv(CSV_FILE, index=False)

    # ---------- shell ----------
    def build_shell(self):
        self.sidebar = tk.Frame(self, bg=NAVY, width=305)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=NAVY, height=118)
        brand.pack(fill="x")
        brand.pack_propagate(False)
        try:
            im = Image.open(LOGO_FILE).convert("RGB")
            im.thumbnail((255, 92), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(im)
            tk.Label(brand, image=self.logo_img, bg=NAVY, bd=0).pack(anchor="w", padx=20, pady=12)
        except Exception:
            tk.Label(brand, text="Spendly", bg=NAVY, fg="white",
                     font=("Segoe UI", 27, "bold")).pack(anchor="w", padx=24, pady=24)

        tk.Label(self.sidebar, text="MAIN", bg=NAVY, fg="#8E9ABC",
                 font=("Segoe UI Semibold", 10)).pack(anchor="w", padx=32, pady=(22, 8))

        self.nav_buttons = {}
        for name, icon in [
            ("Dashboard", "⌂"),
            ("Expenses", "▣"),
            ("Analytics", "▥"),
            ("History", "◷"),
        ]:
            self.add_nav(name, icon)

        tk.Frame(self.sidebar, bg="#2A3154", height=1).pack(fill="x", padx=24, pady=22)
        tk.Label(self.sidebar, text="MORE", bg=NAVY, fg="#8E9ABC",
                 font=("Segoe UI Semibold", 10)).pack(anchor="w", padx=32, pady=(0, 8))
        for name, icon in [
            ("Budgets", "◎"),
            ("Categories", "▦"),
            ("Settings", "⚙"),
            ("Help Center", "?"),
        ]:
            self.add_nav(name, icon)

        promo = tk.Frame(self.sidebar, bg=NAVY, height=188)
        promo.pack(side="bottom", fill="x", padx=19, pady=18)
        promo.pack_propagate(False)
        try:
            pm = Image.open(PROMO_FILE).convert("RGB")
            pm = pm.resize((275, 190), Image.LANCZOS)
            self.promo_img = ImageTk.PhotoImage(pm)
            tk.Label(promo, image=self.promo_img, bg=NAVY, bd=0).pack()
        except Exception:
            tk.Label(promo, text="Better\nChoices\nBrighter\nTomorrow",
                     bg="#201550", fg="white", font=("Segoe UI", 17, "bold"),
                     justify="left").pack(fill="both", expand=True)

        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

        self.topbar = tk.Frame(self.main, bg=BG, height=82)
        self.topbar.pack(fill="x", padx=28, pady=(20, 0))
        self.topbar.pack_propagate(False)

        search_frame = tk.Frame(self.topbar, bg=WHITE,
                                highlightbackground=BORDER, highlightthickness=1)
        search_frame.pack(side="left", fill="x", expand=True, ipady=10)
        tk.Label(search_frame, text="⌕", bg=WHITE, fg="#6A7EA6",
                 font=("Segoe UI", 18)).pack(side="left", padx=(15, 6))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     bg=WHITE, fg=MUTED, relief="flat",
                                     font=("Segoe UI", 11))
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.insert(0, "Search expenses, categories...")
        self.search_entry.bind("<FocusIn>", self.on_search_focus)
        self.search_entry.bind("<Return>", lambda _e: self.navigate("History"))
        tk.Label(search_frame, text="Ctrl  K", bg=WHITE, fg="#99A5BE",
                 font=("Segoe UI", 9)).pack(side="right", padx=12)

        tk.Button(
            self.topbar, text="+ Add Expense", command=self.add_expense_dialog,
            bg=PURPLE, fg="white", relief="flat", bd=0,
            font=("Segoe UI Semibold", 11), padx=20, pady=12
        ).pack(side="left", padx=(14, 0))

        for symbol, cmd in [("♧", self.show_notifications), ("⚙", lambda: self.navigate("Settings"))]:
            tk.Button(
                self.topbar, text=symbol, command=cmd,
                bg=WHITE, fg="#58698C", relief="flat", bd=0,
                font=("Segoe UI", 15), width=4, pady=8
            ).pack(side="left", padx=(9, 0))

        self.body = tk.Frame(self.main, bg=BG)
        self.body.pack(fill="both", expand=True, padx=28, pady=(4, 18))

    def on_search_focus(self, _event=None):
        if self.search_var.get() == "Search expenses, categories...":
            self.search_var.set("")
            self.search_entry.config(fg=TEXT)

    def add_nav(self, name, icon):
        btn = tk.Button(
            self.sidebar,
            text=f"  {icon}   {name}",
            anchor="w",
            bg=NAVY,
            fg="#D7DEF1",
            activebackground="#3D226E",
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            font=("Segoe UI", 11),
            padx=17,
            pady=11,
            command=lambda n=name: self.navigate(n),
            cursor="hand2",
        )
        btn.pack(fill="x", padx=15, pady=1)
        self.nav_buttons[name] = btn

    # ---------- navigation ----------
    def navigate(self, page):
        if page in ("Budgets", "Categories", "Settings", "Help Center"):
            self.current_page = page
        else:
            self.current_page = page

        for name, btn in self.nav_buttons.items():
            btn.config(
                bg="#40216F" if name == page else NAVY,
                fg="white" if name == page else "#D7DEF1"
            )

        for w in self.body.winfo_children():
            w.destroy()

        if page == "Dashboard":
            self.build_dashboard()
        elif page == "Expenses":
            self.build_expenses()
        elif page == "Analytics":
            self.build_analytics()
        elif page == "History":
            self.build_history()
        elif page == "Budgets":
            self.build_budgets()
        elif page == "Categories":
            self.build_categories()
        elif page == "Settings":
            self.build_settings()
        elif page == "Help Center":
            self.build_help()

    def title_row(self, title, subtitle):
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=(0, 14))
        tk.Label(row, text=title, bg=BG, fg=TEXT,
                 font=("Segoe UI", 26, "bold")).pack(side="left")
        tk.Label(row, text=subtitle, bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left", padx=15, pady=(8, 0))

    # ---------- dashboard ----------
    def stats(self):
        arr = self.df["Amount"].to_numpy(dtype=float) if not self.df.empty else np.array([0.0])
        total = float(np.sum(arr))
        avg = float(np.mean(arr)) if len(arr) else 0.0
        high = float(np.max(arr)) if len(arr) else 0.0
        return total, avg, high, len(self.df)

    def metric_card(self, parent, title, value, note, accent, icon):
        card = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=5)
        tk.Frame(card, bg=accent, width=5).pack(side="left", fill="y")
        inner = tk.Frame(card, bg=WHITE)
        inner.pack(fill="both", expand=True, padx=14, pady=12)

        tk.Label(inner, text=icon, bg="#F0EBFF", fg=PURPLE,
                 font=("Segoe UI Semibold", 15), width=3, pady=4).pack(side="left", anchor="n")
        info = tk.Frame(inner, bg=WHITE)
        info.pack(side="left", padx=11)
        tk.Label(info, text=title, bg=WHITE, fg="#7C8AA7",
                 font=("Segoe UI", 10)).pack(anchor="w")
        tk.Label(info, text=value, bg=WHITE, fg="#19294D",
                 font=("Segoe UI", 21, "bold")).pack(anchor="w", pady=(4, 0))
        tk.Label(info, text=note, bg=WHITE, fg="#8290AC",
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))

    def build_dashboard(self):
        self.title_row("Dashboard", "Your spending overview")
        total, avg, high, count = self.stats()

        stats = tk.Frame(self.body, bg=BG)
        stats.pack(fill="x", pady=(0, 14))
        self.metric_card(stats, "Total Spent", f"₹{total:,.2f}", "↓ 12%   vs. last month", PURPLE, "₹")
        self.metric_card(stats, "Average Expense", f"₹{avg:,.2f}", "↓ 8%   vs. last month", GREEN, "≈")
        self.metric_card(stats, "Highest Expense", f"₹{high:,.2f}", "↑ 5%   vs. last month", ORANGE, "★")
        self.metric_card(stats, "Expenses", str(count), "↑ 100%   vs. last month", BLUE, "≡")

        grid = tk.Frame(self.body, bg=BG)
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure(0, weight=3)
        grid.grid_columnconfigure(1, weight=2)
        grid.grid_rowconfigure(0, weight=1)
        grid.grid_rowconfigure(1, weight=1)

        self.chart_card(grid, "Spending Trend", 0, 0, self.draw_line)
        self.chart_card(grid, "Spending by Category", 0, 1, self.draw_donut)
        self.chart_card(grid, "Category-wise Spending", 1, 0, self.draw_bars)
        self.chart_card(grid, "Expense Amount Distribution", 1, 1, self.draw_hist)

        table = tk.Frame(self.body, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        table.pack(fill="x", pady=(12, 0))
        hdr = tk.Frame(table, bg=WHITE)
        hdr.pack(fill="x", padx=18, pady=(10, 4))
        tk.Label(hdr, text="▣  Recent Transactions", bg=WHITE, fg=TEXT,
                 font=("Segoe UI Semibold", 12)).pack(side="left")
        tk.Button(hdr, text="View All →", command=lambda: self.navigate("History"),
                  bg=WHITE, fg=PURPLE, relief="flat", bd=0,
                  font=("Segoe UI Semibold", 9)).pack(side="right")
        self.make_tree(table, self.df.sort_values("Date", ascending=False).head(3), 3)

    def chart_card(self, parent, title, row, col, renderer):
        f = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        f.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
        tk.Label(f, text=title, bg=WHITE, fg=TEXT,
                 font=("Segoe UI Semibold", 12)).pack(anchor="w", padx=18, pady=(12, 2))
        holder = tk.Frame(f, bg=WHITE)
        holder.pack(fill="both", expand=True, padx=8, pady=6)
        fig, ax = plt.subplots(figsize=(6.0, 2.5), dpi=90)
        fig.patch.set_facecolor("white")
        canvas = FigureCanvasTkAgg(fig, master=holder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.chart_canvases.append((fig, ax, canvas, renderer))
        renderer(ax, fig)
        canvas.draw()

    # ---------- chart renderers ----------
    def category_totals(self):
        if self.df.empty:
            return pd.Series(dtype=float)
        return self.df.groupby("Category")["Amount"].sum().sort_values(ascending=False)

    def style_ax(self, ax):
        ax.set_facecolor("white")
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(axis="y", alpha=0.15)
        ax.tick_params(axis="both", labelsize=8, colors="#6E7D9C")

    def draw_line(self, ax, fig):
        ax.clear()
        self.style_ax(ax)
        if self.df.empty:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
            return
        daily = self.df.groupby("Date")["Amount"].sum().sort_index()
        ax.plot(daily.index, daily.values, color="#6D3DF5", linewidth=2.8, marker="o", markersize=4)
        ax.fill_between(daily.index, daily.values, alpha=0.10, color="#6D3DF5")
        ax.set_ylabel("Amount (₹)", fontsize=8)
        fig.autofmt_xdate(rotation=20)
        ax.tick_params(axis="x", labelsize=7)
        ax.set_title("", pad=2)

    def draw_donut(self, ax, fig):
        ax.clear()
        cats = self.category_totals()
        if cats.empty:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            return
        colors = ["#6D3DF5", "#FFA91F", "#2196F3", "#16B889", "#F05B69", "#F2C744", "#A26CF2", "#5E78D6"]
        wedges, _ = ax.pie(
            cats.values,
            startangle=90,
            counterclock=False,
            colors=colors[:len(cats)],
            wedgeprops={"width": 0.38, "edgecolor": "white"},
        )
        total = float(cats.sum())
        ax.text(0, 0, f"₹{total:,.0f}\nTotal Spending", ha="center", va="center",
                fontsize=11, fontweight="bold", color=TEXT)
        ax.legend(
            wedges,
            [f"{k}   ₹{v:,.0f}   {v/total*100:.0f}%" for k, v in cats.items()],
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            frameon=False,
            fontsize=7,
        )
        ax.set_aspect("equal")

    def draw_bars(self, ax, fig):
        ax.clear()
        self.style_ax(ax)
        cats = self.category_totals()
        if cats.empty:
            return
        bars = ax.bar(cats.index, cats.values, color="#7448F4", width=0.64)
        ax.set_ylabel("Amount (₹)", fontsize=8)
        ax.tick_params(axis="x", rotation=15)
        ax.tick_params(axis="x", labelsize=7)
        for b, v in zip(bars, cats.values):
            ax.text(b.get_x() + b.get_width()/2, v + max(cats.values)*0.02,
                    f"₹{v:,.0f}", ha="center", va="bottom", fontsize=7, color=TEXT)

    def draw_hist(self, ax, fig):
        ax.clear()
        self.style_ax(ax)
        if self.df.empty:
            return
        values = self.df["Amount"].to_numpy(dtype=float)
        bins = min(8, max(4, len(values)//2))
        ax.hist(values, bins=bins, color="#8A62EE", edgecolor="white")
        ax.set_xlabel("Amount (₹)", fontsize=8)
        ax.set_ylabel("Frequency", fontsize=8)

    # ---------- expenses ----------
    def build_expenses(self):
        self.title_row("Expenses", "Add, filter, edit and manage your transactions")

        toolbar = tk.Frame(self.body, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        toolbar.pack(fill="x", pady=(0, 12))

        self.cat_filter = tk.StringVar(value="All")
        self.pay_filter = tk.StringVar(value="All")
        self.min_filter = tk.StringVar()

        tk.Label(toolbar, text="Category", bg=WHITE, fg=MUTED).pack(side="left", padx=(15, 4), pady=12)
        ttk.Combobox(toolbar, textvariable=self.cat_filter, values=["All"]+CATEGORIES,
                     state="readonly", width=16).pack(side="left", padx=4)

        tk.Label(toolbar, text="Payment", bg=WHITE, fg=MUTED).pack(side="left", padx=(12, 4))
        ttk.Combobox(toolbar, textvariable=self.pay_filter, values=["All"]+PAYMENTS,
                     state="readonly", width=16).pack(side="left", padx=4)

        tk.Label(toolbar, text="Min Amount", bg=WHITE, fg=MUTED).pack(side="left", padx=(12, 4))
        tk.Entry(toolbar, textvariable=self.min_filter, width=11).pack(side="left", padx=4, ipady=5)

        tk.Button(toolbar, text="Apply", command=self.refresh_expenses,
                  bg=PURPLE, fg="white", relief="flat", bd=0, padx=12, pady=7).pack(side="left", padx=4)
        tk.Button(toolbar, text="Reset", command=self.reset_filters,
                  bg="#F1F3F8", fg=TEXT, relief="flat", bd=0, padx=12, pady=7).pack(side="left", padx=4)
        tk.Button(toolbar, text="+ Add Expense", command=self.add_expense_dialog,
                  bg=GREEN, fg="white", relief="flat", bd=0, padx=14, pady=7).pack(side="right", padx=14)

        self.expense_host = tk.Frame(self.body, bg=WHITE)
        self.expense_host.pack(fill="both", expand=True)
        self.refresh_expenses()

    def refresh_expenses(self):
        for w in self.expense_host.winfo_children():
            w.destroy()

        df = self.df.copy()
        if self.cat_filter.get() != "All":
            df = df[df["Category"] == self.cat_filter.get()]
        if self.pay_filter.get() != "All":
            df = df[df["Payment"] == self.pay_filter.get()]
        if self.min_filter.get().strip():
            try:
                df = df[df["Amount"] >= float(self.min_filter.get())]
            except ValueError:
                messagebox.showerror("Spendly", "Minimum amount must be numeric.")
                return

        tree = self.make_tree(self.expense_host, df.sort_values("Date", ascending=False), 15)
        tree.bind("<Double-1>", self.edit_row)

        tk.Label(self.expense_host,
                 text="Double-click a transaction to edit it.",
                 bg="#F6F8FF", fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=7)

    def reset_filters(self):
        self.cat_filter.set("All")
        self.pay_filter.set("All")
        self.min_filter.set("")
        self.refresh_expenses()

    def make_tree(self, parent, data, height):
        frame = tk.Frame(parent, bg=WHITE)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        cols = ("Date", "Category", "Description", "Amount", "Payment Method")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=height,
                            style="Spendly.Treeview")
        widths = [130, 170, 340, 150, 180]
        for c, w in zip(cols, widths):
            tree.heading(c, text=c)
            tree.column(c, width=w, anchor="w")

        for _, r in data.iterrows():
            tree.insert("", "end", values=(
                pd.to_datetime(r["Date"]).strftime("%Y-%m-%d"),
                r["Category"],
                r["Description"],
                f"₹{float(r['Amount']):,.2f}",
                r["Payment"],
            ))

        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def add_expense_dialog(self):
        win = tk.Toplevel(self)
        win.title("Spendly - Add Expense")
        win.geometry("460x560")
        win.resizable(False, False)
        win.configure(bg=WHITE)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="Add Expense", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 21, "bold")).pack(anchor="w", padx=28, pady=(24, 2))
        tk.Label(win, text="Record a new transaction", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=28, pady=(0, 16))

        date_v = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        cat_v = tk.StringVar(value="Education")
        amount_v = tk.StringVar()
        desc_v = tk.StringVar()
        pay_v = tk.StringVar(value="UPI")

        def field(label, var, combo=None):
            tk.Label(win, text=label, bg=WHITE, fg="#6D7C9B",
                     font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=28, pady=(8, 3))
            if combo:
                ttk.Combobox(win, textvariable=var, values=combo,
                             state="readonly").pack(fill="x", padx=28)
            else:
                tk.Entry(win, textvariable=var, relief="solid", bd=1,
                         font=("Segoe UI", 10)).pack(fill="x", padx=28, ipady=6)

        field("Date (YYYY-MM-DD)", date_v)
        field("Category", cat_v, CATEGORIES)
        field("Amount (₹)", amount_v)
        field("Description", desc_v)
        field("Payment Method", pay_v, PAYMENTS)

        def save():
            try:
                date = pd.to_datetime(date_v.get(), format="%Y-%m-%d")
                amount = float(amount_v.get())
                if amount <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Spendly", "Enter a valid date and positive amount.")
                return

            new_row = pd.DataFrame([{
                "Date": date,
                "Category": cat_v.get() or "Other",
                "Description": desc_v.get() or "Expense",
                "Amount": amount,
                "Payment": pay_v.get() or "UPI",
            }])
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self.save_data()
            win.destroy()
            self.navigate(self.current_page)

        tk.Button(win, text="Save Expense", command=save, bg=PURPLE, fg="white",
                  relief="flat", bd=0, font=("Segoe UI Semibold", 11),
                  pady=10).pack(fill="x", padx=28, pady=22)

    def edit_row(self, event):
        tree = event.widget
        item = tree.selection()
        if not item:
            return
        values = tree.item(item[0], "values")
        if not values:
            return

        dtext, cat, desc, amount_text, payment = values
        amount = float(amount_text.replace("₹", "").replace(",", ""))

        mask = (
            (pd.to_datetime(self.df["Date"]).dt.strftime("%Y-%m-%d") == dtext)
            & (self.df["Category"] == cat)
            & (self.df["Description"] == desc)
            & (self.df["Payment"] == payment)
            & (self.df["Amount"].round(2) == round(amount, 2))
        )
        indices = self.df.index[mask].tolist()
        if not indices:
            return

        new_amount = tk.simpledialog.askfloat("Edit Expense", "New amount:", initialvalue=amount,
                                              parent=self)
        if new_amount is None:
            return
        self.df.loc[indices[0], "Amount"] = float(new_amount)
        self.save_data()
        self.navigate(self.current_page)

    # ---------- history ----------
    def build_history(self):
        self.title_row("History", "All saved transactions")
        panel = tk.Frame(self.body, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True)
        self.make_tree(panel, self.df.sort_values("Date", ascending=False), 18)

    # ---------- analytics ----------
    def build_analytics(self):
        self.title_row("Analytics", "Detailed spending insights")
        grid = tk.Frame(self.body, bg=BG)
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_rowconfigure(0, weight=1)
        grid.grid_rowconfigure(1, weight=1)
        self.chart_card(grid, "Spending Trend", 0, 0, self.draw_line)
        self.chart_card(grid, "Spending by Category", 0, 1, self.draw_donut)
        self.chart_card(grid, "Category-wise Spending", 1, 0, self.draw_bars)
        self.chart_card(grid, "Expense Amount Distribution", 1, 1, self.draw_hist)

    def build_budgets(self):
        self.title_row("Budgets", "Track your monthly spending target")
        panel = tk.Frame(self.body, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="x")
        tk.Label(panel, text="Monthly Budget (₹)", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(24, 4))
        budget_var = tk.StringVar(value="50000")
        tk.Entry(panel, textvariable=budget_var, width=20).pack(anchor="w", padx=24, ipady=6)
        result = tk.Label(panel, bg=WHITE, fg=TEXT, font=("Segoe UI", 12, "bold"))
        result.pack(anchor="w", padx=24, pady=18)

        def update():
            try:
                b = float(budget_var.get())
                spent = self.stats()[0]
                remaining = b - spent
                result.config(text=f"Spent: ₹{spent:,.2f}   |   Remaining: ₹{remaining:,.2f}")
            except ValueError:
                messagebox.showerror("Spendly", "Enter a valid budget.")

        tk.Button(panel, text="Calculate", command=update, bg=PURPLE, fg="white",
                  relief="flat", bd=0, padx=16, pady=8).pack(anchor="w", padx=24, pady=(0,24))

    def build_categories(self):
        self.title_row("Categories", "Your current expense categories")
        panel = tk.Frame(self.body, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True)
        data = self.category_totals()
        for i, (cat, amount) in enumerate(data.items()):
            tk.Label(panel, text=f"{cat:<18} ₹{amount:,.2f}",
                     bg=WHITE, fg=TEXT, font=("Consolas", 11)).pack(anchor="w", padx=30, pady=6)
            if i > 20:
                break

    def build_settings(self):
        self.title_row("Settings", "Local data and project tools")
        panel = tk.Frame(self.body, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="x")
        tk.Label(panel, text="Data Tools", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=24, pady=(24, 8))
        tk.Button(panel, text="Reload CSV", command=self.reload_csv,
                  bg="#F0EDFF", fg=PURPLE_DARK, relief="flat", bd=0, padx=18, pady=8).pack(anchor="w", padx=24, pady=6)
        tk.Button(panel, text="Export CSV", command=self.export_csv,
                  bg=PURPLE, fg="white", relief="flat", bd=0, padx=18, pady=8).pack(anchor="w", padx=24, pady=6)
        tk.Button(panel, text="Reset to Demo Data", command=self.reset_demo,
                  bg="#FFF1F2", fg=RED, relief="flat", bd=0, padx=18, pady=8).pack(anchor="w", padx=24, pady=(6,24))

    def build_help(self):
        self.title_row("Help Center", "Quick guide for your project demonstration")
        panel = tk.Frame(self.body, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True)
        text = (
            "Spendly Mini Project\n\n"
            "Dashboard: shows KPIs and four charts.\n"
            "Expenses: add, filter and edit transactions.\n"
            "Analytics: opens the visualization page.\n"
            "History: shows all saved records.\n"
            "Budgets: compare spending against a budget.\n"
            "Settings: reload, export or reset demo data.\n\n"
            "Technology mapping: Python + Tkinter + Pandas + NumPy + Matplotlib."
        )
        tk.Label(panel, text=text, bg=WHITE, fg=TEXT, justify="left",
                 font=("Segoe UI", 11), wraplength=800).pack(anchor="w", padx=30, pady=30)

    # ---------- utility ----------
    def show_notifications(self):
        messagebox.showinfo("Spendly", "No new notifications.")

    def reload_csv(self):
        self.df = self.load_data()
        self.navigate(self.current_page)

    def reset_demo(self):
        demo = pd.DataFrame([
            ["2026-09-19", "Education", "Course Fee", 1200.00, "UPI"],
            ["2026-09-21", "Education", "Course Material", 500.00, "UPI"],
            ["2026-09-23", "Education", "Workshop", 150.00, "Card"],
            ["2026-09-24", "Shopping", "Clothes", 700.00, "UPI"],
            ["2026-09-26", "Shopping", "Books", 500.00, "Card"],
            ["2026-09-27", "Food", "Lunch at Cafe", 500.00, "UPI"],
            ["2026-09-28", "Food", "Dinner", 300.00, "Cash"],
            ["2026-09-29", "Food", "Snacks", 200.00, "UPI"],
            ["2026-09-30", "Bills", "Internet Bill", 900.00, "Net Banking"],
            ["2026-10-01", "Health", "Medicine", 550.00, "Card"],
            ["2026-10-02", "Travel", "Bus Ticket", 500.00, "Card"],
            ["2026-10-03", "Entertainment", "Movie", 350.00, "UPI"],
        ], columns=["Date", "Category", "Description", "Amount", "Payment"])
        demo.to_csv(CSV_FILE, index=False)
        self.df = self.load_data()
        self.navigate("Dashboard")

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            title="Export Spendly CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="spendly_expenses.csv",
        )
        if path:
            temp = self.df.copy()
            temp["Date"] = pd.to_datetime(temp["Date"]).dt.strftime("%Y-%m-%d")
            temp.to_csv(path, index=False)
            messagebox.showinfo("Spendly", f"CSV exported to:\n{path}")

if __name__ == "__main__":
    SpendlyApp().mainloop()
