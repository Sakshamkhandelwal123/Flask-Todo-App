class CustomException(Exception):
  def __init__(self, message, status_code=500):
      super().__init__(message, status_code)
      self.status_code = status_code
