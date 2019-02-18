from flask import Flask
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

ma = Marshmallow()
db = SQLAlchemy()



class Step(db.Model):
    __tablename__ = 'check_step'
    id            = db.Column(db.Integer, primary_key=True,autoincrement=True)
    Uuid          = db.Column(db.String(40), unique=True, index=True, nullable=False)
    Componente    = db.Column(db.String(150), unique=False, nullable=False)
    Versao        = db.Column(db.String(150), unique=False, nullable=False)
    Responsavel   = db.Column(db.String(150), unique=False, nullable=False)
    Status        = db.Column(db.String(150), unique=False, nullable=False)
    Start_time    = db.Column(db.TIMESTAMP, nullable=False)
    End_time      = db.Column(db.TIMESTAMP, nullable=True)
    Total_time    = db.Column(db.String(40), unique=False, nullable=True)

    def __init__(self,Uuid,Start_time,Componente,Versao,Responsavel,Status):
        self.Uuid           = Uuid
        self.Start_time     = Start_time
        self.Componente     = Componente
        self.Versao         = Versao
        self.Responsavel    = Responsavel
        self.Status         = Status
      


class StepSchema(ma.Schema):
    id           = fields.Integer()
    Uuid         = fields.String(required=False)
    Total_time   = fields.String(required=False)
    Start_time   = fields.DateTime(required=False)
    End_time     = fields.DateTime(required=False)
    Componente   = fields.String(required=False)
    Versao       = fields.String(required=False)
    Responsavel  = fields.String(required=False)
    Status       = fields.String(required=False)
