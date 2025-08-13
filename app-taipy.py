from taipy.gui import Gui
from state import *
from pages.login_page import page as page_login
from pages.quiz_page import page_quiz
from pages.result_page import page_result
from utils.auth import do_login

pages = {
    "home": page_login,
    "quiz": page_quiz,
    "result": page_result,
}

stylekit = {
    "font_family": "Rubik, Inter, system-ui, Arial, sans-serif",
    "border_radius": 12,
    "input_button_height": "44px",
}

if __name__ == "__main__":
    gui = Gui(pages=pages)
    gui.run(
        title="Bootcamp Post-Test",
        port=8600,
        dark_mode=True,
        stylekit=stylekit,
    )
