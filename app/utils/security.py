from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
import bcrypt
import os

# Environment variables or hardcoded values for your JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET", "secret")  # You should store the secret in environment variables
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Default expiration of 1 day

# OAuth2PasswordBearer is used to extract the token from the request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Hashing a password
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Verifying the hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# Creating a JWT access token
def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})  # Set the expiration time of the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to get the current user's username from the JWT token
def get_current_user_username(token: str = Depends(oauth2_scheme)) -> str:
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=403, detail="Could not validate credentials")
        
        # Here we use the email to identify the user, or you can store the username in the token
        return email  # You can replace `email` with `username` if stored in the token
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
