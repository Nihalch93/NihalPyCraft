from pushbullet import PushBullet
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *

from cryptography.fernet import Fernet

def notification(text):
    key = 'rY_KIjSijZEv2fNt367xBCEbpgxaoNr7KKNQm35CJ08='#easygui.enterbox("Enter encryption key")
    fernet = Fernet(key)
    pb = PushBullet(fernet.decrypt(b'gAAAAABkx2DS94XVf-PDAS3P4_M9RjxlQklDKSLR_VjXjmWznSfDptpfLXFQw98Cx0tDOa06t4PmFI-Cwx0DWez8j4rES_4F1DkuL2TNBxEkX0LpaOj5h4_EhwEXH-_3r_dIcgpEPoJf').decode())
    pb.push_note(text, text)


