from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.auth.auth_handler import decode_access_token

class JWTBearer(HTTPBearer):
    def __init__(self, required_role: str = None, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.required_role = required_role

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            token = credentials.credentials
            payload = decode_access_token(token)
            if payload is None:
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            if self.required_role and payload.get("role") != self.required_role:
                raise HTTPException(status_code=403, detail="Access forbidden: insufficient role.")
            return payload
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
