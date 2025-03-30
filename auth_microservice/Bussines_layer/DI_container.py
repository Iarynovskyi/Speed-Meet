from dependency_injector import containers, providers
from auth_microservice.Data_layer.session import SessionLocal
from auth_microservice.Data_layer.DALs import UserDAL, AccessTokensDAL, RefreshTokenDAL
from auth_microservice.Bussines_layer.user_auth_logic import UserAuthLogic

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["auth_microservice.API.auth_controller"],
    )

    db_session = providers.Factory(SessionLocal)
    user_dal = providers.Factory(UserDAL, session=db_session)
    access_tokens_dal = providers.Factory(AccessTokensDAL, db_session=db_session)
    refresh_dal = providers.Factory(RefreshTokenDAL, db_session=db_session)

    user_service = providers.Factory(
        UserAuthLogic,
        user_dal=user_dal,
        access_tokens_dal=access_tokens_dal,
        refresh_dal=refresh_dal,
    )