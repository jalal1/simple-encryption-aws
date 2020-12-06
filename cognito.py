from logging import exception
from os import terminal_size
from tkinter import Label
from pycognito import Cognito

# Global variables
user_pool_id = "xxxxxxx" # get from aws cognito
client_id = "xxxxxxx" # get from aws cognito


def register(user_name, password, email, registration_frame):
    try:
        u = Cognito(user_pool_id, client_id)
        u.set_base_attributes(email=email)
        u.register(user_name, password)
        print("New user created successfully!")
        Label(registration_frame, text="New user created successfully!").grid(row=5, column=0, columnspan=2)
    except Exception as e:
        print(e)
        return False

def confirm(user_name, code, registration_frame):
    try:
        u = Cognito(user_pool_id, client_id)
        u.confirm_sign_up(code,username=user_name)
        print("Your Email was confirmed!")
        Label(registration_frame, text="Your Email was confirmed!").grid(row=8, column=0, columnspan=2)
    except Exception as e:
        print(e)
        return False

def authenticate(user_name, password):
    try:
        u = Cognito(user_pool_id, client_id, username= user_name)
        u.authenticate(password=password)
        print("Logged in successfully!")
        return True
    except Exception as e:
        print(e)
        return False



if __name__ == "__main__":
    pass
