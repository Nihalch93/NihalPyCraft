import os
import datetime
from fyers_api import accessToken
import easygui

def get_access_token(client_id,secret_key,redirect_uri,response_type,grant_type):
    try:
        if not os.path.exists(f"MyCode/access_token/access_token_{datetime.datetime.now().isoformat()[0:10]}.txt"):
            session=accessToken.SessionModel(
            client_id=client_id,
            secret_key=secret_key,
            redirect_uri=redirect_uri, 
            response_type=response_type,
            grant_type=grant_type
            )   
            response = session.generate_authcode()
            print("Login uri: ", response)
            auth_code = easygui.enterbox("Enter Auth Code url: ").split("auth_code=")[1].split("&state=None")[0]
            session.set_token(auth_code)
            token_dict = session.generate_token()
            access_token= token_dict["access_token"]
            #refresh_token= token_dict["refresh_token"]
            with open(f"MyCode/access_token/access_token_{datetime.datetime.now().isoformat()[0:10]}.txt", "w") as f:
                f.write(access_token)
        else:
            with open(f"MyCode/access_token/access_token_{datetime.datetime.now().isoformat()[0:10]}.txt", "r") as f:
                access_token = f.read()
        return access_token
    except Exception as e:
        print(f"ERROR: exception while creating access token:: {e} ")