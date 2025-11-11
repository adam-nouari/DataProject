# main.py — lance le dashboard
from src.pages.home import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)

