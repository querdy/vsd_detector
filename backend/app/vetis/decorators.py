from app.vetis.exceptions import VetisNotResultError


def _push(method):
    def wrapper(self, *args, **kwargs):
        return self._push_request(method(self, *args, **kwargs))

    return wrapper


def _repeat(count: int = 2):
    def repeat_inner(method):
        async def wrapper(self, *args, **kwargs):
            for index in range(count):
                try:
                    result = await method(self, *args, **kwargs)
                    return result
                except VetisNotResultError:
                    if index == count - 1:
                        raise VetisNotResultError(f'Не удалось получить результат запроса')
                    continue
        return wrapper
    return repeat_inner
