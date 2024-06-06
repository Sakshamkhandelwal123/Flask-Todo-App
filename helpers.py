import random

def generate_otp():
  otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])
  return otp
