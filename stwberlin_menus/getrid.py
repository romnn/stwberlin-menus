
import typing
import asyncio
import functools


def flatten_list(l):
    """Flattens a given list

        >> flatten([1,2],3,[4]) = [1,2,3,4]
    """
    return [item for sublist in l for item in sublist]


def flatten_dict(l):
    """Flattens a given list

        >> flatten([1,2],3,[4]) = [1,2,3,4]
    """
    result = dict()
    for d in l:
        result = {**result, **d}
    return result


def flatten(x):
    x = list(x)
    if len(x) < 1:
        return x
    if isinstance(x[0], list):
        return flatten_list(x)
    elif isinstance(x[0], dict):
        return flatten_dict(x)
    return None


def run_sync(
    target: typing.Callable[..., typing.Any],
    *args,
    timeout: int = 10,
    **keywords,
) -> typing.Any:
    """Run async tasks synchronously with a timeout

    :param target:
    :param args:
    :param timeout:
    :param keywords:
    :return:
    """
    loop = asyncio.get_event_loop()

    async def wait(coroutine):
        try:
            return await asyncio.wait_for(
                coroutine(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print("Timeout")
            return None

    return loop.run_until_complete(
        wait(functools.partial(target, *args, **keywords)))
