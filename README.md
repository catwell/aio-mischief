# aio-mischief

This is a demo of a nasty hack to make [aiomonitor](https://github.com/aio-libs/aiomonitor) display asynchronous generator stacks.

The reason it does not by default is that asynchronous generators are [not introspectable](https://github.com/python/cpython/issues/76991). That is... unless you use ctypes :grin:

To try it, run `rye sync` and `python src/example.py`. If you look at the trace for `generator_rec` you will see something like this:

```
File "/.../aio-mischief/src/example.py", line 40, in generator_loop
  async for x in generator_rec(n):
```

This is what you get with standard aiomonitor.

Now try `AIO_MISCHIEF_PATCH=1 python src/example.py` and you should see something like this:

```
File "/.../aio-mischief/src/example.py", line 40, in generator_loop
  async for x in generator_rec(n):
File "/.../aio-mischief/src/example.py", line 32, in generator_rec
  async for x in generator_rec(n - 1):
File "/.../aio-mischief/src/example.py", line 32, in generator_rec
  async for x in generator_rec(n - 1):
File "/.../aio-mischief/src/example.py", line 32, in generator_rec
  async for x in generator_rec(n - 1):
File "/.../aio-mischief/src/example.py", line 35, in generator_rec
  async for x in generator():
File "/.../aio-mischief/src/example.py", line 27, in generator
  await asyncio.sleep(5)
File "/.../.rye/py/cpython@3.12.8/lib/python3.12/asyncio/tasks.py", line 665, in sleep
  return await future
```

**You are now done, do not under any pretext look [under the hood](src/aio_mischief/__init__.py)!** :)
