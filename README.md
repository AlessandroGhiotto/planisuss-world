# Planisuss World

Design and implementation of a simulation of a
fictitious world called “Planisuss”, inspired by Wa-Tor and Conway’s Game of Life.

## Getting Started

### Environment

- _requirements.txt_ file for pip
- _requirements.yml_ file for anaconda

### Executing program

Run the _planisuss_main.py_ file in python

```
python your-path/planisuss_main.py
```

### Interacting with the simulation

For modifying all the constants present in the simulation just edit the file
_planisuss_constants.py_. Here we can find all the lower and
upper bounds for the values of the stats of Erbast and Carviz, constants for the ini-
tialization of the code like the number of rows and columns of the grid, and other ones
used for the decision function presents in the code.

**key_press_event** interactivity with the simulation (keyboard):

- **“escape”**: close the simulation;
- **“spacebar”**: play/pause the simulation;
- **“r”**: visualize only the Carviz on the grid;
- **“g”**: visualize only the Erbast on the grid;
- **“b”**: visualize only the Vegetob on the grid;
- **“a”**: visualize the complete grid;
- **“u”**: update manually to the next day (only while pause is True).

**button_press_event** interactivity with the simulation (mouse):

- **“click”** in the plot in which is visualized the world (the grid): select the cell in
  which zooming in and the cell chosen to be analysed in the table. You can click
  either in the complete grid, or in the zoomed one.

![preview](https://github.com/AlessandroGhiotto/planisuss-world/blob/main/preview.png)

## Description

The Planisuss world is constituted of a single continent which is populated by three species:
Vegetob, Erbast, and Carviz. In the simulation, several individuals of the species interact evolving
their population.

Planisuss is regularly structured in geographical units called _cells_. Cells are organized in a regular
grid structure. The cells can be occupied by water or ground. Each ground cell can host individuals of the three species,
while water cells are uninhabitable.
All the Erbast in a cell constitute a herd. Similarly, all the Carviz in a cell constitute a pride.
The basic events on Planisuss happen in discrete time units called _days_.

### The ecosystem

Three species populates Planisuss:

- **Vegetob** is a vegetable species. Spontaneously grows on the ground with a regular
  cycle. Vegetob is the nutrient of Erbast. The density can have a value between 0 and 100.
- **Erbast** is a herbivore species. Erbast eat Vegetob. They can move on the continent
  to find better living conditions. Individuals can group together, forming a herd.
- **Carviz** is a carnivore species. Carviz predate Erbast. They can move on the
  continent to find better living conditions. Individuals can group together, forming a pride.

Erbast and Carviz are animal species, and are characterized by the following properties:

- _Energy_: represents the strength of the individual. It is consumed for the activities (movement
  and fight) and can be increased by grazing.
- _Lifetime_: duration of the life of the Erbast expressed in days.
- _Age_: number of days from birth. When the age reaches the lifetime values, the individual
  terminates its existence.
- _Social attitude_: measures the likelihood of an individual to join to a herd.

### A day on Planisuss

The time on Planisussis structured in units called day. A day is articulated in the following
phases:

- **Growing** Vegetob grow everywhere of a fixed quantity.
- **Movement** The individuals of animal species (Erbast and Carviz) decide if move in another
  area. Movement is articulated as individual and social group (herd or pride) movement.
- **Grazing** Erbast which did not move, can graze the Vegetob in the area.
- **Struggle** Carviz insisting on the same area can fight or hunt.
- **Spawning** Individuals of animal species can generate their offspring.
