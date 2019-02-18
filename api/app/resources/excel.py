
from flask import request
from flask_restful import Resource
from model import db, Step, StepSchema
from flask import Flask
app = Flask(__name__)
import flask_excel as excel
excel.init_excel(app)

class StepExcel(Resource):

    
     def get(self):
        query_sets = Step.query.all()
        column_names = ['id', 'Componente','Start_time','End_time','Total_time','Versao','Responsavel','Status']
        return excel.make_response_from_query_sets(query_sets, column_names,"handsontable.html",sheet_name='guia bolso')
