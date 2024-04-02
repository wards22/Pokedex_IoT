import os
import time
import ssl
import binascii
import wifi
import vectorio
import socketpool
import adafruit_requests
import displayio
from jpegio import JpegDecoder
from adafruit_display_text import label, wrap_text_to_lines
import terminalio
import adafruit_pycamera
import json
import adafruit_imageload



# SCALE FOR DISPLAYING RETURNED TEXT FROM OPENAI
text_scale = 2

# OPENAI KEY AND PROMPTS FROM SETTINGS.TOML
openai_api_key = os.getenv("OPENAI_API_KEY")
what_pokemon_prompt = os.getenv("WHAT_POKEMON_PROMPT")

prompts = [what_pokemon_prompt]
num_prompts = len(prompts)
prompt_index = 0
prompt_labels = ["POKEMON"]
PokemonName = ""
PokeID = ""
PokeHeight = ""
PokeWeight = ""
PokeType = ""
PokeAbility = ""

# ENCODE JPEG TO BASE64 FOR OPENAI
def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        base64_encoded_data = binascii.b2a_base64(image_data).decode('utf-8').rstrip()
        return base64_encoded_data


# VIEW RETURNED TEXT ON MEMENTO SCREEN
def view_text(the_text):
    rectangle = vectorio.Rectangle(pixel_shader=palette, width=240, height=240, x=0, y=0)
    pycam.splash.append(rectangle)
    the_text = "\n".join(wrap_text_to_lines(the_text, 20))
    if prompt_index == 1:
        the_text = the_text.replace("*", "\n")
    text_area = label.Label(terminalio.FONT, text=the_text,
                            color=0xFFFFFF, x=2, y=10, scale=text_scale)
    pycam.splash.append(text_area)
    pycam.display.refresh()


# SEND IMAGE TO OPENAI, PRINT THE RETURNED TEXT AND SAVE IT AS A TEXT FILE
def send_img(img, prompt):
    global PokemonName
    base64_image = encode_image(img)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{prompt}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions",
                             headers=headers, json=payload)
    json_openai = response.json()
    print(json_openai['choices'][0]['message']['content'])
    alt_text_file = img.replace('jpg', 'txt')
    alt_text_file = alt_text_file[:11] + f"_{prompt_labels[prompt_index]}" + alt_text_file[11:]
    if prompt_index == 5:
        alt_text_file = alt_text_file.replace("?", "")
    with open(alt_text_file, "a") as fp:
        fp.write(json_openai['choices'][0]['message']['content'])
        fp.flush()
        time.sleep(1)
        fp.close()
    x = json_openai['choices'][0]['message']['content']
    PokemonName = str(x)
    # pokeID = get_pokemonID_only(PokemonName)
    # display_pokemon_sprite(pokeID)
    #view_text(x)
    get_pokemon_info(PokemonName)


# def load_sprite(sprite_id, pokemon_name):
#     file = f"sd/pokemon/sprites/bmp/{sprite_id}.bmp"
#     image, palette = adafruit_imageload.load(file)
#     display = pycam.display
#
#     tile_grid = displayio.TileGrid(image, pixel_shader=palette)
#     tile_grid.x = display.width // 11 - tile_grid.tile_width // 11
#     tile_grid.y = display.height // 24 - tile_grid.tile_height // 24
#
#     group = displayio.Group(scale=2)
#     group.append(tile_grid)
#     name_area = label.Label(terminalio.FONT, text=pokemon_name,
#                             color=0xFFFFFF,
#                             x=(display.width // 4 - tile_grid.tile_width // 16) - (2 * len(pokemon_name)),
#                             y=tile_grid.y + tile_grid.tile_height, scale=1)
#     group.append(name_area)  # Append the name label to the same group as the sprite
#
#     display.root_group = group
#     pycam.display.refresh()

# def load_sprite(sprite_id, pokemon_name):
#     file = f"sd/pokemon/sprites/bmp/{sprite_id}.bmp"
#     image, palette = adafruit_imageload.load(file)
#
#
#     display = pycam.display
#
#     rectangle = vectorio.Rectangle(pixel_shader=palette, width=240, height=240, x=0, y=0)
#     pycam.splash.append(rectangle)
#
#     tile_grid = displayio.TileGrid(image, pixel_shader=palette)
#     tile_grid.x = 60
#     tile_grid.y = 60
#     name_area = label.Label(terminalio.FONT, text=pokemon_name,
#                             color=0xFFFFFF,
#                             x=120 - (6 * len(pokemon_name)),
#                             y=200,
#                             scale=2)
#
#     pycam.splash.append(tile_grid)
#     pycam.splash.append(name_area)
#     pycam.display.refresh()

def load_sprite(sprite_id, pokemon_name):
    file = f"sd/pokemon/sprites/bmp/{sprite_id}.bmp"
    image, palette = adafruit_imageload.load(file)

    display = pycam.display

    rectangle = vectorio.Rectangle(pixel_shader=palette, width=240, height=240, x=0, y=0)
    pycam.splash.append(rectangle)
    # Scale factor to make the image larger
    scale_factor = 2

    # Create a new bitmap and scale it
    scaled_bitmap = displayio.Bitmap(image.width * scale_factor, image.height * scale_factor, len(palette))
    for y in range(image.height):
        for x in range(image.width):
            color = image[x, y]
            for dy in range(scale_factor):
                for dx in range(scale_factor):
                    scaled_bitmap[x * scale_factor + dx, y * scale_factor + dy] = color

    # Create a new tile grid with the scaled bitmap
    tile_grid = displayio.TileGrid(scaled_bitmap, pixel_shader=palette)

    # Adjust the position of the tile grid
    tile_grid.x = (display.width - image.width * scale_factor) // 2
    tile_grid.y = (display.height - image.height * scale_factor) // 2

    # Create label with the Pokémon name
    name_area = label.Label(terminalio.FONT, text=pokemon_name,
                            color=0xFFFFFF,
                            x=(display.width - 6 * len(pokemon_name) * scale_factor) // 2,
                            y=display.height - 30,
                            scale=2)

    # Append the tile grid and label to the display
    pycam.splash.append(tile_grid)
    pycam.splash.append(name_area)
    pycam.display.refresh()

# VIEW IMAGES ON SD CARD TO RE-RESEND TO OPENAI
def load_image(bit, file):
    bit.fill(0b00000_000000_00000)  # fill with a middle grey
    decoder.open(file)
    decoder.decode(bit, scale=0, x=0, y=0)
    pycam.blit(bit, y_offset=32)
    pycam.display.refresh()

def get_pokemonID_only(PokemonName):
    url = f"https://pokeapi.co/api/v2/pokemon/{PokemonName.lower()}"
    response = requests.get(url)
    print(response.json())  # Print the JSON response for debugging
    if response.status_code == 200:
        pokemon_data = response.json()
        pID = pokemon_data['id']
    return pID

# USES GLOBAL POKEMONNAME VARIABLE TO GET THE POKEMON'S ID HEIGHT, WEIGHT, TYPE, AND ABILITIES
def get_pokemon_info(PokemonName):
    global PokeID
    global PokeHeight
    global PokeWeight
    global PokeType
    global PokeAbility
    url = f"https://pokeapi.co/api/v2/pokemon/{PokemonName.lower()}"
    response = requests.get(url)
    print(response.json())  # Print the JSON response for debugging
    if response.status_code == 200:
        pokemon_data = response.json()

        PokeID = pokemon_data['id']
        PokeHeight = pokemon_data['height']
        PokeWeight = pokemon_data['weight']
        PokeType = [type_data['type']['name'] for type_data in pokemon_data['types']]
        PokeAbility = [ability_data['ability']['name'] for ability_data in pokemon_data['abilities']]

    #     pokemon_id = pokemon_data['id']
    #     pokemon_height = pokemon_data['height']
    #     pokemon_weight = pokemon_data['weight']
    #     pokemon_types = [type_data['type']['name'] for type_data in pokemon_data['types']]
    #     pokemon_abilities = [ability_data['ability']['name'] for ability_data in pokemon_data['abilities']]
    #     return pokemon_id, pokemon_height, pokemon_weight, pokemon_types, pokemon_abilities
    #
    # else:
    #     return "None", "None", "None", "None", "None"

print()
print("Connecting to WiFi")
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
print("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

palette = displayio.Palette(1)
palette[0] = 0x000000
decoder = JpegDecoder()
# used for showing images from sd card
bitmap = displayio.Bitmap(240, 176, 65535)

pycam = adafruit_pycamera.PyCamera()
pycam.mode = 0  # only mode 0 (JPEG) will work in this example

# Resolution of 320x240 is plenty for OpenAI
pycam.resolution = 1  # 0-12 preset resolutions:
#                      0: 240x240, 1: 320x240, 2: 640x480, 3: 800x600, 4: 1024x768,
#                      5: 1280x720, 6: 1280x1024, 7: 1600x1200, 8: 1920x1080, 9: 2048x1536,
#                      10: 2560x1440, 11: 2560x1600, 12: 2560x1920
# pycam.led_level = 1  # 0-4 preset brightness levels
# pycam.led_color = 0  # 0-7  preset colors: 0: white, 1: green, 2: yellow, 3: red,
#                                          4: pink, 5: blue, 6: teal, 7: rainbow
pycam.effect = 0  # 0-7 preset FX: 0: normal, 1: invert, 2: b&w, 3: red,
#                                  4: green, 5: blue, 6: sepia, 7: solarize
# sort image files by numeric order
all_images = [
    f"/sd/{filename}"
    for filename in os.listdir("/sd")
    if filename.lower().endswith(".jpg")
]
# all_images.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
# add label for selected prompt
rect = vectorio.Rectangle(pixel_shader=palette, width=240, height=20, x=0, y=0)
prompt_txt = label.Label(
    terminalio.FONT, text=prompt_labels[prompt_index], color=0xFF0055, x=10, y=15, scale=2
)
# pylint: disable=protected-access
pycam._botbar.append(rect)
pycam._botbar.append(prompt_txt)
# pylint: enable=protected-access
pycam.display.refresh()

view = False
new_prompt = False
file_index = -1

view_info = False

while True:
    if new_prompt:
        pycam.display_message("")
    if not view:
        if not new_prompt:
            pycam.blit(pycam.continuous_capture())
    pycam.keys_debounce()
    if pycam.shutter.long_press:
        pycam.autofocus()
    if pycam.shutter.short_count:
        try:
            pycam.display_message("snap", color=0x00DD00)
            pycam.capture_jpeg()
            pycam.live_preview_mode()
        except TypeError as exception:
            pycam.display_message("Failed", color=0xFF0000)
            time.sleep(0.5)
            pycam.live_preview_mode()
        except RuntimeError as exception:
            pycam.display_message("Error\nNo SD Card", color=0xFF0000)
            time.sleep(0.5)
        all_images = [
            f"/sd/{filename}"
            for filename in os.listdir("/sd")
            if filename.lower().endswith(".jpg")
        ]
        all_images.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        the_image = all_images[-1]
        pycam.display_message("Loading...", color=0x00DD00)
        send_img(the_image, prompts[prompt_index])
        view = True
        load_sprite(PokeID, PokemonName)

    # PRESS THE DOWN BUTTON TO DISPLAY THE POKEMON'S INFORMATION
    if pycam.down.fell:
        view_info = True
        pycam.display_message("Loading...", color=0x00DD00)

        rectangle = vectorio.Rectangle(pixel_shader=palette, width=240, height=240, x=0, y=0)
        pycam.splash.append(rectangle)

        # pokemon_id, pokemon_height, pokemon_weight, pokemon_types, pokemon_abilities = get_pokemon_info(PokemonName)
        abilities_text = "\n".join([f"• {ability}" for ability in PokeAbility])
        pokemon_info = f"ID: {PokeID}\n" + f"Height: {PokeHeight}dm\n" + f"Weight: {PokeWeight}hg\n" + f"Types: {', '.join(PokeType)}\n" + f"Abilities:\n{abilities_text}"

        the_text = "\n".join(wrap_text_to_lines(pokemon_info, 20))
        if prompt_index == 1:
            pokemon_info = pokemon_info.replace("*", "\n")
        text_area = label.Label(terminalio.FONT, text=pokemon_info,
                                    color=0xFFFFFF, x=2, y=10, scale=text_scale)
        pycam.splash.append(text_area)
        pycam.display.refresh()
        # view_text(pokemon_info)

    # PRESS OK BUTTON TO RESET THE SCREEN AND TAKE ANOTHER PICTURE
    if pycam.ok.fell:
        if view_info:
            pycam.splash.pop()
            pycam.splash.pop()
            pycam.display.refresh()
            view_info = False
            view = True
        if view:
            pycam.splash.pop()
            pycam.splash.pop()
            pycam.splash.pop()
            pycam.display.refresh()
            view = False
        if new_prompt:
            pycam.display_message("OpenAI..", color=0x00DD00)
            send_img(filename, prompts[prompt_index])
            new_prompt = False
            view = True

    # PRESS RIGHT BUTTON TO TEST CRIES
    if pycam.right.fell:
        if not view:
            load_sprite(6,"Charizard")
            view = True