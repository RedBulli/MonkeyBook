from tests import BaseTestCase
from tests.factories import MonkeyFactory

from pytest import raises
from sqlalchemy.exc import IntegrityError

from MonkeyBook.models.monkey import Monkey
from MonkeyBook.extensions import db


class TestMonkeyColumnExistences(BaseTestCase):
    def setup_method(self, method):
        super(TestMonkeyColumnExistences, self).setup_method(method)
        monkey = MonkeyFactory()
        self.monkey = Monkey.query.get(monkey.id)

    def test_has_column_id(self):
        assert self.monkey.id

    def test_has_column_name(self):
        assert self.monkey.name

    def test_has_column_email(self):
        assert self.monkey.email


class TestMonkeyFriends(BaseTestCase):
    def setup_method(self, method):
        super(TestMonkeyFriends, self).setup_method(method)
        self.friend = MonkeyFactory(name='Ystava')
        monkey = MonkeyFactory()
        self.monkey = Monkey.query.get(monkey.id)

    def test_add_friend(self):
        assert len(self.monkey.friends) == 0
        self.monkey.friends.append(self.friend)
        db.session.commit()
        assert len(self.monkey.friends) == 1
        assert self.monkey.friends[0].name == 'Ystava'

    def test_add_same_friend_twice(self):
        self.monkey.friends.append(self.friend)
        self.monkey.friends.append(self.friend)
        with raises(IntegrityError):
            db.session.commit()


class TestMonkeyBestFriend(BaseTestCase):
    def setup_method(self, method):
        super(TestMonkeyBestFriend, self).setup_method(method)
        self.friend = MonkeyFactory(name='Paras ystava')
        self.monkey = MonkeyFactory()

    def add_as_best_friends_both_ways(self, monkey, friend):
        monkey.friends.append(friend)
        monkey.best_friend = friend
        friend.friends.append(monkey)
        friend.best_friend = monkey
        db.session.commit()

    def test_add_best_friend(self):
        self.monkey.friends.append(self.friend)
        db.session.commit()
        self.monkey.best_friend = self.friend
        print self.monkey.best_friend
        db.session.commit()
        print self.monkey.best_friend_id
        assert Monkey.query.get(self.monkey.id).best_friend == self.friend

    def test_remove_friendship(self):
        friend_id = self.friend.id
        self.monkey.friends.append(self.friend)
        db.session.commit()
        self.monkey.friends = []
        db.session.commit()
        assert Monkey.query.get(friend_id) == self.friend

    def test_delete_friend_with_best_friend(self):
        monkey_count = Monkey.query.count()
        self.add_as_best_friends_both_ways(self.monkey, self.friend)
        db.session.delete(self.monkey)
        db.session.commit()
        assert Monkey.query.count() == monkey_count - 1
