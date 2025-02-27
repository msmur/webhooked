from fastapi import APIRouter


# Initialize router with a prefix
router = APIRouter(prefix="/healthchecks", tags=["Health Checks"])


# Route for creating a hook
@router.get(
    "/liveness",
    summary="Check the health of the application",
)
async def liveness() -> dict:
    """
    Endpoint to check the health of the application.
    """
    return {"status": "OK"}
