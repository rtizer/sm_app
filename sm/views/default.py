from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import SQLAlchemyError

from .. import models


@view_config(route_name="home", renderer="sm:templates/users.jinja2")
def users(request):
    try:
        users = request.dbsession.query(models.User)
    except SQLAlchemyError:
        return Response(db_err_msg, content_type="text/plain", status=500)
    return {"users": users, "hierarchy": request.params.get("hierarchy")}


@view_config(route_name="documents", renderer="sm:templates/documents.jinja2")
def documents(request):
    try:
        query = request.dbsession.query(models.Document)
        documents = query.order_by(models.Document.date_changed.desc())
    except SQLAlchemyError:
        return Response(db_err_msg, content_type="text/plain", status=500)
    return {"documents": documents, "project": "SM"}


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to initialize your database tables with `alembic`.
    Check your README.txt for descriptions and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
