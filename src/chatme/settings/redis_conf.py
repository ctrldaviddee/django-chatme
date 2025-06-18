from decouple import config


def get_redis_params(db=0):
    return {
        "host": config("REDIS_HOST"),
        "port": config("REDIS_PORT", cast=int, default=6379),
        "db": db,
        "password": config("REDIS_PASSWORD", default=""),
    }
