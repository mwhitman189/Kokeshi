# KoKeMama
KoKeMama is an e-commerce site for Kokeshi dolls with a Python back-end which allows artisans to select an order to fullfil.
## Installation
1. In a Python Virtual Environment:
`git clone https://github.com/mwhitman189/Kokeshi.git`
1. `pip install -r requirements.txt`

## Usage
KoKeMama requires the following environment variables:


- 'SECURITY_PASSWORD_SALT'

    Email server:
- 'MAIL_SERVER'
- 'MAIL_USERNAME'
- 'MAIL_PASSWORD'

You can set them in the terminal:

`export [ENV_VAR_NAME]=['env_var']`

To run a server locally:

`python3 run.py`
