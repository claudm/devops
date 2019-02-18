from datetime import datetime as dt

from flask import request
from flask_restful import Resource

from model import db, Step, StepSchema
from resources.export import StepExport
from resources.excel import StepExcel

check_steps_schema = StepSchema(many=True)
step_schema = StepSchema()


class StepResource(Resource):

    def elapsed_interval(self, start, end):
        # import ipdb
        # ipdb.set_trace()
        start_dt = dt.strptime(start[:-6], '%Y-%m-%dT%H:%M:%S.%f')
        end_dt = end
        elapsed = end_dt - start_dt

        min, secs = divmod(elapsed.days * 86400 + elapsed.seconds, 60)
        hour, minutes = divmod(min, 60)
        return '%.2d:%.2d:%.2d' % (hour, minutes, secs)

    def get(self):
        format = request.args.get('format')


        if format == 'excel':
            excel = StepExcel()
            return excel.get()
        if format == 'export':
            excel = StepExport()
            return excel.get()
        check_steps = Step.query.all()
        check_steps = check_steps_schema.dump(check_steps).data
        return {'status': 'success', 'data': check_steps}, 200

    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        # Validate and deserialize input
        data, errors = step_schema.load(json_data)
        if errors:
            return errors, 422
        step = Step.query.filter_by(Uuid=data['Uuid']).first()

        if step:
            return {'message': 'Uuid already exists'}, 400
        step = Step(
            Start_time=dt.now(),
            Uuid=json_data['Uuid'],
            Componente=json_data['Componente'],
            Versao=json_data['Versao'],
            Responsavel=json_data['Responsavel'],
            Status=json_data['Status']

        )

        db.session.add(step)
        db.session.commit()

        result = step_schema.dump(step).data

        return {"status": 'success', 'data': result}, 201

    def put(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        # Validate and deserialize input
        data, errors = step_schema.load(json_data)
        if errors:
            return errors, 422
        step = Step.query.filter_by(Uuid=data['Uuid']).first()
        if not step:
            return {'message': 'Step does not exist'}, 400
        # import ipdb
        # ipdb.set_trace()
        start_time = step_schema.dump(step).data.get("Start_time")
        end_time = dt.now()
        total_elapsed = self.elapsed_interval(start_time, end_time)
        step.End_time = end_time
        step.Status = data['Status']
        step.Versao = data['Versao']
        step.Total_time = total_elapsed
        db.session.commit()
        result = step_schema.dump(step).data

        return {"status": 'success', 'data': result}, 204

    def delete(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        # Validate and deserialize input
        data, errors = step_schema.load(json_data)
        if errors:
            return errors, 422
        step = Step.query.filter_by(id=data['id']).delete()
        db.session.commit()

        result = step_schema.dump(step).data

        return {"status": 'success', 'data': result}, 204
