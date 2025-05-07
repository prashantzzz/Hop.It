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
game_logo_image = pygame.image.load(resource_path('assets/hop.it.png')).convert_alpha()

#load button images
left_btn_image = pygame.image.load(resource_path('assets/left-btn.png')).convert_alpha()
right_btn_image = pygame.image.load(resource_path('assets/right-btn.png')).convert_alpha()

# Load button images for home screen
start_btn_image = pygame.image.load(resource_path('assets/Start.png')).convert_alpha()
music_btn_image = pygame.image.load(resource_path('assets/Music.png')).convert_alpha()
sfx_btn_image = pygame.image.load(resource_path('assets/SFX.png')).convert_alpha()
theme_btn_image = pygame.image.load(resource_path('assets/Theme.png')).convert_alpha()

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
new_high_score = False  # Flag to track if a new high score was achieved

# Game state management
GAME_STATE_HOME = 0
GAME_STATE_PLAYING = 1
GAME_STATE_OVER = 2
current_game_state = GAME_STATE_HOME

# Theme settings
theme_index = 0
theme_colors = [
    {'name': 'Default', 'bg': (6, 56, 107), 'text': (255, 255, 255)},
    {'name': 'Dark', 'bg': (30, 30, 30), 'text': (220, 220, 220)},
    {'name': 'Neon', 'bg': (0, 0, 0), 'text': (0, 255, 0)},
    {'name': 'Pastel', 'bg': (255, 230, 230), 'text': (70, 70, 100)}
]

# Sound settings
music_on = True
sfx_on = True

#define colours
BRIGHT_COLOR = theme_colors[theme_index]['text']
DARK_COLOR = (0, 0, 0)
UI_COLOR = theme_colors[theme_index]['bg']

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
font_game_over = pygame.font.SysFont('Lucida Sans', 36, bold=True)  # Larger font for Game Over text
font_status = pygame.font.SysFont('Lucida Sans', 16, bold=True)  # Small bold font for button status indicators

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
			horizontal_move = -8  # Matched with keyboard input for better responsiveness
			self.facing_left = True
		if keys[pygame.K_RIGHT]:
			horizontal_move = 10
			self.facing_left = False
		elif self.move_right:  # Use elif to prevent keyboard and button input conflicts
			horizontal_move = 8  # Matched with keyboard input for better responsiveness
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
			
			# Calculate the next position
			next_x = self.rect.x + (self.move_direction * (self.move_speed * 0.5))
			
			# Check if the next position would be outside the screen boundaries
			if next_x < 0 or next_x + self.rect.width > SCREEN_WIDTH:
				self.move_direction *= -1  # Reverse direction
				self.movement_timer = 0
			else:
				self.rect.x = next_x  # Only move if within boundaries

		#change direction after timer expires
		if self.movement_timer >= 100:
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

# Home screen buttons - layout based on the provided image
button_scale = 0.8  # Scale factor for buttons

# Scale and position the game logo at the top
logo_scale = 0.6  # Adjust this value to fit the screen properly
logo_width = game_logo_image.get_width() * logo_scale
logo_height = game_logo_image.get_height() * logo_scale
logo_image = pygame.transform.scale(game_logo_image, (int(logo_width), int(logo_height)))

# Start button positioned lower on the screen
start_width = start_btn_image.get_width() * button_scale
start_height = start_btn_image.get_height() * button_scale
start_button = Button(SCREEN_WIDTH//2 - start_width//2, SCREEN_HEIGHT//2 - start_height//2, start_btn_image, button_scale)

# Row of smaller buttons at the bottom
small_btn_width = music_btn_image.get_width() * button_scale
small_btn_height = music_btn_image.get_height() * button_scale
button_spacing = 20  # Space between buttons
total_width = 3 * small_btn_width + 2 * button_spacing

# Position the row of buttons centered at the bottom
row_start_x = SCREEN_WIDTH//2 - total_width//2
row_y = SCREEN_HEIGHT * 3//4  # Moved further down

music_button = Button(row_start_x, row_y, music_btn_image, button_scale)
sfx_button = Button(row_start_x + small_btn_width + button_spacing, row_y, sfx_btn_image, button_scale)
theme_button = Button(row_start_x + 2 * (small_btn_width + button_spacing), row_y, theme_btn_image, button_scale)

#create starting floor
floor = Floor(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
floor_group.add(floor)

# Function to update theme colors
def update_theme_colors():
	global BRIGHT_COLOR, UI_COLOR
	BRIGHT_COLOR = theme_colors[theme_index]['text']
	UI_COLOR = theme_colors[theme_index]['bg']

#game loop
run = True
while run:
	clock.tick(FPS)

	# Draw background based on game state
	if current_game_state == GAME_STATE_HOME:
		# Auto-scrolling background on home screen
		background_offset += 0.5  # Slow background movement
		if background_offset >= 600:
			background_offset = 0
		draw_bg(background_offset)

	if current_game_state == GAME_STATE_HOME:
		# Draw home screen
		# Draw the game logo at the top
		screen.blit(logo_image, (SCREEN_WIDTH // 2 - logo_width // 2, 50))
		
		# High score display
		best_text = f'Best: {best_height}'
		text_width = font_big.size(best_text)[0]
		draw_text(best_text, font_big, BRIGHT_COLOR, SCREEN_WIDTH - text_width - 10, 10)
		
		# Draw buttons - no text needed as images have text
		start_button.draw()
		
		# Draw status indicators next to buttons
		music_status = "ON" if music_on else "OFF"
		sfx_status = "ON" if sfx_on else "OFF"
		theme_name = theme_colors[theme_index]['name']
		
		# Draw the buttons
		music_button.draw()
		sfx_button.draw()
		theme_button.draw()
		
		# Draw status indicators below buttons using small bold font
		draw_text(music_status, font_status, BRIGHT_COLOR, 
			music_button.rect.centerx - font_status.size(music_status)[0]//2, 
			music_button.rect.bottom + 10)
		
		draw_text(sfx_status, font_status, BRIGHT_COLOR, 
			sfx_button.rect.centerx - font_status.size(sfx_status)[0]//2, 
			sfx_button.rect.bottom + 10)
		
		draw_text(theme_name, font_status, BRIGHT_COLOR, 
			theme_button.rect.centerx - font_status.size(theme_name)[0]//2, 
			theme_button.rect.bottom + 10)
		
		# Store button states before checking clicks to avoid double-triggering
		start_clicked = start_button.draw()
		music_clicked = music_button.draw()
		sfx_clicked = sfx_button.draw()
		theme_clicked = theme_button.draw()
		
		# Check button clicks
		if start_clicked:
			current_game_state = GAME_STATE_PLAYING
			# Reset game variables
			end_state = False
			player_height = 0
			camera_shift = 0
			level_up_played = False
			new_high_score = False
			show_instructions = True
			instruction_timer = 0
			# Reset hero position
			hero.hitbox.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
			hero.move_left = False
			hero.move_right = False
			# Reset floors and jets
			floor_group.empty()
			jet_group.empty()
			# Create starting floor
			floor = Floor(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
			floor_group.add(floor)
			# Start music if enabled
			if music_on:
				try:
					pygame.mixer.music.play(-1)
				except:
					pass
		
		if music_clicked:
			music_on = not music_on
			if music_on:
				try:
					pygame.mixer.music.play(-1)
				except:
					pass
			else:
				try:
					pygame.mixer.music.stop()
				except:
					pass
		
		if sfx_clicked:
			sfx_on = not sfx_on
			# Test sound effect when toggling
			if sfx_on and level_up_effect:
				try:
					level_up_effect.play()
				except:
					pass
		
		if theme_clicked:
			theme_index = (theme_index + 1) % len(theme_colors)
			update_theme_colors()
		
	elif current_game_state == GAME_STATE_PLAYING and end_state == False:
		camera_shift = hero.update()

		#draw background - scrolls with player movement
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
		
		# Play level up sound when passing best height (if SFX enabled)
		if player_height > best_height and not end_state and level_up_effect and not level_up_played and sfx_on:
			level_up_effect.play()
			level_up_played = True

		#check game over
		if hero.hitbox.top > SCREEN_HEIGHT:
			end_state = True
			#update best height only at game over
			if player_height > best_height:
				new_high_score = True  # Set flag for new high score
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
			# Fade out music and play game over sound if SFX is enabled
			try:
				pygame.mixer.music.fadeout(1000)  # Fade out over 1 second
				if sfx_on and game_over_effect:
					game_over_effect.play()  # Play game over sound
			except:
				pass
			current_game_state = GAME_STATE_OVER
	elif current_game_state == GAME_STATE_OVER:
		# Draw game over background
		screen.blit(game_over_image, (0, 0))
		
		# Center-align all text
		game_over_text = 'Game Over!'
		text_width = font_game_over.size(game_over_text)[0]
		draw_text(game_over_text, font_game_over, BRIGHT_COLOR, (SCREEN_WIDTH - text_width) // 2, 180)  # Moved up slightly to accommodate larger font
		
		height_text = 'Height:  ' + str(player_height)
		text_width = font_big.size(height_text)[0]
		draw_text(height_text, font_big, BRIGHT_COLOR, (SCREEN_WIDTH - text_width) // 2, 250)
		
		# Show 'New High Score' message if player achieved a new high score
		if new_high_score:
			high_score_text = 'New High Score!'
			text_width = font_big.size(high_score_text)[0]
			draw_text(high_score_text, font_big, (255, 255, 0), (SCREEN_WIDTH - text_width) // 2, 275)  # Yellow color for emphasis
		
		retry_text = 'Hit Space or Tap to Retry'
		text_width = font_big.size(retry_text)[0]
		draw_text(retry_text, font_big, BRIGHT_COLOR, (SCREEN_WIDTH - text_width) // 2, 300)
		key = pygame.key.get_pressed()
		# Check for space key or mouse click to restart
		if key[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
			#reset variables
			end_state = False
			player_height = 0
			camera_shift = 0
			level_up_played = False
			new_high_score = False  # Reset high score flag
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
			# Return to home screen instead of immediately restarting
			current_game_state = GAME_STATE_HOME

	#event handler
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			#update best height
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
