from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from nxtbn.users.utils.jwt_utils import verify_jwt_token
class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication without CSRF protection. 

    WARNING: Do not use this in production environments.
    This class is intended for development and API testing purposes where CSRF tokens might interfere 
    with various testing tools or workflows. In production, it's strongly advised to rely on JWT 
    authentication and avoid using session-based authentication altogether.

    This class overrides the enforce_csrf method to disable CSRF checks.
    """

    def enforce_csrf(self, request):
        """
        Disable CSRF checks for requests.
        """
        pass



class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            user = verify_jwt_token(token)
            if user:
                return (user, None)
            raise AuthenticationFailed("Invalid or expired token")
        return None
