# app.py
import multiprocessing as mp
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-me-in-prod"  # sebaiknya ambil dari env

    # Register blueprints
    from routes import auth
    from routes.user import quiz, code, result
    from routes.admin import dashboard, questions, problems

    app.register_blueprint(auth.bp)
    app.register_blueprint(quiz.bp)
    app.register_blueprint(code.bp)
    app.register_blueprint(result.bp)

    app.register_blueprint(dashboard.bp)
    app.register_blueprint(questions.bp)
    app.register_blueprint(problems.bp)

    return app

if __name__ == "__main__":
    # penting di Windows untuk multiprocessing (coderunner)
    try:
        mp.set_start_method("spawn", force=False)
    except (RuntimeError, ValueError):
        pass
    app = create_app()
    app.run(debug=True)
