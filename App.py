from tkinter import *
from tkinter import filedialog
import boto3
import time
import cognito
import os
import configparser

config = configparser.RawConfigParser()
config.read("credentials")
user_access_key_id = config.get("default", "aws_access_key_id")
user_secret_access_key = config.get("default", "aws_secret_access_key")
aws_session_token = config.get("default", "aws_session_token")


### GLOBAL VARIABLES ###
get_encrypted_file_retries = 10  # abort after 5 retries (5 seconds)
cost_per_KB = 0.001  # 1 MB = 1 cent, 1 GB
bucket_name = "input-files-bucket"
output_bucket_name = "output-files-bucket1"
########################

# initiate main window
root = Tk()
root.title("Encrypt")

# initiate parameters
user_name_var = StringVar()
email_var = StringVar()
confirm_code_var = StringVar()
password_var = StringVar()

# username = ""
password = ""
s3_client = ""
state = {"login": NORMAL, "browser": DISABLED}


def init_services():
    # global s3
    global s3_client
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=user_access_key_id,
            aws_secret_access_key=user_secret_access_key,
            aws_session_token=aws_session_token,
        )
    except Exception as e:
        print(e)


def register():
    # show frame for registartion
    registration_widget = Toplevel()
    registration_widget.title("Registration")
    registration_frame = LabelFrame(registration_widget, text="Registration:")

    email_label = Label(
        registration_frame,
        text="Email: ",
        fg="#052b69",
        anchor=E,
        relief=SUNKEN,
        bd=1,
        padx=50,
    )

    user_name_label = Label(
        registration_frame,
        text="User Name: ",
        fg="#052b69",
        anchor=E,
        relief=SUNKEN,
        bd=1,
        padx=50,
    )
    password_label = Label(
        registration_frame,
        text="Password: ",
        fg="#052b69",
        anchor=E,
        relief=SUNKEN,
        bd=1,
        padx=50,
    )
    email_entry = Entry(registration_frame, textvariable=email_var)
    user_name_entry = Entry(registration_frame, textvariable=user_name_var)
    password_entry = Entry(registration_frame, textvariable=password_var, show="*")

    registration_frame.grid(row=0, column=0)
    user_name_label.grid(row=1, column=0, sticky=W + E)
    user_name_entry.grid(row=1, column=1)
    password_label.grid(row=2, column=0, sticky=W + E)
    password_entry.grid(row=2, column=1)
    email_label.grid(row=3, column=0, sticky=W + E)
    email_entry.grid(row=3, column=1)

    register_button = Button(
        registration_frame,
        text="Register!",
        command=lambda: cognito.register(
            user_name_entry.get(),
            password_entry.get(),
            email_entry.get(),
            registration_frame,
        ),
        fg="#052b69",
        borderwidth="2",
        state=state["login"],
    )

    register_button.grid(row=4, column=0, columnspan=2)

    confrim_code_label = Label(
        registration_frame,
        text="Code: ",
        fg="#052b69",
        anchor=E,
        relief=SUNKEN,
        bd=1,
        padx=50,
    )
    confirm_code_entry = Entry(registration_frame, textvariable=confirm_code_var)
    confrim_code_label.grid(row=6, column=0, sticky=W + E)
    confirm_code_entry.grid(row=6, column=1)

    confirm_button = Button(
        registration_frame,
        text="Confirm",
        command=lambda: cognito.confirm(
            user_name_entry.get(), confirm_code_entry.get(), registration_frame
        ),
        fg="#052b69",
        borderwidth="2",
        state=state["login"],
    )

    confirm_button.grid(row=7, column=0, columnspan=2)


def login():
    global user_name
    global password
    global s3_client
    global state

    user_name = user_name_entry.get()
    password = password_entry.get()

    if len(user_name) == 0 or len(password) == 0:
        login_button.flash()
        login_button["text"] = "Empty details!"
    elif cognito.authenticate(user_name, password):
        init_services()
        browse_button["state"] = NORMAL
        login_frame.grid_remove()
        browse_button.grid(row=0, column=0, columnspan=2)
    else:
        login_button.flash()
        login_button["text"] = "Login failed!, try again!"


def get_cost(file_size):
    """
    calculate cost in $
    """
    file_size = file_size / 1000  # byte to KB
    return round((file_size * cost_per_KB) / 100, 3)


def get_encrypted_file(aws_bucket_name, aws_file_name, frame):
    local_file = filedialog.asksaveasfile(initialfile=aws_file_name)
    if local_file is None:
        print("no selected file!")

    is_found = False
    global get_encrypted_file_retries
    while not is_found and get_encrypted_file_retries > 0:
        file_size = download_file(aws_bucket_name, aws_file_name, local_file)
        print(file_size)
        if file_size > 0:  # file downloaded successfully
            print("Done!")
            is_found = True
            Label(frame, text="Encrypted file saved successfully!").grid(
                row=6, column=0, columnspan=2
            )
            # calculate billing cost
            # get file size,then multiply by cost_per_KB
            cost_text = "Total cost: " + str(get_cost(file_size)) + " $ "
            Label(frame, text=cost_text).grid(row=7, column=0, columnspan=2)

        else:
            time.sleep(2)
            get_encrypted_file_retries -= 1
            print("Retry: ", get_encrypted_file_retries)


def download_file(aws_bucket_name, aws_file_name, local_file):
    file_size = 0
    try:
        with open(local_file.name, "wb") as f:
            s3_client.download_fileobj(aws_bucket_name, aws_file_name, f)
            file_size = os.fstat(f.fileno()).st_size
        print("Downloaded Successfully!")
        return file_size

    except Exception as e:
        print(e)
        print("Downloaded Failed!")
        return 0


def upload_file(aws_bucket_name, frame):
    Label(frame, text="Rename uploading file (with extension): ").grid(
        row=3, column=0, sticky=W
    )

    # not on the screen yet, will be shown depend on the status. Check upload method below.
    succeed_response = Label(frame, text="Uploaded Successfully!")
    failed_response = Label(frame, text="Uploading failed!")

    root.filename = filedialog.askopenfilename(
        initialdir="~/Pictures",
        title="Select a file to upload",
        filetypes=(
            ("all files", "*.*"),
            ("image files", ("*.jpg", "*.jpeg", "*.png")),
            ("document files", ("*.doc", "*.docs", "*.odt", "*.pdf", "*.txt")),
        ),
    )

    # keep this label here, because root.filename should be called first
    Label(
        frame,
        text="Selected file: " + root.filename.split("/")[-1],
        fg="#b82c06",
    ).grid(row=2, column=0, sticky=W)

    Button(
        frame,
        text="Upload selected file",
        command=lambda: upload(root.filename, aws_bucket_name),
    ).grid(row=4, column=0, columnspan=2)

    selected_name_file = Entry(frame)
    selected_name_file.grid(row=3, column=1)
    # to upload, using boto3 instance
    def upload(original_file_path, bucket_name):
        # get either original file name or renamed file name
        file_name = (
            selected_name_file.get()
            if len(selected_name_file.get()) > 0
            else original_file_path.split("/")[-1]
        )
        print(file_name)
        try:
            s3_client.upload_file(original_file_path, bucket_name, file_name)
            succeed_response.grid(row=1, column=1)
            print("Uploaded Successfully!")
            Label(frame, text="Waiting encrypted file...").grid(
                row=5, column=0, columnspan=2
            )
            if "." in file_name:
                encrypted_file_name = (
                    file_name.split(".")[0] + "_enc" + "." + file_name.split(".")[1]
                )
            else:
                encrypted_file_name = file_name + "_enc"

            get_encrypted_file(output_bucket_name, encrypted_file_name, frame)

        except FileNotFoundError as e:
            print(e)
            failed_response.grid(row=1, column=1)
            print("failed to upload...")


app_menu = Menu(root)
root.config(menu=app_menu)

title = Label(
    root,
    text="Encryption Tool",
    font=("Arial", 16),
    justify=LEFT,
    padx=200,
    relief=SUNKEN,
    bd=1,
)

login_frame = LabelFrame(root, text="Login", pady=10)
user_name_label = Label(
    login_frame,
    text="User Name: ",
    fg="#052b69",
    anchor=E,
    relief=SUNKEN,
    bd=1,
    padx=50,
)
password_label = Label(
    login_frame, text="Password: ", fg="#052b69", anchor=E, relief=SUNKEN, bd=1, padx=50
)
user_name_entry = Entry(login_frame, textvariable=user_name_var)
password_entry = Entry(login_frame, textvariable=password_var, show="*")
login_button = Button(
    login_frame,
    text="Login!",
    padx=50,
    command=lambda: login(),
    fg="#052b69",
    borderwidth="2",
    state=state["login"],
)
register_button = Button(
    root,
    text="Register!",
    command=lambda: register(),
    fg="#052b69",
    borderwidth="2",
    state=state["login"],
)

browser_frame = LabelFrame(root, text="Browser...", pady=10)
browse_button = Button(
    browser_frame,
    text="Browse file!",
    command=lambda: upload_file(bucket_name, browser_frame),
    state=state["browser"],
    padx=100,
)

title.grid(row=0, column=0, columnspan=2)
login_frame.grid(row=1, column=0, columnspan=2)
user_name_label.grid(row=1, column=0, sticky=W + E)
user_name_entry.grid(row=1, column=1)
password_label.grid(row=2, column=0, sticky=W + E)
password_entry.grid(row=2, column=1)
login_button.grid(row=3, column=0, columnspan=2)
register_button.grid(row=0, column=2, sticky=E)
browser_frame.grid(row=3, column=0, columnspan=2)

root.mainloop()
