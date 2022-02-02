import json
import os
from core.logs import debug_log, console_log
import logging
from datetime import datetime
from core.hivemind import HiveStore

BASE_DIR = ("python-plugins", "storage")

class HiveStorage(object):
    lib = HiveStore
    # plugin_name=self.plugin_name
    # storage_name=self.storage_name

    def __init__(self, uuid, plugin_name, storage_name):
        self.uuid = uuid
        self.plugin_name = plugin_name
        self.storage_name = storage_name
        self.set_data({})

    def set_data(self, data):
        self.data = data

    def save(self):
        #debug_log.debug("saving {}".format(str(self.uuid)))
        #debug_log.debug(self.data)
        payload = {
            "data": self.data,
            "uuid": self.uuid,
            "plugin_name": self.plugin_name,
            "storage_name": self.storage_name
        }
        HiveStore(data=payload).send()

__CODEX = {}
class IndexStorage(object):
    def __init__(self, plugin_name, storage_name, storage_module=HiveStorage):
        # TODO: Way for storage objects to maitain their storage locations
        #       but also patch existing objects, such as "mage", so plugins can add
        #       data to those objects
        hash_name = "{}.{}".format(plugin_name, storage_name)
        if __CODEX.get(hash_name):
            self.__dict__ = __CODEX.get(hash_name).__dict__
        else:
            __CODEX[hash_name] = self
            self.plugin_name = plugin_name
            self.storage_name = storage_name
            self.storage_module = storage_module
            self.files = {}
            self.touch_time = datetime.now()

    def reload(self, data):
        print(data)

        """ 
        for file_name in os.listdir(self.path):
            file_path = os.path.join(self.path, file_name)
            if file_name.endswith(".json") and os.path.isfile(file_path):
                self.files[file_name[0:-5]] = self.storage_module(
                    file_name[0:-5], file_path, self.plugin_name, self.storage_name
                )
        """
    def get(self, key):
        """
        if self.files.get(key) is None:
            file_path = os.path.join(self.path, "{}.json".format(key))
            if os.path.isfile(file_path):
                self.files[key] = self.storage_module(key, file_path)
        """
        return self.files.get(key)

    def get_by(self, attr, key):
        ret_val = []
        for ds in self.files.values():
            if ds.data.get(attr) == key:
                ret_val.append(ds)
        return ret_val

    def add(self, key, data=None):
        if data is None:
            data = {}
        #file_path = os.path.join(self.path, key)
        self.files[key] = self.storage_module(key, self.plugin_name, self.storage_name)
        self.files[key].set_data(data)
        self.files[key].save()
        return self.files[key]

    def remove(self, key):
        if self.files.get(key):
            del self.files[key]
            print("SEND MESSAGE TO HUVE TO DELETE THIS")
            #file_path = os.path.join(self.path, "{}.json".format(key))
            #new_file_path = os.path.join(self.path, "{}.removed".format(key))
            #os.rename(file_path, new_file_path)
        else:
            print("WHY THE FUCK IS THIS SAYING UNKNOWN TOWN")
            raise ValueError("Unknown Town: {}".format(key))

    def get_or_create(self, key):
        if self.files.get(key) is None:
            self.files[key] = self.storage_module(key, self.plugin_name, self.storage_name)
            #self.files[key].save()
        return self.files[key]

    def save_all(self):
        for file, storage in self.files.iteritems():
            console_log.info(file)
            storage.save()

    def __iter__(self):
        for k, v in self.files.iteritems():
            yield k, v
