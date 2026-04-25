from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import socket

class InternetCheckMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour vérifier la connexion Internet
    L'application ne fonctionne QUE si Internet est disponible
    """
    
    async def dispatch(self, request: Request, call_next):
        # Exclure les endpoints de santé
        if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Vérifier la connexion Internet
        if not self.check_internet():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Pas de connexion Internet",
                    "message": "Cette application nécessite une connexion Internet active pour fonctionner.",
                    "code": "NO_INTERNET_CONNECTION"
                }
            )
        
        response = await call_next(request)
        return response
    
    def check_internet(self, host="8.8.8.8", port=53, timeout=3):
        """
        Vérifie la connexion Internet en tentant de se connecter à Google DNS
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            return False
