CONFIG_VALUES = [
    {
        "name": "RABBITMQ_HOST",
        "type": str,
        "required": True,
        "default": None
    },
    {
        "name": "QUEUE_NAME",
        "type": str,
        "required": True,
        "default": None
    },
    {
        "name": "MSG_LIMIT",
        "type": int,
        "required": False,
        "default": None
    },
    {
        "name": "MIN_SLEEP",
        "type": int,
        "required": False,
        "default": 0
    },
    {
        "name": "MAX_SLEEP",
        "type": int,
        "required": False,
        "default": 3
    }
]
