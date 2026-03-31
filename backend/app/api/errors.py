from fastapi import HTTPException, status


def bad_request(message: str, error: str = "bad_request", details=None) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": error, "message": message, "details": details},
    )

def not_found(message: str, error: str = "not_found", details=None) -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": error, "message": message, "details": details},
    )


def unprocessable(message: str, error: str = "unprocessable_entity", details=None) -> None:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={"error": error, "message": message, "details": details},
    )
