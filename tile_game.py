" Tile game "

import pygame
import pygame.locals as pg

# Colors
BLACK = (  0,   0,   0)
GREEN = (  0, 255,   0)
WHITE = (255, 255, 255)

# Map Size(in tiles)
MAP_WIDTH, MAP_HEIGHT = 10, 10

# Tile dimensions
TILE_WIDH, TILE_HEIGHT = 32, 32

# Screen dimensions
SCREEN_WIDTH    = MAP_WIDTH * TILE_WIDH
SCREEN_HEIGHT   = MAP_HEIGHT * TILE_HEIGHT

FRAME_RATE = 60

class Tile(pygame.sprite.Sprite):
    " Tile object "

    def __init__(self, pos):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.is_highlighted = False
        self.team = 0
        self.units = 5
        self.production_rate = 0#.125
        self.image = pygame.image.load("images/tile_neutral.png")
        self.highlighted_image = pygame.image.load("images/selected_tile_neutral.png")
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.neighbours = list()

    def draw(self, screen):
        " Update Tile visuals "

        # Draw the tile
        screen.blit(self.image, (self.rect.x, self.rect.y))

        # Draw the number of units
        fontobject = pygame.font.Font(None, 24)
        screen.blit(fontobject.render("{:3.0f}".format(self.units), 1, BLACK),
                    (self.rect.x + 2, self.rect.y + self.rect.height/2))

    def update(self):
        " Update Tile logic "

        if self.team > 0:
            self.units += self.production_rate

    def update_tile_sprite(self, team):
        " Update Tile highlights and team "

        self.team = team

        team_name = "neutral"
        if team == 1:
            team_name = "blue"
        elif team == 2:
            team_name = "red"

        if self.is_highlighted:
            image_path = "images/selected_tile_"
        else:
            image_path = "images/tile_"

        image_path += team_name
        image_path += ".png"

        highlighted_image_path = "images/selected_tile_"
        highlighted_image_path += team_name
        highlighted_image_path += ".png"

        self.image = pygame.image.load(image_path)
        self.highlighted_image = pygame.image.load(highlighted_image_path)

    def contains_neighbour(self, neighbour):
        " Checks if the Tile has the passed neighbour "

        for neigh in self.neighbours:
            if neigh == neighbour:
                return True
        return False

class GeneralPiece(pygame.sprite.Sprite):
    " Class to hold data about the teams generals "

    def __init__(self, pos, team):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.team = team

        sprite_path = "images/general_"
        if self.team == 1:
            sprite_path += "blue"
        elif self.team == 2:
            sprite_path += "red"
        sprite_path += ".png"

        self.image = pygame.image.load(sprite_path)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def draw(self, screen):
        " Update General visuals "

        # Draw the general
        screen.blit(self.image, (self.rect.x, self.rect.y))

class TileMap(object):
    " Object to hold the map data "

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.all_tiles = pygame.sprite.Group()

    def create_map(self):
        " Generate the map "

        index_x = 0
        while index_x < self.width:
            index_y = 0
            while index_y < self.height:
                new_tile = Tile((index_x * TILE_WIDH, index_y * TILE_HEIGHT))
                self.all_tiles.add(new_tile)
                index_y += 1
            index_x += 1

        blue_tile = self.get_tile((0, self.height * TILE_HEIGHT / 2))
        blue_tile.update_tile_sprite(1)
        blue_tile.units += 10
        blue_tile_second = self.get_tile((TILE_WIDH * 1, self.height * TILE_HEIGHT / 2))
        blue_tile_second.update_tile_sprite(1)
        blue_tile_second.units += 10

        red_tile = self.get_tile(
            ((self.width - 1) * TILE_WIDH, self.height * TILE_HEIGHT / 2))
        red_tile.update_tile_sprite(2)
        red_tile.units += 10
        red_tile_second = self.get_tile(
            ((self.width - 2) * TILE_WIDH, self.height * TILE_HEIGHT / 2))
        red_tile_second.update_tile_sprite(2)
        red_tile_second.units += 10

    def update_tiles(self):
        " Iterates through the tiles to update their logic "

        for tile in self.all_tiles:
            tile.update()

    def draw_tiles(self, screen):
        " Iterates through the tiles to re-draw them "

        for tile in self.all_tiles:
            tile.draw(screen)

    def get_tile(self, coords):
        " Looks for a tile based on a coordinate "

        for tile in self.all_tiles:
            if tile.rect.x <= coords[0] and abs(coords[0] - tile.rect.x) < TILE_WIDH:
                if tile.rect.y <= coords[1] and abs(coords[1] - tile.rect.y) < TILE_HEIGHT:
                    return tile

    def set_neighbours(self):
        " Looks for the neigbours of all the tiles "

        for tile in self.all_tiles:
            north_neighbour = self.get_tile(
                (tile.rect.x, tile.rect.y + TILE_HEIGHT))
            if north_neighbour is not None:
                tile.neighbours.append(north_neighbour)

            south_neighbour = self.get_tile(
                (tile.rect.x, tile.rect.y - TILE_HEIGHT))
            if south_neighbour is not None:
                tile.neighbours.append(south_neighbour)

            east_neighbour = self.get_tile(
                (tile.rect.x + TILE_WIDH, tile.rect.y))
            if east_neighbour is not None:
                tile.neighbours.append(east_neighbour)

            west_neighbour = self.get_tile(
                (tile.rect.x - TILE_WIDH, tile.rect.y))
            if west_neighbour is not None:
                tile.neighbours.append(west_neighbour)

class Game(object):
    " Object to hold the temp game data "

    def __init__(self):

        self.pressed_key        = None
        self.game_over          = False
        self.game_paused        = False
        self.selected_general   = None
        self.boosted_tile       = None
        self.general_last_tile  = None
        self.screen             = pygame.display.get_surface()
        self.all_generals       = pygame.sprite.Group()
        self.screen.fill(WHITE)

    def main(self):
        " The game "

        clock = pygame.time.Clock()

        previous_tile   = None
        current_tile    = None

        tile_map = TileMap(MAP_WIDTH, MAP_HEIGHT)
        tile_map.create_map()
        tile_map.set_neighbours()

        blue_general    = GeneralPiece((0, MAP_HEIGHT / 2 * TILE_HEIGHT), 1)
        red_general     = GeneralPiece(((MAP_WIDTH - 1) * TILE_WIDH , MAP_HEIGHT / 2 * TILE_HEIGHT), 2)

        self.all_generals.add(blue_general)
        self.all_generals.add(red_general)

        self.boosted_tile = {0 : tile_map.get_tile((0, MAP_HEIGHT * TILE_HEIGHT / 2)),
            1 : tile_map.get_tile(((MAP_WIDTH - 1) * TILE_WIDH, MAP_HEIGHT * TILE_HEIGHT / 2))}

        while not self.game_over:
            # Game Loop

            # Process Quit and Pause events
            events = pygame.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.game_over = True
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.game_paused = not self.game_paused
                        if self.game_paused:
                            popup(self.screen, "Game Paused", 50, 10,\
                                (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), GREEN, BLACK)

            if self.game_paused:
                continue

            # Reset background
            self.screen.fill(WHITE)

            # Process pygame events
            for event in events:
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos

                    temp_tile = tile_map.get_tile((mouse_x, mouse_y))

                    if self.selected_general is None:
                        temp_general = get_general((mouse_x, mouse_y), self.all_generals)
                        if temp_general is not None:
                            self.selected_general   = temp_general
                            self.general_last_tile  = temp_tile
                            continue
                    else:
                        if temp_tile.team == temp_general.team:
                            self.selected_general.rect.x = temp_tile.rect.x
                            self.selected_general.rect.y = temp_tile.rect.y
                            self.boosted_tile[self.selected_general.team - 1] = temp_tile
                            self.general_last_tile = None
                        else:
                            self.selected_general.rect.x = self.general_last_tile.rect.x
                            self.selected_general.rect.y = self.general_last_tile.rect.y
                        self.selected_general = None
                        continue

                    # Tile interaction
                    if temp_tile is None:
                        current_tile.is_highlighted     = False
                        previous_tile.is_highlighted    = False
                        current_tile.update_tile_sprite(current_tile.team)
                        previous_tile.update_tile_sprite(previous_tile.team)
                        current_tile    = None
                        previous_tile   = None
                    else:
                        previous_tile   = current_tile
                        current_tile    = temp_tile
                        current_tile.is_highlighted = True
                        current_tile.update_tile_sprite(current_tile.team)
                        if previous_tile is not None:
                            if previous_tile.units > 1 and previous_tile.team > 0 \
                                    and previous_tile.contains_neighbour(current_tile):
                                traspassed_units = (previous_tile.units / 2).__int__()
                                previous_tile.units -= traspassed_units
                                if previous_tile.team == current_tile.team:
                                    current_tile.units += traspassed_units
                                else:
                                    remaining_units = abs(traspassed_units - current_tile.units)
                                    if traspassed_units - current_tile.units > 1:
                                        if is_boosted_neighbour(self.boosted_tile[previous_tile.team - 1], previous_tile):
                                            remaining_units += traspassed_units / 2
                                        current_tile.units = remaining_units
                                        current_tile.update_tile_sprite(previous_tile.team)
                                    else:
                                        current_tile.units = remaining_units
                            current_tile.is_highlighted     = False
                            previous_tile.is_highlighted    = False
                            current_tile.update_tile_sprite(current_tile.team)
                            previous_tile.update_tile_sprite(previous_tile.team)
                            current_tile    = None
                            previous_tile   = None
                elif event.type == pg.MOUSEMOTION:
                    mouse_x, mouse_y = event.pos

                    # Dragging generals
                    if self.selected_general is not None:
                        self.selected_general.rect.x = mouse_x - self.selected_general.rect.width / 2
                        self.selected_general.rect.y = mouse_y - self.selected_general.rect.height / 2


            # Update Tiles
            tile_map.update_tiles()

            # Re-Draw Tiles
            tile_map.draw_tiles(self.screen)

            for general in self.all_generals:
                general.draw(self.screen)

            pygame.display.flip()

            clock.tick(FRAME_RATE)

def popup(screen, message, width, height, pos, bgcolor, text_color):
    " Displays a popup box "

    # How to use -> popup(self.screen, "Test", 50, 10, mouse_x, mouse_y, GREEN, BLACK)

    fontobject = pygame.font.Font(None, 18)
    pygame.draw.rect(screen, bgcolor, (pos[0] - width/2 +2, pos[1] - height/2 +2, 300, 36), 0)

    if message.count != 0:
        screen.blit(fontobject.render(message, 1, text_color),
                    (pos[0] - width/2 + 10, pos[1] - height/2 + 14))
    pygame.display.flip()

def get_general(coords, all_generals):
    " Looks for a general based on a coordinate "

    for general in all_generals:
        if general.rect.x <= coords[0] and abs(coords[0] - general.rect.x) < TILE_WIDH:
            if general.rect.y <= coords[1] and abs(coords[1] - general.rect.y) < TILE_HEIGHT:
                return general

def is_boosted_neighbour(boosted_tile, neighbour):
    " Checks if the Tile has the passed neighbour "
    for neigh in boosted_tile.neighbours:
        if neigh == neighbour:
            return True
    return False

def setup_pygame(width, height):
    " Pygame basic starting routine "

    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((width, height))

def quit_pygame():
    " Pygame basic quitting routine "

    pygame.font.quit()
    pygame.quit()

if __name__ == "__main__":
    setup_pygame(SCREEN_WIDTH, SCREEN_HEIGHT)
    Game().main()
    quit_pygame()
