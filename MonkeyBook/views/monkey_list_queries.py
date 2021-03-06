from flask import abort
from flask.ext.sqlalchemy import Pagination
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.sql import and_

from MonkeyBook.extensions import db
from MonkeyBook.models.monkey import Monkey, monkey_friends, best_friends


class MonkeyListQueries:
    def get_paginated_monkeys(self, order_by, direction, page, page_size):
        if (order_by == 'friends'):
            return self.get_paginated_monkeys_ordered_by_friends_count(
                direction, page, page_size)
        elif (order_by == 'best_friend'):
            query = self.get_monkeys_ordered_by_best_friend_name_query(
                direction)
        else:
            query = self.get_monkeys_ordered_by_name_query(direction)
        return query.paginate(page, page_size)

    def get_paginated_monkeys_ordered_by_friends_count(self, direction, page, 
                                                       page_size):
        query = self.get_monkeys_ordered_by_friends_count_query(direction)
        pagination = self.paginate(query, page, page_size)
        pagination.items = map(lambda item: item[0], pagination.items)
        return pagination

    def get_monkeys_ordered_by_friends_count_query(self, direction):
        return db.session.query(Monkey, 
                func.count(monkey_friends.c.monkey_id).label('friend_count')
            ).outerjoin(
                monkey_friends, monkey_friends.c.monkey_id == Monkey.id
            ).group_by(Monkey).order_by('friend_count ' + direction)

    def get_monkeys_ordered_by_best_friend_name_query(self, direction):
        best_friend_table = aliased(Monkey)
        query = Monkey.query \
            .outerjoin(
                best_friends, 
                best_friends.c.monkey_id == Monkey.id
            ).outerjoin(
                best_friend_table,
                best_friends.c.friend_id == best_friend_table.id
            ).order_by('monkey_1.name ' + direction + ' NULLS LAST')
        return query

    def get_monkeys_ordered_by_name_query(self, direction):
        return Monkey.query.order_by('name ' + direction)

    def paginate(self, query, page, per_page=20, error_out=True):
        if error_out and page < 1:
            abort(404)
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        if not items and page != 1 and error_out:
            abort(404)

        if page == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = query.order_by(None).count()

        return Pagination(query, page, per_page, total, items)