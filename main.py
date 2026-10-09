import flet as ft
import sqlite3

# --- ۱. مدیریت دیتابیس لوکال ---
def init_db():
    conn = sqlite3.connect("my_agent.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, time_str TEXT)")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('auto_reply', '0')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('status_context', 'در حال حاضر در کلاس دانشگاه هستم.')")
    conn.commit()
    conn.close()

def set_setting(key, value):
    conn = sqlite3.connect("my_agent.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def get_setting(key):
    conn = sqlite3.connect("my_agent.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def add_reminder(title, time_str):
    conn = sqlite3.connect("my_agent.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (title, time_str) VALUES (?, ?)", (title, time_str))
    conn.commit()
    conn.close()

def get_reminders():
    conn = sqlite3.connect("my_agent.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, time_str FROM reminders")
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- ۲. رابط کاربری (UI) ---
def main(page: ft.Page):
    init_db()
    page.title = "دستیار شخصی من"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15

    # ----- زبانه ۱: چت با ایجنت -----
    chat_messages = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    message_input = ft.TextField(hint_text="پیامت رو بنویس...", expand=True, border_radius=15)

    def send_message_click(e):
        if not message_input.value.strip():
            return
        user_text = message_input.value
        chat_messages.controls.append(
            ft.Row([ft.Container(content=ft.Text(user_text, color=ft.colors.WHITE), bgcolor=ft.colors.BLUE_700, padding=10, border_radius=10)], alignment=ft.MainAxisAlignment.END)
        )
        message_input.value = ""
        page.update()

        ai_response = f"دستور شما دریافت شد: {user_text}"
        chat_messages.controls.append(
            ft.Row([ft.Container(content=ft.Text(ai_response, color=ft.colors.WHITE), bgcolor=ft.colors.GREY_800, padding=10, border_radius=10)], alignment=ft.MainAxisAlignment.START)
        )
        page.update()

    chat_tab = ft.Column([
        ft.Text("🤖 گفتگو با ایجنت", size=20, weight=ft.FontWeight.BOLD),
        ft.Container(content=chat_messages, expand=True, border=ft.border.all(1, ft.colors.GREY_700), border_radius=10, padding=10),
        ft.Row([message_input, ft.IconButton(icon=ft.icons.SEND_ROUNDED, icon_color=ft.colors.BLUE_400, on_click=send_message_click)])
    ], expand=True)

    # ----- زبانه ۲: یادآوری قرص و کارها -----
    reminders_list = ft.ListView(expand=True, spacing=10)

    def load_reminders():
        reminders_list.controls.clear()
        for title, time_str in get_reminders():
            reminders_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.ALARM, color=ft.colors.AMBER),
                    title=ft.Text(title),
                    subtitle=ft.Text(f"ساعت: {time_str}"),
                    bgcolor=ft.colors.GREY_900,
                    border_radius=10
                )
            )
        page.update()

    task_name = ft.TextField(label="عنوان (مثلا: قرص / پروژه شبکه)", expand=True)
    task_time = ft.TextField(label="زمان (20:00)", width=110)

    def add_reminder_click(e):
        if task_name.value and task_time.value:
            add_reminder(task_name.value, task_time.value)
            task_name.value = ""
            task_time.value = ""
            load_reminders()

    reminder_tab = ft.Column([
        ft.Text("⏰ یادآوری‌ها و قرص‌ها", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([task_name, task_time]),
        ft.ElevatedButton("ثبت یادآوری جدید", icon=ft.icons.ADD, on_click=add_reminder_click),
        ft.Divider(),
        reminders_list
    ], expand=True)

    # ----- زبانه ۳: پاسخ خودکار به اس‌ام‌اس -----
    status_input = ft.TextField(
        label="وضعیت فعلی شما (مبنای پاسخ به SMSها)",
        value=get_setting('status_context'),
        multiline=True
    )

    def switch_changed(e):
        set_setting('auto_reply', "1" if e.control.value else "0")
        page.update()

    def save_status_click(e):
        set_setting('status_context', status_input.value)
        page.snack_bar = ft.SnackBar(ft.Text("وضعیت جدید ذخیره شد."))
        page.snack_bar.open = True
        page.update()

    auto_reply_tab = ft.Column([
        ft.Text("📱 پاسخ خودکار پیامک‌ها", size=20, weight=ft.FontWeight.BOLD),
        ft.Container(
            content=ft.Column([
                ft.Switch(label="فعال‌سازی پاسخ‌دهی خودکار", value=get_setting('auto_reply') == '1', on_change=switch_changed),
                ft.Divider(),
                status_input,
                ft.ElevatedButton("ذخیره وضعیت", icon=ft.icons.SAVE, on_click=save_status_click)
            ]),
            bgcolor=ft.colors.GREY_900,
            padding=15,
            border_radius=10
        )
    ], expand=True)

    load_reminders()

    # ساخت تب‌های اصلی
    page.add(ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="چت", icon=ft.icons.CHAT, content=chat_tab),
            ft.Tab(text="یادآوری", icon=ft.icons.ALARM, content=reminder_tab),
            ft.Tab(text="پاسخ SMS", icon=ft.icons.AUTO_MODE, content=auto_reply_tab),
        ],
        expand=True
    ))

# نقطه ورود برنامه
ft.app(target=main)