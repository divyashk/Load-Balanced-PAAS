from tinydb import TinyDB, Query

app_db = TinyDB("databases/app_" + "app1" + ".json")
app_instances = app_db.table("instances")
app_instances.update({'provisioning': False}, doc_ids=[1])
