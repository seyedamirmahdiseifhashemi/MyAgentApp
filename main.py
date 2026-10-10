import flet as ft

def main(page: ft.Page):
    page.title = "Student Assistant"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # کامپوننت‌های رابط کاربری
    txt_output = ft.Text(value="سلام! دستیار دانشجویی شما آماده است.", size=18)
    
    def button_clicked(e):
        txt_output.value = "دکمه کلیک شد و برنامه به درستی کار می‌کند!"
        page.update()

    btn = ft.ElevatedButton(text="تست کلیک", on_click=button_clicked)

    page.add(
        ft.Column(
            [
                txt_output,
                btn
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    ft.app(main)