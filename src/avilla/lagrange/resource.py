from __future__ import annotations

from avilla.core.resource import Resource
from avilla.core.selector import Selector


# TODO: resource
class LagrangeResource(Resource[bytes]):
    res: ...

    def __init__(self, res, res_id: str = ''):
        super().__init__(Selector().land('qq').resourse(res_id if res_id else str(id(res))))
        self.res = res
