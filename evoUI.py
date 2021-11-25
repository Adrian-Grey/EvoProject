import sys, pygame
import asyncio
import websockets
pygame.init()
pygame.mixer.quit()

# implement message queue modeled after pygame.event
# fetch pop data from population.csv, incorporate into main loop

async def get_population_count():
    print("get_population_count called")
    async with websockets.connect("ws://localhost:8765") as websocket:
        print("get_population_count got websocket connection")
        await websocket.send("getPop")
        print("sent getPop query")
        return(f"{await websocket.recv()}")

size = width, height = 1080, 640
white = 255, 255, 255

screen = pygame.display.set_mode(size)

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(white)

font = pygame.font.Font(None, 36)


while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    screen.fill(white)
    screen.blit(background, (0, 0))
    background.fill(white)
    text = font.render(f"Current Population: {get_population_count()}", 1, (10, 10, 10))
    textpos = text.get_rect(centerx=background.get_width()/2)
    background.blit(text, textpos)


    pygame.display.flip()
#def handle_message(message):
#    if message.name eq "population"
