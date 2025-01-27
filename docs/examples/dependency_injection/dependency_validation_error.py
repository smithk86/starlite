from typing import Any, Dict

from litestar import Litestar, get
from litestar.di import Provide


def provide_str() -> str:
    """Returns a string."""
    return "whoops"


@get("/", dependencies={"injected": Provide(provide_str)})
def hello_world(injected: int) -> Dict[str, Any]:
    """Handler expects and `int`, but we've provided a `str`."""
    return {"hello": injected}


app = Litestar(route_handlers=[hello_world])
