from dotenv import load_dotenv
load_dotenv()

from backend.app import create_app
from backend.extensions import db

app = create_app()



if __name__ == "__main__":
    app.run(debug=True)