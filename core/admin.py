from core.storage import IndexStorage
from core.commands import console_command
from core.logs import console_log
import json


def deep_get(names, obj):
    if names:
        if type(obj) is dict:
            name = names.pop(0)
            return deep_get(names, obj.get(name))
        elif type(obj) is list:
            idx = names.pop(0)
            return deep_get(names, obj[int(idx)])
    else:
        return obj


@console_command("save-all")
def save_all(parameters):
    for name, storage in IndexStorage.codex.iteritems():
        console_log.info("saving {}".format(name))
        storage.save_all()


@console_command("list")
def list_plugin(parameters):
    cmd_len = len(parameters)

    if cmd_len == 0:
        print(IndexStorage.codex.keys())
    elif cmd_len == 1:
        store = IndexStorage.codex.get(parameters[0])
        print(store)
        if store:
            for name, storage in store:
                print(name, storage)
    elif cmd_len == 2:
        store = IndexStorage.codex.get(parameters[0])
        if store:
            item = store.get(parameters[1])
            if item:
                print(item.data)
    elif cmd_len == 3:
        store = IndexStorage.codex.get(parameters[0])
        if store:
            item = store.get(parameters[1])
            if item:
                print(deep_get(parameters[2].split("."), item.data))


def prep_command(parameters):
    if len(parameters) != 4:
        raise AttributeError("Not enough values")
    store_name, uuid, namespace_str, newvalue = parameters
    try:
        newvalue = json.loads(newvalue)
    except:
        raise AttributeError("{} is not value JSON".format(newvalue))

    store = IndexStorage.codex.get(store_name)
    namespace = namespace_str.split(".")
    if len(namespace) < 1:
        raise AttributeError("cannot alter base objects. stop being dumb.")
    item = store.get(uuid)
    if not item:
        raise AttributeError("invalid uuid {} for {}".format(uuid, store))

    value_key = namespace.pop()
    obj = deep_get(namespace, item.data)
    console_log.warn("ALTERING STORE DATA FOR {}: {}".format(store_name, uuid))
    console_log.warn(
        "PREVIOUS STATE -----------------------------------------------------"
    )
    print(obj)
    console_log.warn(
        "--------------------------------------------------------------------"
    )
    return obj, value_key, newvalue


@console_command("edit")
def edit_plugin(parameters):
    if len(parameters) != 4:
        console_log.info(
            "/mageadmin-edit <store_name> <uuid> <namespace_str> <newvalue>"
        )
        return
    try:
        obj, value_key, newvalue = prep_command(parameters)
        obj[value_key] = newvalue
    except Exception as e:
        print(e)
        return


@console_command("add")
def add_plugin(parameters):
    if len(parameters) != 4:
        console_log.info("/mageadmin-add <store> <uuid> <namespace> <addvalue>")
        return
    try:
        obj, value_key, newvalue = prep_command(parameters)
        obj.append(newvalue)
    except Exception as e:
        print(e)
        return
