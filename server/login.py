# -*- encoding: utf-8 -*-

"""An application server for CBGM.  User management module.  """

import urllib

import flask
from flask_user import UserMixin
import flask_login

from ntg_common import db as dbx


bp = flask.Blueprint ('login', __name__)


def init_app (app):
    """ Initialize the flask app. """

    app.config['USER_AFTER_LOGIN_ENDPOINT'] = 'login.welcome'


@bp.route ('/user/welcome')
def welcome ():
    """Endpoint.  Serve welcome page."""

    return flask.render_template ('welcome.html')


def make_safe_url (url):
    """Turns an unsafe absolute URL into a safe relative URL
    by removing the scheme and the hostname

    Example: make_safe_url('http://hostname/path1/path2?q1=v1&q2=v2#fragment')
             returns: '/path1/path2?q1=v1&q2=v2#fragment

    Copied from flask_user/views.py because it was defective.
    """

    parts = urllib.parse.urlsplit (url)
    return urllib.parse.urlunsplit ( ('', '', parts[2], parts[3], parts[4]) )


def declare_user_model_on (db): # db = flask_sqlalchemy.SQLAlchemy ()
    """ Declare the user model on flask_sqlalchemy. """

    # global User, Role, Roles_Users
    # pylint: disable=protected-access

    class User (db.Model, dbx._User, UserMixin):
        __tablename__ = 'user'

        roles = db.relationship (
            'Role',
            secondary = 'roles_users',
            backref = db.backref ('users', lazy='dynamic')
        )

    class Role (db.Model, dbx._Role):
        __tablename__ = 'role'

    class Roles_Users (db.Model, dbx._Roles_Users):
        __tablename__ = 'roles_users'

    return User, Role, Roles_Users


class AnonymousUserMixin (flask_login.AnonymousUserMixin):
    '''
    This is the default object for representing an anonymous user.
    '''

    def has_role (self, *_specified_role_names):
        return False
