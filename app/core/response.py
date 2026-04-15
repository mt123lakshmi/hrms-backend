from fastapi import HTTPException


def success_response(data=None, message="Success"):
    return {
        "success": True,
        "error": False,
        "message": message,
        "data": data
    }


def error_response(message="Error", status_code=400):
    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error": True,
            "message": message,
            "data": None
        }
    )