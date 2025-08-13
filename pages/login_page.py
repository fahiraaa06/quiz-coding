# pages/login_page.py
from state import POST_START, POST_END

login_window_text = f"{POST_START.strftime('%d %b %Y %H:%M')} - {POST_END.strftime('%d %b %Y %H:%M')} WIB"
login_email = ""
login_password = ""

page = r"""
<style>
  /* === Font (Rubik) === */
  @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;700;800&display=swap');

  :root{
    --brand-navy:#023047; --brand-orange:#FF5400;
    --bg:#0d1520; --bg-accent:#101c2a; --text:#e6edf3; --muted:#a9b1c3;
    --card:rgba(255,255,255,0.08); --card-border:rgba(255,255,255,0.14);
    --radius:12px; --ring:rgba(255,84,0,.35); --shadow:0 18px 40px rgba(0,0,0,.35);
  }
  body{ font-family:'Rubik', system-ui, -apple-system, Segoe UI, Arial, sans-serif;
        background:
          radial-gradient(60rem 60rem at 20% -10%, rgba(2,48,71,.18), transparent 60%),
          radial-gradient(40rem 40rem at 110% 10%, rgba(255,84,0,.12), transparent 60%),
          linear-gradient(180deg, var(--bg) 0%, var(--bg-accent) 100%);
        color:var(--text);
  }
  .login-wrapper{min-height:100vh;display:grid;place-items:center;padding:56px 18px;}
  .login-card{width:100%;max-width:480px;background:var(--card);border:1px solid var(--card-border);
              border-radius:16px;box-shadow:var(--shadow);backdrop-filter:blur(10px);padding:28px 26px;}
  .login-title{
    display:block; text-align:center;
    font-size:1.75rem; font-weight:800; letter-spacing:.2px;
    margin:0 0 12px 0;
  }
  .login-subtitle{display:block;color:var(--muted);font-size:1rem;line-height:1.5;margin:0 0 18px 0;}
  .badge{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:12px;
         background:rgba(255,255,255,0.06);border:1px dashed var(--card-border);margin:2px 0 18px 0;}
  .badge-label{color:var(--muted);font-weight:600;}
  .badge-value{color:#fff;font-weight:700;}
  /* Fields & Inputs */
  .field{width:100%;margin-bottom:14px;}
  .login-card input{height:48px;border-radius:var(--radius);}
  /* Button */
  .btn{display:inline-flex;align-items:center;justify-content:center;width:100%;height:50px;
       border-radius:16px;border:1px solid transparent;background:var(--brand-orange);
       color:#fff;font-weight:800;letter-spacing:.5px;cursor:pointer;user-select:none;}
  .btn:hover{filter:brightness(1.04);}
  .btn:focus{outline:0;box-shadow:0 0 0 4px var(--ring);}
</style>

<|part|class_name=login-wrapper|
<|part|class_name=login-card|

<|🎓 Bootcamp Post-Test|text|class_name=login-title|>

<|part|class_name=badge|
<|Jendela post-test:|text|class_name=badge-label|>
<|{login_window_text}|text|class_name=badge-value|>
|>

<|Masuk dengan email dan password Anda.|text|class_name=login-subtitle|>

<|{login_email}|input|label=Email|placeholder=email@domain.com|width=100%|class_name=field|>
<|{login_password}|input|type=password|label=Password|placeholder=********|width=100%|class_name=field|>

<|LOGIN|button|on_action=do_login|class_name=btn|>

|>
|>
"""