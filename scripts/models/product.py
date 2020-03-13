class Store():
    def __init__(self, id, store_id, name, warranty_info):
        self.id = id
        self.store_id = store_id
        self.name = name
        self.warranty_info = warranty_info


class Product():
    def __init__(self, id, product_id, title, branch,
                 price, feature, rating, description, image_urls):
        self.id = id
        self.product_id = product_id
        self.title = title
        self.branch = branch
        self.price = price
        self.feature = feature
        self.rating = rating
        self.description = description
        self.image_urls = image_urls


