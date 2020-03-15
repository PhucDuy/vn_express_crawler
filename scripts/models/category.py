from app import db
from datetime import datetime
from scripts.models.product import products_categories

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey(
        'category.id'), nullable=True)
    is_leaf_cat = db.Column(db.Boolean, nullable=False, default=False)
    is_scraped = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return "ID: {}, Name: {}, URL: {}, Parent_id: {}".format(self.id, self.name, self.url, self.parent_id)