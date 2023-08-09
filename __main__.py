import pygame
import asyncio

import camera
import config
import discord

all_tasks = set()


async def count(countdown):
    while countdown["active"] and countdown["count"] > 0:
        await asyncio.sleep(1)
        countdown["count"] -= 1


def pygame_event_loop(queue, loop):
    while True:
        event = pygame.event.wait()
        asyncio.run_coroutine_threadsafe(queue.put(event), loop)


async def event_handler_loop(queue, countdown):
    while True:
        event = await queue.get()

        if (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            # Exit
            pygame.quit()

        if (event.type == pygame.MOUSEBUTTONUP and not countdown["active"]):
            print("CLICK")
            countdown["active"] = True
            countdown["count"] = 3
            # Start countdown loop
            count_task = asyncio.create_task(count(countdown))
            all_tasks.add(count_task)
            count_task.add_done_callback(all_tasks.discard)

            await count_task


async def upload_handler_loop(upload_queue):
    while True:
        filename = await upload_queue.get()
        if filename:
            await discord.upload(filename)
            # await asyncio.to_thread(discord.upload, filename)


async def draw_loop(screen, countdown, upload_queue, loop):
    BLACK = [0, 0, 0]
    WHITE = [255, 255, 255]

    CENTER_X = int(config.resolution[0]/2)
    CENTER_Y = int(config.resolution[1]/2)

    FONT = pygame.font.SysFont('arial',  120)
    BG_IMAGE = pygame.image.load('bg.png').convert()

    PREVIEW_SPACING_LEFT = int(
        (config.resolution[0]-config.preview_resolution[0])/2)

    PREVIEW_SPACING_TOP = int(
        (config.resolution[1]-config.preview_resolution[1])/2)

    while True:
        await asyncio.sleep(0)
        # Draw bg image
        screen.blit(BG_IMAGE, (0, 0))

        # Draw preview
        img = pygame.image.frombuffer(
            camera.buffer(), config.resolution, 'RGB')
        img = pygame.transform.scale(img, config.preview_resolution)
        screen.blit(img, (PREVIEW_SPACING_LEFT, PREVIEW_SPACING_TOP))

        # Draw countdown
        if countdown["active"]:
            pygame.draw.circle(screen, [255, 255, 255], [
                CENTER_X, CENTER_Y], 100)

            number = FONT.render(str(countdown["count"]), True, BLACK)
            text_x = int(CENTER_X - number.get_width()/2)
            text_y = int(CENTER_Y - number.get_height()/2)

            screen.blit(number, (text_x, text_y))

        if countdown["active"] and countdown["count"] == 0:
            screen.fill(WHITE)
            pygame.display.update()
            filename = camera.take_photo()
            img = pygame.image.load(filename).convert()
            img = pygame.transform.scale(img, config.resolution)
            img = pygame.transform.flip(img, flip_x=True, flip_y=False)
            screen.blit(img, (0, 0))
            pygame.display.update()
            print("display image 3s")
            asyncio.run_coroutine_threadsafe(
                upload_queue.put(filename), loop)
            await asyncio.sleep(3)

            countdown["active"] = False

        pygame.display.update()


async def main():
    screen = pygame.display.set_mode(config.resolution, pygame.FULLSCREEN)

    queue = asyncio.Queue()
    upload_queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    pygame.init()

    # asyncio.create_task(count())

    countdown = {"count": 0, "active": False}

    pygame_event_task = loop.run_in_executor(
        None, pygame_event_loop, queue, loop)
    event_handler_task = asyncio.create_task(
        event_handler_loop(queue, countdown))
    upload_handler_task = asyncio.create_task(
        upload_handler_loop(upload_queue))
    draw_task = asyncio.create_task(
        draw_loop(screen, countdown, upload_queue, loop))

    all_tasks.add(pygame_event_task)
    all_tasks.add(event_handler_task)
    all_tasks.add(upload_handler_task)
    all_tasks.add(draw_task)

    pygame_event_task.add_done_callback(all_tasks.discard)
    event_handler_task.add_done_callback(all_tasks.discard)
    upload_handler_task.add_done_callback(all_tasks.discard)
    draw_task.add_done_callback(all_tasks.discard)

    await pygame_event_task
    await event_handler_task
    await upload_handler_task
    await draw_task


if __name__ == "__main__":
    asyncio.run(main())
