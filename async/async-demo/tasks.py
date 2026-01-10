import asyncio
import time


def sync_infinite_loop():
    """同步無窮迴圈"""
    i = 0
    while True:
        print(f"[SYNC] {i}")
        time.sleep(1)
        i += 1


async def async_infinite_loop():
    """異步無窮迴圈"""
    i = 0
    while True:
        print(f"[ASYNC] {i}")
        await asyncio.sleep(1)
        i += 1
