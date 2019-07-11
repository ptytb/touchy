from autoclass import autoclass
from functools import partial
from dill import load, dump


@autoclass
class TableRow:
    def __init__(self, key_binding, value_bindings: list):
        super().__init__()


class Model:
    def __init__(self, *rows: TableRow):
        super().__init__()
        self._storage = dict()
        
        for row in rows:

            def on_value_binding_changed(row, value, *, binding):
                is_key_static = isinstance(row.key_binding, tuple)
                if not is_key_static:
                    if not row.key_binding.is_valid:
                        return
                key = row.key_binding.model_key if not is_key_static else row.key_binding
                self._storage[key] = [value_binding.to_tuple() for value_binding in row.value_bindings]
                
            def on_key_binding_changed(row, value, *, binding):
                self.update_binding_from_table_row(row)
                
            if not isinstance(row.key_binding, tuple):
                row.key_binding.listen('*', partial(on_key_binding_changed, row))
            
            for binding in row.value_bindings:
                binding.listen('*', partial(on_value_binding_changed, row))

    def save(self):
        try:
            with open('settings.pickle', 'wb') as f:
                dump(self._storage, f)
        except Exception as e:
            print(e)
            
    def load(self):
        try:
            with open('settings.pickle', 'rb') as f:
                self._storage = load(f)
        except Exception as e:
            print(e)

    def __getitem__(self, item):
        return self._storage.get(item, None)
    
    def update_binding_from_table_row(self, row):
        is_key_static = isinstance(row.key_binding, tuple)
        key = row.key_binding.model_key if not is_key_static else row.key_binding
        values = self._storage.get(key, None)
        for i, binding in enumerate(row.value_bindings):
            row_value = values[i] if values else None
            binding.from_tuple(row_value if row_value else binding.defaults)

    def update_row(self, row, binding_old_value: tuple, binding_new_value: tuple):
        is_key_static = isinstance(row.key_binding, tuple)
        key = row.key_binding.model_key if not is_key_static else row.key_binding
        values = self._storage.get(key, None)
        i = values.index(binding_old_value)
        row.value_bindings[i].from_tuple(binding_new_value)
