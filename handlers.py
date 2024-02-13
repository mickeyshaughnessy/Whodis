from database import database as DB

db = DB()

class database():
    def __init__(self):
        pass

    def get_salt(self, key):
        return redis.hget(config.REDHASH_SALTS, key)

    def get(self, key, _hash=None):
        if not _hash:
            return redis.get(key)
        else:
            return redis.hget(_hash, key)

def validate(req):
    # checks to see if the 
    key = req.get("key")
    if key:
        salt = bd.get_salt(key)
        authed = db.get(key+salt)
        return authed # True or False
    else:
        return False

def db_resolve(req):
    pass

def db_inject(reslv, req):
    pass
