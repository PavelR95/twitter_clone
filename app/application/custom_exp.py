class CustomException(Exception):

    def __init__(self, status_code: int, error_type: str, error_message: str):
        self.status_code = status_code
        self.error_type = error_type
        self.error_message = error_message
