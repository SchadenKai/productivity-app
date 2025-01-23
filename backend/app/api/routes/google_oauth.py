from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

from app.core.config import settings
from app.api.deps import SessionDep
from app.models import UserCreate, UserPublic
from app import crud

router = APIRouter()

# Configure OAuth
config_data = {
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=settings.GOOGLE_REDIRECT_URI,
    client_kwargs={'scope': 'openid profile email'},
)

@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/login/google/callback")
async def login_google_callback(request: Request, session: SessionDep):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    userinfo = token.get('userinfo')
    if not userinfo:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")
    
    email = userinfo['email']
    name = userinfo.get('name', '')
    picture = userinfo.get('picture', '')
    
    # Check if user exists
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        # Create new user
        user_create = UserCreate(
            email=email,
            full_name=name,
            is_active=True,
            is_superuser=False,
            profile_picture=picture
        )
        user = crud.create_user(session=session, user_create=user_create)
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserPublic.from_orm(user)
    }