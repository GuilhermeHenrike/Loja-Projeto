# Entidade Produto e seus atributos

class Product:
    def __init__(self, id, user_id, name, description, price, category_id, category_name, stock=0, image_url=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.price = price
        self.category_id = category_id
        self.category_name = category_name
        self.stock = stock
        self.image_url = image_url
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0.0,
            'category_id': self.category_id,
            'stock': int(self.stock) if self.stock else 0,
            'image_url': self.image_url,
            'category_name': self.category_name,
            'created_at': self.created_at
        }