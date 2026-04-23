from fastapi import APIRouter, Depends


def create_core_router(get_current_user, get_user_profile):
    core_router = APIRouter()

    @core_router.get("/world")
    async def world():
        return {"message": "Hello, world!"}

    @core_router.get("/hello")
    async def hello(user: dict = Depends(get_current_user)):
        profile = get_user_profile(user)
        display_name = (
            profile.get("name")
            or profile.get("login")
            or profile.get("email")
            or profile.get("sub")
        )
        return {"message": f"Hello, {display_name}!"}

    @core_router.get("/me")
    async def me(user: dict = Depends(get_current_user)):
        # Return a provider profile shape for new providers while preserving GitHub compatibility.
        return get_user_profile(user)

    return core_router
