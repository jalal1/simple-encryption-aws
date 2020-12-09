# Simple Encryption on AWS

Files encryption using OpenSSL with python-tkinter and AWS.

![alt text](/imgs/sys-diagram.PNG)

![alt text](/imgs/login.PNG)

Demo Video: https://youtu.be/O79PDFAx3iA

### Installation

- Clone the repo.

- Create a virtual enviroment: "python -m venv env" ( for python 3 and above, virtualenv will be installed) (https://docs.python.org/3/tutorial/venv.html), then activate the enviroment.

- Install requirements.txt using: pip install -r requirements.txt

### Preparing AWS

- Get aws credentials and update credentials file.

- S3: Create 2 buckets: input bucket and output bucket. One to save the new uploaded files and the other used by ec2 to save the encrypted files.

- SQS: Create aws simple queue service. Copy queue name and use it in server.py

- Lambda: Create a new function to be triggered each time a new file is uploaded to S3 input bucket. Copy the code from lambda_function.py.

- EC2: 
    - Create a new virtual machine and ssh from local computer. Follow instructions on aws portal to use the private key.

    - install OpenSSL. Check for more details: https://www.openssl.org

    - Update server.py with queue name. Then copy server.py to the ec2 machine.

    - To run the code on ec2: python server.py

- Cognito: create new pool and specify needed attributes and details from aws portal. Copy pool id and client id to cognito.py

## Run

- Python App.py

## Built With

* [Python](https://www.python.org/)
* [tkinter](https://docs.python.org/3/library/tkinter.html)
* [OpenSSL](https://www.openssl.org)
* [AWS](https://aws.amazon.com/)

## Author

* **Jalal Khalil (jalalk@uab.edu)**

