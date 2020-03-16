from app import db
from datetime import datetime
from scripts.models.product import products_categories
from flask_admin.contrib.sqla import ModelView

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

class CategoryView(ModelView):
    can_delete = False  # disable model deletion
    page_size = 50  # the number of entries to display on the list view
    can_view_details = True
    column_exclude_list = ['is_leaf_cat', 'is_scraped']
    column_searchable_list = ['name', 'url']
    column_filters = ['name']
    can_export = True





