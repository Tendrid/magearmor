import json
import os
import logging

BASE_DIR = ("python-plugins", "storage")


class DataStorage(object):
    def __init__(self, uuid, path, data=None):
        self.uuid = uuid
        self.path = path
        if data:
            self.set_data(data)
        else:
            self.load()

    def set_data(self, data):
        self.data = data

    def clear_data(self):
        self.data = {}

    def load(self):
        self.clear_data()
        if not os.path.isfile(self.path):
            self.save()
        with open(self.path) as fh:
            self.set_data(json.load(fh))

    def save(self):
        with open(self.path, "w+") as fh:
            json.dump(self.data, fh)


class IndexStorage(object):
    codex = {}

    def __init__(self, plugin_name, storage_name, storage_module=DataStorage):
        # TODO: Way for storage objects to maitain their storage locations
        #       but also patch existing objects, such as "mage", so plugins can add
        #       data to those objects
        self.codex[storage_name] = self
        self.storage_module = storage_module
        self.path = os.path.abspath(
            os.path.join(*(BASE_DIR + (plugin_name, storage_name)))
        )
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        self.reload()

    def reload(self):
        self.files = {}
        for file_name in os.listdir(self.path):
            file_path = os.path.join(self.path, file_name)
            if file_name.endswith(".json") and os.path.isfile(file_path):
                self.files[file_name[0:-5]] = self.storage_module(
                    file_name[0:-5], file_path
                )

    def get(self, key):
        if self.files.get(key) is None:
            file_path = os.path.join(self.path, "{}.json".format(key))
            if os.path.isfile(file_path):
                self.files[key] = self.storage_module(key, file_path)
        return self.files.get(key)

    def add(self, key, data=None):
        if data is None:
            data = {}
        file_path = os.path.join(self.path, key)
        self.files[key] = self.storage_module(key, "{}.json".format(file_path), data)
        self.files[key].save()
        return self.files[key]

    def remove(self, key):
        if self.files.get(key):
            del self.files[key]
            file_path = os.path.join(self.path, "{}.json".format(key))
            new_file_path = os.path.join(self.path, "{}.removed".format(key))
            os.rename(file_path, new_file_path)
        else:
            raise ValueError("Unknown Town: {}".format(key))

    def get_or_create(self, key):
        if self.files.get(key) is None:
            file_path = os.path.join(self.path, "{}.json".format(key))
            self.files[key] = self.storage_module(key, file_path)
            self.files[key].save()
        return self.files[key]

    def __iter__(self):
        for k, v in self.files.iteritems():
            yield k, v
