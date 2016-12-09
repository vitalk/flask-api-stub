# A Flask API stub

This is a template project repository used for REST API creation. It contains
the minimal configuration files and folders you will need for quick start from
scratch.

Build on top of the:

- [Flask](http://flask.pocoo.org/)
- [sqlalchemy](http://www.sqlalchemy.org/)
- [sqlalchemy-utils](https://sqlalchemy-utils.readthedocs.io/en/latest/index.html)
- [marshmallow](http://marshmallow.readthedocs.io/en/latest/)
- [Flask-Apify](https://github.com/vitalk/flask-apify)


## Usage

```python
from flask_api_stub.model import Model
from flask_api_stub.schema import Schema
from flask_api_stub.resource import Resource, Collection

from myapp.extensions import db, ma, api


class Album(db.Model, Model):
    name = db.Column(db.Text)
    description = db.Column(db.Text)


class AlbumSchema(Schema):
    class Meta:
        model = Album
    name = ma.Str()
    description = ma.Str()


class AlbumResource(Resource):
    model = Album
    schema = AlbumSchema
    methods = ('get', 'put', 'delete')


class AlbumCollection(Collection):
    model = Album
    schema = AlbumSchema
    methods = ('get', 'post')


AlbumResource.register(api)
AlbumCollection.register(api)
```
