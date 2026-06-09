import customtkinter as ctk
from database.db_example import init_db
from ui.theme import apply_theme, LAVENDER


def main():
    init_db()
    apply_theme()

    app = ctk.CTk()
    app.title("Wera")
    app.geometry("1100x720")
    app.configure(fg_color=LAVENDER)
    app.resizable(False, False)

    def clear():
        for w in app.winfo_children():
            w.destroy()

    def show_login():
        from ui.login_screen import LoginScreen
        clear()
        LoginScreen(
            app,
            on_login=show_home,
            on_register=show_register
        ).pack(fill="both", expand=True)

    def show_register():
        from ui.register_screen import RegisterScreen
        clear()
        RegisterScreen(
            app,
            on_success=after_register,
            on_back=show_login
        ).pack(fill="both", expand=True)

    def after_register(user):
        # Go straight to home after successful registration
        show_home(user)

    def show_home(user):
        from ui.home_screen import HomeScreen
        clear()
        HomeScreen(
            app,
            user=user,
            on_logout=do_logout
        ).pack(fill="both", expand=True)

    def do_logout():
        from logic.auth import logout
        from database.db_example import close_session
        logout()
        close_session()   # ← add this
        show_login()

    show_login()
    app.mainloop()


if __name__ == "__main__":
    main()