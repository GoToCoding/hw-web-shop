class Product:
    def __init__(self, id, name, category, is_deleted=False):
        self.id = id
        self.name = name
        self.category = category
        self.is_deleted = is_deleted

    def to_dict(self):
        res = {
            'name': self.name,
            'id': self.id,
            'category': self.category,
        }
        if self.is_deleted:
            res['is_deleted'] = True
        return res
