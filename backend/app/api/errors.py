from fastapi import HTTPException, status


def bad_request(message: str, error: str = "bad_request", details=None) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": error, "message": message, "details": details},
    )


