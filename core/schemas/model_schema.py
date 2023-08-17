from core.database.models import User, Trains

from marshmallow import post_dump, Schema

class UserSchema(Schema):

    class Meta:
        model = User
        ordered = True
        load_instance = True
        fields = ("id", "username", "email", "name", "role", "password", "is_active", "profile", "date_created")

    @post_dump
    def change_none_values(cls, data, **kwargs):
        fields = cls.Meta.model.__dict__.get('__table__').columns
        
        field_map = {
            "VARCHAR": "",
            "INTEGER": 0,
            "FLOAT": 0.0,
            "JSON": {},
            "BOOLEAN": False,
            "DATETIME": ""
        }

        field_type = {}

        for field in fields:
            type_ = str(field.type).split("(")
            field_type.update({field.name: type_[0]})

        for key, value in data.items():

            try:
                if not value:
                    data[key] = field_map[field_type[key]]
            except KeyError:
                pass
        return data


class TrainSchema(Schema):

    class Meta:
        model = Trains
        ordered = True
        load_instance = True
        fields = ("train_id", "train_number", "train_name", "source", "destination", "price", "seats_available", "time")

    @post_dump
    def change_none_values(cls, data, **kwargs):
        fields = cls.Meta.model.__dict__.get('__table__').columns
        
        field_map = {
            "VARCHAR": "",
            "INTEGER": 0,
            "FLOAT": 0.0,
            "JSON": {},
            "BOOLEAN": False,
            "DATETIME": ""
        }

        field_type = {}

        for field in fields:
            type_ = str(field.type).split("(")
            field_type.update({field.name: type_[0]})

        for key, value in data.items():

            try:
                if not value:
                    data[key] = field_map[field_type[key]]
            except KeyError:
                pass
        return data

user_schema     = UserSchema()
users_schema    = UserSchema(many=True)

train_schema     = TrainSchema()
trains_schema    = TrainSchema(many=True)