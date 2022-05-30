from tinydb import TinyDB, Query

app_db = TinyDB("databases/app_" + "app1" + ".json")
app_instances = app_db.table("instances")
app_instances.update({'provisioning': False}, doc_ids=[1])

app_db = TinyDB("databases/app_" + "app1" + ".json")
instance_table = app_db.table("instances")
instance_table.remove(doc_ids=[1])
