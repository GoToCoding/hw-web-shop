import sys

import time

from src.auth import AppWrapper

if __name__ == "__main__":
    try:
        time.sleep(1)  # lag time
        appWrapper = AppWrapper()
        appWrapper.init_app()
        appWrapper.app.run(host="0.0.0.0", port=5010, debug=False)
    except Exception as e:
        print(e, file=sys.stderr)
        raise e
