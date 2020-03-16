from app import db
from flask_admin.contrib.sqla import ModelView

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), nullable=False)
    def __repr__(self):
        return f"{self.url}"


products_categories = db.Table('products_categories',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('cat_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(80), nullable=True) 
    seller_id = db.Column(db.String(80), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.String(80), nullable=False)
    image_urls = db.relationship('Photo', backref='product', lazy=True)
    url = db.Column(db.String(255), unique=True, nullable=False)
    cat_ids = db.relationship('Category', secondary=products_categories, 
                                lazy='subquery',backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f"{self.title}"

class PhotoView(ModelView):
    can_delete = False  # disable model deletion
    page_size = 50  # the number of entries to display on the list view
    can_view_details = True
    can_export = True
    column_searchable_list = ['url']

class ProductView(ModelView):
    can_delete = False  # disable model deletion
    page_size = 50  # the number of entries to display on the list view
    can_view_details = True
    column_exclude_list = ['seller_id', 'product_id']
    column_searchable_list = ['title','price', 'url']
    column_filters = ['title','price']
    can_export = True