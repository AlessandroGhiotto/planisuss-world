# planisuss_constants.py
"""
Collection of the main constants defined for the 
"Planisuss" project.

Values can be modified according to the envisioned behavior of the 
simulated world.

"""

### Game constants

NUMDAYS = 1000     # Length of the simulation in days

# geometry
# NUMCELLS = 50      # size of the (square) grid (NUMCELLS x NUMCELLS)
NUMCELLS_R = 50      # number of rows of the (potentially non-square) grid
NUMCELLS_C = 50      # number of columns of the (potentially non-square) grid
WATER_PROB = 0.1     # probability of a cell being water (0.0 to 1.0) (here 10% of cells are water)
                     # (excluding the border cells, which are always water)

# social groups
# NEIGHBORHOOD = 1   # radius of the region that a social group can evaluate to decide the movement
NEIGHBORHOOD_E = 1   # radius of the region that a herd can evaluate to decide the movement
NEIGHBORHOOD_C = 1   # radius of the region that a pride can evaluate to decide the movement

MAX_HERD = 300       # maximum numerosity of a herd
MAX_PRIDE = 100      # maximum numerosity of a pride

# individuals
# MAX_ENERGY = 100   # maximum value of Energy
MAX_ENERGY_E = 100   # maximum value of Energy for Erbast
MAX_ENERGY_C = 100   # maximum value of Energy for Carviz

# MAX_LIFE = 10000   # maximum value of Lifetime
MAX_LIFE_E = 1000    # maximum value of Lifetime for Erbast
MAX_LIFE_C = 1000    # maximum value of Lifetime for Carviz
MIN_LIFE_E = 10      # if Lifetime is lower than this value, the Erbast is terminated
MIN_LIFE_C = 10      # if Lifetime is lower than this value, the Carviz is terminated

# AGING = 1           # energy lost each month
AGING_E = 1          # energy lost each month for Erbast
AGING_C = 1          # energy lost each month for Carviz

GROWING = 1          # Vegetob density that grows per day.


# SOCIAL ATTITUDE

HUNGER_E = 1.1       # devide the social_attitude of an Erbast, when doesn't graze due to lack of Vegetob
HUNGER_C = 1.03      # devide the social_attitude of a Carviz, when doesn't hunt due to lack of Erbast
EAT_E = 0.01         # sum to the social_attitude of a Erbast, when it graze
EAT_C = 0.05         # sum to the social_attitude of a Carviz, when it hunt
WIN_FIGHT = 0.1      # increase social attitude of the Carviz after they win a fight



# MOVEMENT

# erbast.energy * erbast.social_attitude < const.MIN_MOVEMENT_E : the animal stay while the herd move
# erbast.energy / erbast.social_attitude > const.MAX_MOVEMENT_E : the animal move while the herd stay
MIN_MOVEMENT_E = 3   # decide if a Erbast want to stay while the herd move
MAX_MOVEMENT_E = 300 # decide if a Erbast want to move while the herd stay
MIN_MOVEMENT_C = 3   # decide if a Carviz want to stay while the pride move
MAX_MOVEMENT_C = 300 # decide if a Carviz want to move while the pride stay

JOIN_PRIDE = 0.9     # if pride1.mean_social_attitude + pride2.mean_social_attitude > const.JOIN_PRIDE
                     # pride1 and pride2 are joined


### Initialization constants

# We will use random.randint(NUM_LB, NUM_UB)

NUM_HERDS_LB = 50     # minimum number of herds generated at the start
NUM_HERDS_UB = 80    # maximum number of herds generated at the start
NUM_PRIDES_LB = 20    # minimum number of prides generated at the start
NUM_PRIDES_UB = 30   # maximum number of prides generated at the start

NUM_ERBAST_LB = 10    # minimum number of erbast spawned in a herd
NUM_ERBAST_UB = 30    # maximum number of erbast spawned in a herd
NUM_CARVIZ_LB = 3     # minimum number of carviz spawned in a pride
NUM_CARVIZ_UB = 10    # maximum number of carviz spawned in a pride
