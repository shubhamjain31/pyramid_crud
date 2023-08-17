import jwt, time

def decodeJWT(token: str, algorithm: str, secret: str):
    try:
        decoded_token = jwt.decode(token, secret, algorithms=[algorithm])
        if decoded_token["expires"] is False:
            return decoded_token
        else:
            return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}