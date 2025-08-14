# app.py
import multiprocessing as mp
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-me-in-prod"  # boleh ambil dari env

    # Register blueprints
    from routes.auth import bp as auth_bp
    from routes.quiz import bp as quiz_bp
    from routes.code import bp as code_bp
    from routes.result import bp as result_bp
    from routes.leaderboard import bp as leaderboard_bp
    from routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(code_bp)
    app.register_blueprint(result_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(admin_bp)

    return app

if __name__ == "__main__":
    # penting di Windows untuk multiprocessing (coderunner)
    try:
        mp.set_start_method("spawn", force=False)
    except Exception:
        pass
    app = create_app()
    app.run(debug=True)
