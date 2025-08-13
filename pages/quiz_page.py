# pages/quiz_page.py
from state import nav_items, page, on_nav, quiz_body, init_quiz

page_quiz = """
<|navbar|lov={nav_items}|value={page}|on_change=on_nav|>

<|part|on_init=init_quiz|
## 📝 Post Test Bootcamp

{quiz_body}
|>
"""
