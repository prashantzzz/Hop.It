#import libraries
import pygame
import random
import os
import sys

# Helper function to handle resource paths for both development and PyInstaller
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

#initialise pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound effects

#game window dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

#create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Hop.It')

#load images
jump1_sprite = pygame.image.load(resource_path('assets/jump1.png')).convert_alpha()
jump2_sprite = pygame.image.load(resource_path('assets/jump2.png')).convert_alpha()
jump3_sprite = pygame.image.load(resource_path('assets/jump3.png')).convert_alpha()
jet_sprite = pygame.image.load(resource_path('assets/jet.png')).convert_alpha()
jet_char_sprite = pygame.image.load(resource_path('assets/jet-char.png')).convert_alpha()
background_image = pygame.image.load(resource_path('assets/bg.png')).convert_alpha()
floor_sprite = pygame.image.load(resource_path('assets/platform.png')).convert_alpha()
game_over_image = pygame.image.load(resource_path('assets/over.png')).convert_alpha()

#load button images
left_btn_image = pygame.image.load(resource_path('assets/left-btn.png')).convert_alpha()
right_btn_image = pygame.image.load(resource_path('assets/right-btn.png')).convert_alpha()

#set window icon
# pygame.display.set_icon(jump1_sprite)

#set frame rate
clock = pygame.time.Clock()
FPS = 60

#game variables
CAMERA_BOUNDARY = 200
FALL_SPEED = 0.7  # Reduced from 1 to 0.7 for slower falling
MAX_FLOORS = 10
camera_shift = 0
background_offset = 0
end_state = False
player_height = 0
level_up_played = False  # Flag to track if level up sound has been played
show_instructions = True  # Flag to show instructions at start
instruction_timer = 0  # Timer for how long to show instructions

#define colours
BRIGHT_COLOR = (255, 255, 255)
DARK_COLOR = (0, 0, 0)
UI_COLOR = (6, 56, 107)

# Create fade surface for game over screen
# fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
# fade_surface.fill(DARK_COLOR)
# fade_surface.set_alpha(180)  # Semi-transparent (0-255)

# Try to get the score file from the appropriate location
score_file_path = resource_path('score.txt')
if os.path.exists(score_file_path):
	try:
		with open(score_file_path) as file:
			best_height = int(file.read())
	except:
		best_height = 0
else:
	best_height = 0

#define font
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24, bold=True)
font_instruction = pygame.font.SysFont('Lucida Sans', 18, bold=True)  # Smaller font for instructions

# Load sounds

try:
	level_up_effect = pygame.mixer.Sound(resource_path('assets/level-up.mp3'))
	level_up_effect.set_volume(0.5)  # Set volume to 50%
except Exception as e:
	print(f"Level up sound file not found: {e}. Game will run without sound.")
	level_up_effect = None

try:
	game_over_effect = pygame.mixer.Sound(resource_path('assets/over.mp3'))
	game_over_effect.set_volume(0.5)  # Set volume to 50%
except Exception as e:
	print(f"Game over sound file not found: {e}. Game will run without sound.")
	game_over_effect = None

# Load and play background music
try:
	pygame.mixer.music.load(resource_path('assets/bg-music.mp3'))
	pygame.mixer.music.set_volume(0.25)  # Set volume to 25% (half of sound effects)
	pygame.mixer.music.play(-1)  # -1 means loop indefinitely
except Exception as e:
	print(f"Background music file not found: {e}. Game will run without music.")

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

#button class
class Button():
	def __init__(self, x, y, image, scale=1):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False
		self.held = False
		self.finger_id = None
	
	def draw(self):
		action = False
		
		#get mouse position
		pos = pygame.mouse.get_pos()
		
		#check mouseover and clicked/held conditions
		if self.rect.collidepoint(pos):
			# Check for mouse press
			if pygame.mouse.get_pressed()[0] == 1:
				if not self.clicked:
					self.clicked = True
					action = True
				self.held = True
				return action or self.held
		
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
			self.held = False
			
		#draw button on screen
		screen.blit(self.image, (self.rect.x, self.rect.y))
		
		return action or self.held
	
	def check_finger_event(self, event):
		# Handle touch events
		if event.type == pygame.FINGERDOWN:
			# Convert finger position to screen coordinates
			x = event.x * SCREEN_WIDTH
			y = event.y * SCREEN_HEIGHT
			
			if self.rect.collidepoint((x, y)):
				self.finger_id = event.finger_id
				self.held = True
				return True
				
		elif event.type == pygame.FINGERMOTION:
			if self.finger_id == event.finger_id:
				# Keep button active during finger motion if it started on this button
				return True
				
		elif event.type == pygame.FINGERUP:
			if self.finger_id == event.finger_id:
				self.finger_id = None
				self.held = False
				
		return self.held

#function for drawing info panel
def draw_panel():
	draw_text(' ' + str(int(player_height)), font_big, BRIGHT_COLOR, 10, 5)

#function for drawing the background
def draw_bg(background_offset):
	screen.blit(background_image, (0, 0 + background_offset))
	screen.blit(background_image, (0, -600 + background_offset))

#jet class
class Jet(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(jet_sprite, (30, 30))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)

	def update(self, camera_shift):
		self.rect.y += camera_shift
		#remove jet if it goes off the bottom of screen
		if self.rect.top > SCREEN_HEIGHT:
			self.kill()

#player class
class Hero():
	def __init__(self, x, y):
		self.jump1 = pygame.transform.scale(jump1_sprite, (45, 45))
		self.jump2 = pygame.transform.scale(jump2_sprite, (45, 45))
		self.jump3 = pygame.transform.scale(jump3_sprite, (45, 45))
		self.jet_char = pygame.transform.scale(jet_char_sprite, (45, 45))
		self.current_sprite = self.jump1
		self.width = 25
		self.height = 40
		self.hitbox = pygame.Rect(0, 0, self.width, self.height)
		self.hitbox.center = (x, y)
		self.vertical_speed = 0
		self.facing_left = False
		self.has_bounced = False
		self.animation_timer = 0
		self.animation_speed = 15
		self.has_jet = False
		self.jet_timer = 0
		self.jet_platforms = 0
		self.move_left = False
		self.move_right = False

	def update(self):
		#reset movement variables
		camera_shift = 0
		horizontal_move = 0
		vertical_move = 0

		#handle keyboard input
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT]:
			horizontal_move = -10
			self.facing_left = True
		elif self.move_left:  # Use elif to prevent keyboard and button input conflicts
			horizontal_move = -3  # Further reduced sensitivity for button input
			self.facing_left = True
		if keys[pygame.K_RIGHT]:
			horizontal_move = 10
			self.facing_left = False
		elif self.move_right:  # Use elif to prevent keyboard and button input conflicts
			horizontal_move = 3  # Further reduced sensitivity for button input
			self.facing_left = False
		
		#reset movement flags
		self.move_left = False
		self.move_right = False

		#apply gravity physics
		if not self.has_jet:
			self.vertical_speed += FALL_SPEED
		vertical_move += self.vertical_speed

		#update animation
		self.animation_timer += 1
		if self.has_jet:
			self.current_sprite = self.jet_char
			self.jet_timer += 1
			if self.jet_timer >= 20:  # Reduced from 30 to 20 frames for shorter duration
				self.jet_timer = 0
				self.jet_platforms += 1
				if self.jet_platforms >= 3:  # Reduced from 5 to 3 platforms
					self.has_jet = False
					self.jet_platforms = 0
					self.current_sprite = self.jump1
		else:
			if self.vertical_speed < 0:  # Going up
				if self.animation_timer >= self.animation_speed:
					self.animation_timer = 0
					if self.current_sprite == self.jump1:
						self.current_sprite = self.jump2
					else:
						self.current_sprite = self.jump1
			else:  # Going down
				if self.animation_timer >= self.animation_speed:
					self.animation_timer = 0
					if self.current_sprite == self.jump3:
						self.current_sprite = self.jump1
					else:
						self.current_sprite = self.jump3

		#prevent moving off screen edges
		if self.hitbox.left + horizontal_move < 0:
			horizontal_move = -self.hitbox.left
		if self.hitbox.right + horizontal_move > SCREEN_WIDTH:
			horizontal_move = SCREEN_WIDTH - self.hitbox.right

		#check for floor collisions
		for floor in floor_group:
			#detect collision in vertical direction
			if floor.rect.colliderect(self.hitbox.x, self.hitbox.y + vertical_move, self.width, self.height):
				#verify hero is above the floor
				if self.hitbox.bottom < floor.rect.centery:
					if self.vertical_speed > 0:
						self.hitbox.bottom = floor.rect.top
						vertical_move = 0
						self.vertical_speed = -15
						self.current_sprite = self.jump1
						self.animation_timer = 0
						self.has_bounced = True

		#check for jet collection
		for jet in jet_group:
			if self.hitbox.colliderect(jet.rect):
				self.has_jet = True
				self.vertical_speed = -10  # Reduced boost for smaller jump
				jet.kill()
				# Play level up sound when collecting jet
				try:
					level_up_effect.play()
				except:
					pass

		#scroll camera when hero reaches upper section
		if self.hitbox.top <= CAMERA_BOUNDARY:
			#only scroll during upward movement
			if self.vertical_speed < 0:
				camera_shift = -vertical_move

		#update hero position
		self.hitbox.x += horizontal_move
		self.hitbox.y += vertical_move + camera_shift

		return camera_shift

	def draw(self):
		screen.blit(pygame.transform.flip(self.current_sprite, self.facing_left, False), (self.hitbox.x - 12, self.hitbox.y - 5))

#platform class
class Floor(pygame.sprite.Sprite):
	def __init__(self, x, y, width, is_moving):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(floor_sprite, (width, 20))
		self.is_moving = is_moving
		self.movement_timer = random.randint(0, 50)
		self.move_direction = random.choice([-1, 1])
		self.move_speed = random.randint(1, 2)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self, camera_shift):
		#handle horizontal movement for moving floors
		if self.is_moving == True:
			self.movement_timer += 1
			self.rect.x += self.move_direction * self.move_speed

		#change direction at screen edges or after timer expires
		if self.movement_timer >= 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
			self.move_direction *= -1
			self.movement_timer = 0

		#update vertical position with camera scrolling
		self.rect.y += camera_shift

		#remove floor if it goes off the bottom of screen
		if self.rect.top > SCREEN_HEIGHT:
			self.kill()

#player instance
hero = Hero(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

#create sprite groups
floor_group = pygame.sprite.Group()
jet_group = pygame.sprite.Group()

#create buttons
# Position buttons at the bottom with padding of 30px from edges and bottom
button_scale = 1.5  # Larger buttons while maintaining aspect ratio
button_padding = 30
left_button = Button(button_padding, SCREEN_HEIGHT - button_padding - left_btn_image.get_height() * button_scale, left_btn_image, button_scale)
right_button = Button(SCREEN_WIDTH - button_padding - right_btn_image.get_width() * button_scale, SCREEN_HEIGHT - button_padding - right_btn_image.get_height() * button_scale, right_btn_image, button_scale)

#create starting floor
floor = Floor(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
floor_group.add(floor)

#game loop
run = True
while run:
	clock.tick(FPS)

	if end_state == False:
		camera_shift = hero.update()

		#draw background
		background_offset += camera_shift
		if background_offset >= 600:
			background_offset = 0
		draw_bg(background_offset)

		#generate floors
		if len(floor_group) < MAX_FLOORS:
			floor_width = random.randint(40, 60)
			floor_x = random.randint(0, SCREEN_WIDTH - floor_width)
			floor_y = floor.rect.y - random.randint(80, 120)
			floor_variant = random.randint(1, 2)
			
			# Enable moving floors at higher heights
			if floor_variant == 1 and player_height > 500:
				floor_moves = True
			else:
				floor_moves = False
				
			floor = Floor(floor_x, floor_y, floor_width, floor_moves)
			floor_group.add(floor)

		#generate jets every 350 points
		if player_height % 500 < 5 and len(jet_group) == 0 and player_height>400:  # Changed from 200 to 350 points
			jet_x = random.randint(50, SCREEN_WIDTH - 50)
			jet_y = floor.rect.y - random.randint(40, 60)  # Place between platforms
			jet = Jet(jet_x, jet_y)
			jet_group.add(jet)

		#update floors and jets
		floor_group.update(camera_shift)
		jet_group.update(camera_shift)

		#increase player height score
		if camera_shift > 0:
			player_height += int(camera_shift)

		#draw sprites
		floor_group.draw(screen)
		jet_group.draw(screen)
		hero.draw()

		#draw panel
		draw_panel()
		
		#draw and check buttons
		# Check for button press/hold
		hero.move_left = left_button.draw()
		hero.move_right = right_button.draw()
		
		#draw best height
		best_text = f'BEST:{best_height}'
		text_width = font_small.size(best_text)[0]
		draw_text(best_text, font_small, BRIGHT_COLOR, SCREEN_WIDTH - text_width - 10, 5)
		
		# Show instructions at start of game
		if show_instructions:
			# Calculate text width to ensure background fits
			instruction_text = 'Use LEFT/RIGHT ARROW KEYS'
			text_width = font_instruction.size(instruction_text)[0]
			
			# Semi-transparent background for instructions with padding
			padding = 20
			bg_width = text_width + (padding * 2)
			bg_x = (SCREEN_WIDTH - bg_width) // 2  # Center horizontally
			
			instruction_bg = pygame.Surface((bg_width, 60))
			instruction_bg.fill(DARK_COLOR)
			instruction_bg.set_alpha(180)
			screen.blit(instruction_bg, (bg_x, SCREEN_HEIGHT // 2 - 30))
			
			# Instruction text - centered on background
			draw_text(instruction_text, font_instruction, BRIGHT_COLOR, bg_x + padding, SCREEN_HEIGHT // 2 - 15)
			
			# Update instruction timer
			instruction_timer += 1
			if instruction_timer > 180:  # Show for 3 seconds (60 FPS * 3)
				show_instructions = False
		
		# Play level up sound when passing best height
		if player_height > best_height and not end_state and level_up_effect and not level_up_played:
			level_up_effect.play()
			level_up_played = True

		#check game over
		if hero.hitbox.top > SCREEN_HEIGHT:
			end_state = True
			#update best height only at game over
			if player_height > best_height:
				best_height = player_height
				try:
					# Get the appropriate directory to save the score file
					# For executable, use the user's documents folder
					if hasattr(sys, '_MEIPASS'):
						save_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
					else:
						save_dir = os.path.abspath(".")
					
					score_path = os.path.join(save_dir, 'score.txt')
					with open(score_path, 'w') as file:
						file.write(str(best_height))
				except Exception as e:
					print(f"Could not save score: {e}")
			# Fade out music and play game over sound
			try:
				pygame.mixer.music.fadeout(1000)  # Fade out over 1 second
				game_over_effect.play()  # Play game over sound
			except:
				pass
	else:
		# Draw game over background
		screen.blit(game_over_image, (0, 0))
		
		draw_text('Game Over!', font_big, BRIGHT_COLOR, 130, 200)
		draw_text('Height:  ' + str(player_height), font_big, BRIGHT_COLOR, 130, 250)
		draw_text('Press space to play again', font_big, BRIGHT_COLOR, 40, 300)
		key = pygame.key.get_pressed()
		if key[pygame.K_SPACE]:
			#reset variables
			end_state = False
			player_height = 0
			camera_shift = 0
			level_up_played = False
			show_instructions = True  # Show instructions again on restart
			instruction_timer = 0
			#reposition hero
			hero.hitbox.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
			hero.move_left = False
			hero.move_right = False
			#reset floors and jets
			floor_group.empty()
			jet_group.empty()
			#create starting floor
			floor = Floor(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
			floor_group.add(floor)
			# Restart background music
			try:
				pygame.mixer.music.play(-1)
			except:
				pass

	#event handler
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			#update best height
			if player_height > best_height: 	
				best_height = player_height
				try:
					# Get the appropriate directory to save the score file
					if hasattr(sys, '_MEIPASS'):
						save_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
					else:
						save_dir = os.path.abspath(".")
					
					score_path = os.path.join(save_dir, 'score.txt')
					with open(score_path, 'w') as file:
						file.write(str(best_height))
				except Exception as e:
					print(f"Could not save score: {e}")
			run = False
		
		# Handle touch events for buttons
		if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
			if left_button.check_finger_event(event):
				hero.move_left = True
			if right_button.check_finger_event(event):
				hero.move_right = True

	#update display window
	pygame.display.update()

pygame.quit()
