def success(message: str, data=None):
    return {
        "status": "success",
        "message": message,
        "data": data
    }


def error(message: str):
    return {
        "status": "error",
        "message": message
    }
