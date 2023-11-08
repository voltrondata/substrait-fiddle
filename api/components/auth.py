import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

############################################################
# Function to verify the passed token by decoding with key
############################################################
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, os.environ.get("SESSION_SECRET"),
                             algorithms=["HS256"])
        return payload
    except jwt.exceptions.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credential validation unsuccessful",
            headers={"WWW-Authenticate": "Bearer"},
        )
