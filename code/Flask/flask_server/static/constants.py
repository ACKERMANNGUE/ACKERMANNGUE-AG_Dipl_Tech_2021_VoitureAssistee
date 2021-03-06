DEFAULT_MODE = False
MODE_OFF = 0
MODE_ON = 1
DEFAULT_SPEED = 0
DEFAULT_ANGLE = 0

BTN_REQUEST_RESET_ANGLE = "reset angle"
BTN_REQUEST_STOP = "stop"
BTN_REQUEST_DISCONNECT = "disconnect"

SENSOR_BRIGHTPI = "bright-pi"
SENSOR_CAMERA = "camera"
SENSOR_FLYINGFISH = "flying-fish"

CHART_PATH = "static/img/"
CHART_NAME = "chart.jpg"
CHART_DOWN_NAME = "radar_down.png"

GPIO_FLYING_FISH_FRONT_RIGHT = 17
GPIO_FLYING_FISH_FRONT_LEFT = 27
GPIO_FLYING_FISH_BACK_RIGHT = 23
GPIO_FLYING_FISH_BACK_LEFT = 24

GPIO_BOUNCEBACK = 300

FLYING_FISH_STATE_GROUNDED = True
FLYING_FISH_STATE_UNGROUNDED = False

GPIO_FLYING_FISH = [
    (GPIO_FLYING_FISH_FRONT_LEFT, FLYING_FISH_STATE_GROUNDED),
    (GPIO_FLYING_FISH_FRONT_RIGHT, FLYING_FISH_STATE_GROUNDED),
    (GPIO_FLYING_FISH_BACK_LEFT, FLYING_FISH_STATE_GROUNDED),
    (GPIO_FLYING_FISH_BACK_LEFT, FLYING_FISH_STATE_GROUNDED),
]

CODE_TURN_NOTHING = 0
CODE_TURN_LEFT = 1
CODE_TURN_RIGHT = 2

CODE_MOVE_NOTHING = 0
CODE_MOVE_FORWARD = 1
CODE_MOVE_BACKWARD = 2

MAX_ANGLE_OBSTACLE_DETECTION = 15
FRONT_DISTANCE_OBSTACLE_DETECTION = 320
BACK_DISTANCE_OBSTACLE_DETECTION = 150

FULL_ANGLE = 360
HALF_ANGLE = FULL_ANGLE / 2


MAX_SPEED_FROM_BORDER = 0.2
