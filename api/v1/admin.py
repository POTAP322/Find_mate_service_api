from sqladmin import Admin, ModelView
from fastapi import FastAPI
from api.v1.models import User, Game, UserGame, PartnerRequest, UserLog
from api.v1.database import engine


def setup_admin(app: FastAPI):
    admin = Admin(app, engine)

    class UserAdmin(ModelView, model=User):
        column_list = [
            User.id,
            User.telegram_id,
            User.username,
            User.account_status,
            User.description,
            User.current_partner_requests
        ]
        form_columns = [
            User.telegram_id,
            User.username,
            User.account_status,
            User.description,
            User.current_partner_requests
        ]
        column_formatters = {
            User.account_status: lambda m, a: m.account_status.upper()
        }

    class GameAdmin(ModelView, model=Game):
        column_list = [Game.id, Game.name]
        form_columns = [Game.name]

    class UserGameAdmin(ModelView, model=UserGame):
        column_list = [
            UserGame.id,
            UserGame.user,
            UserGame.game
        ]
        form_columns = [
            UserGame.user,
            UserGame.game
        ]

        # Настройка отображения связей в выпадающем списке
        form_ajax_refs = {
            'user': {
                'fields': (User.username, User.telegram_id),
                'order_by': User.username,
            },
            'game': {
                'fields': (Game.name,),
                'order_by': Game.name,
            }
        }

    class PartnerRequestAdmin(ModelView, model=PartnerRequest):
        column_list = [
            PartnerRequest.id,
            PartnerRequest.user,
            PartnerRequest.game,
            PartnerRequest.required_players,
            PartnerRequest.description,
            PartnerRequest.created_at,
            PartnerRequest.lifetime,
            PartnerRequest.platform
        ]
        form_columns = [
            PartnerRequest.user,
            PartnerRequest.game,
            PartnerRequest.required_players,
            PartnerRequest.description,
            PartnerRequest.lifetime,
            PartnerRequest.platform
        ]

        form_ajax_refs = {
            'user': {
                'fields': (User.username, User.telegram_id),
                'order_by': User.username,
            },
            'game': {
                'fields': (Game.name,),
                'order_by': Game.name,
            }
        }

    class UserLogAdmin(ModelView, model=UserLog):
        column_list = [
            UserLog.id,
            UserLog.user,
            UserLog.log_text,
            UserLog.created_at,
            UserLog.log_type
        ]
        form_columns = [
            UserLog.user,
            UserLog.log_text,
            UserLog.log_type
        ]

        form_ajax_refs = {
            'user': {
                'fields': (User.username, User.telegram_id),
                'order_by': User.username,
            }
        }

    admin.add_view(UserAdmin)
    admin.add_view(GameAdmin)
    admin.add_view(UserGameAdmin)
    admin.add_view(PartnerRequestAdmin)
    admin.add_view(UserLogAdmin)