from datetime import date, datetime, timedelta
from flask import abort, jsonify, g
from flask.views import MethodView
from flask_smorest import Blueprint
from middlewares import auth_required, developer_required
from sqlalchemy import Date, cast, asc, desc
from schemas.homestats import (
    HomeStatsSchema,
    HomeStatsCreateSchema,
    HomeStatsUpdateSchema,
    HomeStatsListSchema,
    HomeStatsUsingList,
    HomeStatsUsingFilters,
    HomeStatsUnckeckedList
)
from models.homestats import HomeStats
from models.expense import Expense
from models.incoming import Incoming
from models.using import Using

homestats = Blueprint('homestats', 'homestats', url_prefix='/homestats')


@homestats.route('/')
class HomeStatsList(MethodView):
    @homestats.response(200, HomeStatsListSchema)
    def get(self):
        homestats_list = HomeStats.query.filter_by(deleted=False).order_by(asc('place')).order_by(asc('position')).all()

        for homestat in homestats_list:
            if homestat.place == 2 and homestat.type == 'exp':
                query = Expense.query.filter_by(liquid_id=homestat.liquid.id, deleted=False)\
                    .filter(cast(Expense.date, Date) == date.today())\
                    .order_by(desc('date'))

                amounts = query.with_entities(Expense.amount)
                amount = 0

                for expenseAmount in amounts:
                    amount = amount + expenseAmount.amount

                homestat.expenses = {
                    'expenses': query.all(),
                    'count': query.count(),
                    'amount': amount,
                }
            elif homestat.place == 2 and homestat.type == 'inc':
                query = Incoming.query.filter_by(liquid_id=homestat.liquid.id, deleted=False)\
                    .filter(cast(Incoming.date, Date) == date.today())\
                    .order_by(desc('date'))

                amounts = query.with_entities(Incoming.amount)
                amount = 0

                for incomingAmount in amounts:
                    amount = amount + incomingAmount.amount

                homestat.incoming = {
                    'incoming': query.all(),
                    'count': query.count(),
                    'amount': amount,
                }
            if homestat.place == 3:
                query = Expense.query.filter_by(liquid_id=homestat.liquid.id, deleted=False)\
                    .filter(cast(Expense.date, Date) >= (date.today() - timedelta(days=6)))\
                    .order_by(desc('date'))
                

                average_amounts = query.with_entities(Expense.amount)
                average_amount = 0

                for expenseAmount in average_amounts:
                    average_amount = average_amount + expenseAmount.amount
                
                homestat.average_expense = average_amount / 7

        return {
            'homestats': homestats_list
        }

    @auth_required
    @developer_required
    @homestats.arguments(HomeStatsCreateSchema, location='json')
    @homestats.response(200, HomeStatsSchema(only=(
        'type',
        'type_display',
        'title',
        'place',
        'position',
        'liquid',
        'id',
        'user',
        'created_at'
    )))
    def post(self, data):
        data['stat_type'] = data['type']
        del data['type']

        homestat = HomeStats(user_id=g.user.id, **data)
        homestat.save()

        return homestat


@homestats.route('/unchecked')
class HomeStatsUnchecked(MethodView):
    @homestats.response(200, HomeStatsUnckeckedList())
    def get(self):
        expenses = Expense.query.filter_by(deleted=False).filter(Expense.verified != 2).order_by(desc('date'))
        incoming = Incoming.query.filter_by(deleted=False).filter(Incoming.verified != 2).order_by(desc('date'))

        return {
            'expenses': {
                'expenses': expenses.all(),
                'count': expenses.count()
            },
            'incoming': {
                'incoming': incoming.all(),
                'count': incoming.count()
            },
        }


@homestats.route('/<homestat_id>')
class HomeStatsById(MethodView):
    @homestats.response(200, HomeStatsSchema(only=(
        'type',
        'type_display',
        'title',
        'place',
        'position',
        'liquid',
        'id',
        'user',
        'created_at'
    )))
    def get(self, homestat_id):
        homestat = HomeStats.query.get_or_404(homestat_id)
        if homestat.deleted:
            return abort(404)

        return homestat

    @auth_required
    @developer_required
    @homestats.arguments(HomeStatsUpdateSchema, location='json')
    @homestats.response(200, HomeStatsSchema(only=(
        'type',
        'type_display',
        'title',
        'place',
        'position',
        'liquid',
        'id',
        'user',
        'created_at'
    )))
    def put(self, data, homestat_id):
        homestat = HomeStats.query.get_or_404(homestat_id)

        if 'position' in data:
            homestat_check = HomeStats.query.filter_by(deleted=False, place=homestat.place, position=data['position']).first()
            if homestat_check:
                return jsonify({
                    'errors': {
                        'code': 422,
                        'json': {
                            'position': 'Позиция занята'
                        },
                        'status': 'Unprocessable Entity'
                    }
                }), 422

        if 'place' in data:
            homestat_check = HomeStats.query.filter_by(deleted=False, place=data['place'], position=homestat.position).first()
            if homestat_check:
                return jsonify({
                    'errors': {
                        'code': 422,
                        'json': {
                            'position': 'Позиция занята'
                        },
                        'status': 'Unprocessable Entity'
                    }
                }), 422

        if homestat.deleted:
            return abort(404)

        for key, value in data.items():
            setattr(homestat, key, value)

        homestat.save()

        return homestat

    @auth_required
    @developer_required
    def delete(self, homestat_id):
        homestat = HomeStats.query.get_or_404(homestat_id)
        if homestat.deleted:
            return abort(404)

        homestat.deleted = True
        homestat.save()

        return jsonify({
            'message': 'success deleting'
        }), 200


@homestats.route('/using')
class HomeStatsUsing(MethodView):
    @homestats.arguments(HomeStatsUsingFilters, location='query')
    @homestats.response(200, HomeStatsUsingList)
    def get(self, arguments):
        query = Using.query

        if 'worker_id' in arguments:
            query = query.filter_by(worker_id=arguments['worker_id'])
        if 'vehicle_id' in arguments:
            query = query.filter_by(vehicle_id=arguments['vehicle_id'])
        
        query = query.order_by(
            desc('used')
        )

        return {
            'using': query.all()
        }
