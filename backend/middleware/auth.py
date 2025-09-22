"""Basic authentication middleware for admin routes"""
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os

security = HTTPBasic()

def verify_admin_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials for protected routes"""
    # Get credentials from environment variables
    correct_username = os.environ.get("ADMIN_USERNAME", "admin")
    correct_password = os.environ.get("ADMIN_PASSWORD", "changeme")
    
    # Use constant-time comparison to prevent timing attacks
    username_correct = secrets.compare_digest(
        credentials.username.encode("utf8"), 
        correct_username.encode("utf8")
    )
    password_correct = secrets.compare_digest(
        credentials.password.encode("utf8"), 
        correct_password.encode("utf8")
    )
    
    if not (username_correct and password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

def verify_department_credentials(department: str):
    """Create a dependency function for department-specific authentication"""
    def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
        """Verify department-specific credentials"""
        department_credentials = {
            "medical": {
                "username": os.environ.get("MEDICAL_USERNAME", "medical"),
                "password": os.environ.get("MEDICAL_PASSWORD", "medical123")
            },
            "dental": {
                "username": os.environ.get("DENTAL_USERNAME", "dental"),
                "password": os.environ.get("DENTAL_PASSWORD", "dental123")
            },
            "others": {
                "username": os.environ.get("OTHERS_USERNAME", "others"),
                "password": os.environ.get("OTHERS_PASSWORD", "others123")
            }
        }
        
        if department not in department_credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        correct_username = department_credentials[department]["username"]
        correct_password = department_credentials[department]["password"]
        
        username_correct = secrets.compare_digest(
            credentials.username.encode("utf8"),
            correct_username.encode("utf8")
        )
        password_correct = secrets.compare_digest(
            credentials.password.encode("utf8"),
            correct_password.encode("utf8")
        )
        
        if not (username_correct and password_correct):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        
        return credentials.username
    
    return verify_credentials

def verify_any_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify either admin or any department credentials for API access"""
    # First, try admin credentials
    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "changeme")
    
    admin_username_correct = secrets.compare_digest(
        credentials.username.encode("utf8"),
        admin_username.encode("utf8")
    )
    admin_password_correct = secrets.compare_digest(
        credentials.password.encode("utf8"),
        admin_password.encode("utf8")
    )
    
    if admin_username_correct and admin_password_correct:
        return credentials.username
    
    # Try department credentials
    department_credentials = {
        "medical": {
            "username": os.environ.get("MEDICAL_USERNAME", "medical"),
            "password": os.environ.get("MEDICAL_PASSWORD", "medical123")
        },
        "dental": {
            "username": os.environ.get("DENTAL_USERNAME", "dental"),
            "password": os.environ.get("DENTAL_PASSWORD", "dental123")
        },
        "others": {
            "username": os.environ.get("OTHERS_USERNAME", "others"),
            "password": os.environ.get("OTHERS_PASSWORD", "others123")
        }
    }
    
    for dept, creds in department_credentials.items():
        dept_username_correct = secrets.compare_digest(
            credentials.username.encode("utf8"),
            creds["username"].encode("utf8")
        )
        dept_password_correct = secrets.compare_digest(
            credentials.password.encode("utf8"),
            creds["password"].encode("utf8")
        )
        
        if dept_username_correct and dept_password_correct:
            return credentials.username
    
    # If no credentials match, raise unauthorized error
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
