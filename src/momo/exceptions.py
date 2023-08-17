import json

class APICallError(Exception):
    def __init__(self, error_code, message ):
        self.error_code = error_code

        try:
            self.message = json.loads(message).get("message") or None

        except json.JSONDecodeError:
            self.message = message
            
        super().__init__(f"{ self.error_code } Error - { self.message }")

