from app_controller import AppController
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.resolve()))

if __name__ == "__main__":
    app = AppController()
    app.run()

