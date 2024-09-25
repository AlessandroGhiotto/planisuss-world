# planisuss_main.py
# python=3.9.19

""" 
Implementation of the Planisuss world

"""

# IMPORTS
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import planisuss_constants as const
from functools import reduce
from IPython import get_ipython



# --------------------------------------------------------------------------------------------------------------------- # 
# ERBAST and CARVIZ
# --------------------------------------------------------------------------------------------------------------------- # 
class Specie:  
    def __init__(self, energy, lifetime, social_attitude, age=0):
        """
        Parent class of Erbast and Carviz

        Parameters
        ----------
        energy : int
            represents the strength of the individual. It is consumed for the activities (movement
            and fight) and can be increased by grazing/hunting. When the energy value reaches 0, the
            animal dies.
        lifetime : int
            duration of the life of the animal expressed in days. Its value is set at the birth
            and does not change.
        social_attitude : float
            measures the likelihood of an individual to join to a herd. It is represented
            by a value in [0, 1].
        age : int, optional
            number of days from birth. When the age reaches the lifetime values, the individual
            terminates its existence. The default is 0
        """
        self.energy = energy                    # [0, MAX_ENERGY]
        self.lifetime = lifetime                # [1, MAX_LIFE]
        self.age = age                          # [0, self.lifetime]
        self.social_attitude = social_attitude  # [0, 1]
        self.moved = False                      # Bool, True if the animal moved today, false otherwise


class Erbast(Specie):
    def __init__(self, energy, lifetime, social_attitude, age=0):
        super().__init__(energy, lifetime, social_attitude, age)
    
    
class Carviz(Specie):
    def __init__(self, energy, lifetime, social_attitude, age=0):
        super().__init__(energy, lifetime, social_attitude, age)
  
    
  
# --------------------------------------------------------------------------------------------------------------------- # 
# HERD and PRIDE
# --------------------------------------------------------------------------------------------------------------------- #        
class Group:
    def __init__(self):
        """
        Parent class of Herd and Pride
        """
        self.population = []            # list of the animals present in the group
        self.total_energy = 0           # Sum of the energy of the animals             
        self.total_lifetime = 0         # Sum of the social_attitude of the animals  
        self.total_age = 0              # Sum of the social_attitude of the animals   
        self.total_social_attitude = 0  # Sum of the social_attitude of the animals   
    
    def world_init(self, grid, cell, idx_specie, NUM_ANIMALS_LB, NUM_ANIMALS_UB, MAX_ENERGY, MAX_LIFE):
        """
        Method used at the beginning of the simulation, when I initialize the world. In particular
        is used to initialize a starting group, with specific characteristic.
        Create a Herd or Pride with a random number of animals in [NUM_ANIMALS_LB, NUM_ANIMALS_UB],
        with the following characteristics:
            - energy : a int in [0, MAX_ENERGY]
            - lifetime : a int in [1, MAX_LIFE]
            - social_attitude : a float in [0, 1]
            - age = 0

        Parameters
        ----------
        grid : ndarray
        cell : tuple
            The cell in which is present the group.
        idx_specie : int
            1 for Herd, 2 for Pride.
        NUM_ANIMALS_LB : int
        NUM_ANIMALS_UB : int
        MAX_ENERGY : int
        MAX_LIFE : int
        
        Returns
        -------
        grid : ndarray
            The grid, updated with the addition of the new Animals.
        """
        # choose a random number of Animals
        num_animals = random.randint(NUM_ANIMALS_LB, NUM_ANIMALS_UB) 
        grid[idx_specie, cell[0], cell[1]] += num_animals
        for animal in range(num_animals):
            energy = random.randint(0, MAX_ENERGY)   # random energy in [0, MAX_ENERGY]
            lifetime = random.randint(1, MAX_LIFE)   # random lifetime in [1, MAX_LIFE]
            social_attitude = random.random()        # random social_attitude in [0, 1]
            # add the animal to the population list of the group
            self.population.append(self.create_animal(energy, lifetime, social_attitude))
        return grid # the updated grid

    def join_groups(self, group_list, res_group, MAX_GROUP):
        """ 
        Unify the groups that are present in the same cell.
        If the number of animals after the merge is greater then MAX_GROUP, a part of the population dies of overpopulation.
        
        Parameters
        ----------
        group_list : list
            List of Erbast or Carviz, which are present in the same cell.
        res_group : object
            Herd() or Pride().
        MAX_GROUP : int
            Max number of individuals in a group.

        res_group
        -------
        The resulting group, after the join of the groups in the group_list
        """
        # sum of the populations
        res_group.population = reduce(lambda x, y: x + y.population, group_list, list())
        if len(res_group.population) > MAX_GROUP:
            # sort the animals by decreasing (reverse=True) energy, and take the firsts MAX_GROUP number of animals
            res_group.population.sort(key=lambda animal: animal.energy, reverse=True)
            # dispose of the least strong animals, if necessary
            res_group.population = res_group.population[0 : MAX_GROUP + 1]
        return res_group # return the resulting group
                
    def spawning(self, grid, cell, idx_specie, AGING, MIN_LIFE, MAX_LIFE, MAX_GROUP):
        """
        The Age value of the animals are increased by one day.
        Those that reach an age multiple of 10 (one month) have their Energy decreased by AGING.
        Every animal with energy == 0 is terminated, since it has suffered fatigue and hunger.
        Every animal with lifetime < MIN_LIFE is terminated, since is affected by a mortal disease.
        Those that reach their lifetime are terminated by spawning two offsprings. The offsping properties
        are set with the following rules:
            - Age: set to 0.
            - Energy: the sum of the Energy of the offsprings is equal to the Energy of the parent.
            - Other properties: the average of the properties of the offsprings are equal to the corresponding
              properties of the parent.
              (the sum of the property values of the offsprings is the double of the corresponding property of the parent)
        The spawning is allowed only if the social group can be enlarged to include the offsprings,
        otherwise the offspring with less energy is terminated by the other animals of the herd/pride.

        Parameters
        ----------
        grid : ndarray
        cell : tuple
            The cell in which is present the group.
        idx_specie : int
            1 for Erbast, 2 for Carviz.
        AGING : int
        MIN_LIFE : int
        MAX_LIFE : int
        MAX_GROUP : int

        Returns
        -------
        grid : ndarray
            The grid, updated with the addition of the new Animals.
        """
        # we create a list and then incrementally add the animals
        # I can't modify directly the group, because I will change the length of the list during the iteration
        Ls = list()
        for animal in self.population:
            animal.age += 1
            # AGING
            # if age is a multiple of 10, the energy is decreased by AGING
            if animal.age % 10 == 0:
                animal.energy -= AGING
            
            if animal.energy == 0 or animal.lifetime < MIN_LIFE:
                # a animal with 0 energy or short lifetime is terminated (no spawning)
                grid[idx_specie, cell[0], cell[1]] -= 1 
            # SPAWNING
            elif animal.age == animal.lifetime:
                # stats for the offsprings
                energy1 = random.randint(1, max(1, animal.energy - 1)) # don't spawn with 0 energy
                energy2 = animal.energy - energy1
                # min with MAX_LIFE so I don't get a too big lifetime
                lifetime1 = random.randint(1, min(2*animal.lifetime - 1, MAX_LIFE))
                lifetime2 = 2*animal.lifetime - lifetime1
                # use max and min, so that I don't go out of the range [0, 1]
                social_attitude1 = random.uniform(max(0, 2*animal.social_attitude - 1), min(2*animal.social_attitude, 1))
                social_attitude2 = 2*animal.social_attitude - social_attitude1  
                if energy1 >= energy2:
                    # we spawn the offspring with more energy
                    Ls.append(self.create_animal(energy1, lifetime1, social_attitude1))
                    if grid[idx_specie, cell[0], cell[1]] < MAX_GROUP:
                        # if there is space we spawn also the other
                        Ls.append(self.create_animal(energy2, lifetime2, social_attitude2))
                        grid[idx_specie, cell[0], cell[1]] += 1
                else: # energy1 < energy2 (same as before)
                    Ls.append(self.create_animal(energy2, lifetime2, social_attitude2))  
                    if grid[idx_specie, cell[0], cell[1]] < MAX_GROUP:
                        Ls.append(self.create_animal(energy1, lifetime1, social_attitude1)) 
                        grid[idx_specie, cell[0], cell[1]] += 1
            # If we don't terminate the animal and we don't spawn offsprings, we simply reappend the animal
            else:
                Ls.append(animal)
        # save as population the updated list of Animals
        self.population = Ls
        return grid # the updated grid

    def update_stats(self):
        """
        Update the stats of the group, which are the following:
            - self.total_energy
            - self.total_lifetime
            - self.total_age
            - self.total_social_attitude
        """
        # x = (enrgy, lifetime, age, social_attitude)
        # y = each Erbast in self.population
        total_stats = reduce(lambda x, y: x + np.array((y.energy, y.lifetime, y.age, y.social_attitude)), \
                             self.population, np.array((0, 0, 0, 0))) 
        
        self.total_energy = total_stats[0]         
        self.total_lifetime = total_stats[1]
        self.total_age = total_stats[2]
        self.total_social_attitude = total_stats[3]

    # def create_animal(self, energy, lifetime, social_attitude, age=0):
    #     """
    #     Create an Erbast or a Carviz. This method is implemented only in the child classes.
    #     It will identify to what object is applied to:
    #         - if it is a Herd, it will create a Erbast,
    #         - if it is a Pride, it will create a Carviz.
    #     """
    #     return Animal(energy, lifetime, social_attitude, age)


class Herd(Group):
    def __init__(self):
        super().__init__()
     
    def world_init(self, grid, cell):  
        """
        We use inheritance for specifying different constants for Erbast and Carviz
        Erbast : idx_specie = 1
        NUM_ERBAST_LB, NUM_ERBAST_UB, MAX_ENERGY_E, MAX_LIFE_E
        """
        return super().world_init(grid, cell, idx_specie=1, \
                                  NUM_ANIMALS_LB=const.NUM_ERBAST_LB, NUM_ANIMALS_UB=const.NUM_ERBAST_UB, \
                                  MAX_ENERGY=const.MAX_ENERGY_E,      MAX_LIFE=const.MAX_LIFE_E)
    
    def movement(self, grid, cell, neighbours):
        """
        The herd decides whether to move or not, and the Erbast present in the group
        choose whether to follow the herd or separate.
        
        The most appealing cell in the neighborhood is identified (the one with more nutrients). 
        Once the herd of the cell made a decision (stay or move), the individuals can choose
        if they will follow the social group or made a different decision, splitting by the social group.
        Splitting decision can be formed considering the properties of the individual (e.g., the herd will
        move, while the individual having a low value of energy may stay; or, on the contrary, the herd
        will stay, but strong Erbast may want to move, due to the lack of Vegetob in the cell) and is weighted
        with the social attitude of the individual. The movement costs to each Erbast one point of Energy.
        
        Parameters
        ----------
        grid : ndarray
        cell : tuple
            The cell in which is present the herd.
        neighbours : list
            List of the neighbours cells to our cell in analisys.

        Returns
        -------
        res_herds : list
            list with 1 or 2 herds (2 if some animals have separated from the herd).
        """
        # sort the neighbours cell by decreasing (reverse=True) value of Vegetob (nutrients)
        neighbours.sort(key=lambda cell: grid[0, cell[0], cell[1]], reverse=True)
        if len(neighbours) != 0:        # check if there is any neighbour
            best_cell = neighbours[0]   # pick the first cell in the list, which is the most suitable one
        else:                           
            return [(self, cell)]       # if I don't have any neighbour I don't move
             
        # move_erbast = list()   # res of the movement, Erbast that moved
        # stay_erbast = list()   # res of the movement, Erbast that didn't moved  
        # decide if the group will move or not:
        # they move if : - in the current cell there aren't enough vegetob for everyone
        #                - in the best cell there are more vegetob than in the current cell
        if grid[0, cell[0], cell[1]] < len(self.population) and \
            grid[0, cell[0], cell[1]] < grid[0, best_cell[0], best_cell[1]]:
            # THE HERD WILL MOVE
            # The Erbast with low social attitude and low energy will stay in the current cell
            move_erbast = [erbast for erbast in self.population if \
                           erbast.energy * erbast.social_attitude >= const.MIN_MOVEMENT_E and
                           erbast.energy > 1]
                
            stay_erbast = [erbast for erbast in self.population if \
                           erbast.energy * erbast.social_attitude < const.MIN_MOVEMENT_E or 
                           erbast.energy <= 1]
            
        else:
            # THE HERD WILL NOT MOVE
            # The Erbast with low social attitude and high energy will move
            move_erbast = [erbast for erbast in self.population if \
                           erbast.energy / erbast.social_attitude > const.MAX_MOVEMENT_E and
                           erbast.energy > 1]
            
            stay_erbast = [erbast for erbast in self.population if \
                           erbast.energy / erbast.social_attitude <= const.MAX_MOVEMENT_E or 
                           erbast.energy <= 1]
                
        #### update value
        for erbast in move_erbast:
            erbast.moved = True
            erbast.energy -= 1
        for erbast in stay_erbast:
            erbast.moved = False
            
        # craete a new herd
        other_herd = Herd()
        # update the attributes population 
        self.population = stay_erbast         # the Erbast that didn't moved
        other_herd.population = move_erbast   # the Erbast that moved
        res_herds = [(self, cell), (other_herd, best_cell)]  # add the resulting herds to the list res_herds
        # remove the herds that are empty
        res_herds = [herd_cell for herd_cell in res_herds if len(herd_cell[0].population) > 0]
        # RETURN A LIST OF TUPLES (one for each herd)
        # THE FIRST ELEMENT OF THE TUPLE IS THE HERD, THE SECOND IS THE CELL
        return res_herds
    
    def unify(self, herd_list):
        """ 
        Unify the herds that are present in the same cell.
        If the number of Erbast after the merge is greater then MAX_HERD, a part of the population dies of overpopulation.
        The herds doesn't have the option of fighting with each order (unlike the prides)
                
        Parameters
        ----------
        herd_list : list
            List of the Erbast that are present in the current cell.
        """
        return super().join_groups(herd_list, Herd(), const.MAX_HERD)
    
    def grazing(self, grid, cell):
        """
        The Erbast that did not move, can graze to increment their Energy. The grazing decreases the
        Vegetob density of the cell. Every Erbast can have 1 point of Energy for 1 point of Vegetob
        density. If the Vegetob density is lower than the number of Erbast, 1 point is assigned to those
        Erbast having the lowest value of Energy, up to exhaustion of the Vegetob of the cell.
        The Social attitude of those individuals that did not eat (due to lack of Vegetob) is decreased.
        
        Returns
        -------
        grid : ndarray
            The grid, updated with the addition of the new Animals.
        """  
        # create two sublist:
        # moved_erbast : contains the Erbast that won't graze (they moved today)
        # static_erbast : contains the Erbast that will graze (they don't moved today)
        moved_erbast = [erbast for erbast in self.population if erbast.moved]
        static_erbast = [erbast for erbast in self.population if not erbast.moved]
       
        # if there is Vegetob for each static_erbast
        if grid[0, cell[0], cell[1]] >= len(static_erbast):
            for erbast in static_erbast:
                erbast.energy += 1
            # update Vegetob, decrease by the number of erbast that have eaten
            grid[0, cell[0], cell[1]] -= len(static_erbast)
        # if there are more static_erbast than Vegetob
        else:
            # sort the Erbast in the herd by energy (increasing)
            static_erbast.sort(key=lambda erbast: erbast.energy)
            # until there are Vegetob, the Erbast graze
            for n in range(grid[0, cell[0], cell[1]]):
                static_erbast[n].energy += 1
            # when the Vegetob are finished, the social atittude of the remaining Erbast is decreased
            for n in range(grid[0, cell[0], cell[1]], len(static_erbast)):
                # decrease social attitude
                static_erbast[n].social_attitude /= const.HUNGER_E
            # update Vegetob, in this case all the Vegetob have been eaten
            grid[0, cell[0], cell[1]] = 0
        # reassign the complete list of Erbast to the Herd
        self.population = moved_erbast + static_erbast
        return grid # the updated grid
 
    def spawning(self, grid, cell):
        """
        We use inheritance for specifying different constants for Erbast and Carviz
        Erbast : idx_specie = 1
        AGING_E, MIN_LIFE_E, MAX_LIFE_E, MAX_HERD
        """
        return super().spawning(grid, cell, idx_specie=1, \
                                AGING=const.AGING_E,       MIN_LIFE=const.MIN_LIFE_E, \
                                MAX_LIFE=const.MAX_LIFE_E, MAX_GROUP=const.MAX_HERD)
          
    def create_animal(self, energy, lifetime, social_attitude, age=0):
        """
        Create an Erbast

        Parameters
        ----------
        energy : int
        lifetime : int
        social_attitude : float
        age : int, optional

        Returns
        -------
        Erbast
        """
        return Erbast(energy, lifetime, social_attitude, age)

       
              
class Pride(Group):
    def __init__(self):
        super().__init__()
        
    def world_init(self, grid, cell):
        """
        We use inheritance for specifying different constants for Erbast and Carviz
        Carviz : idx_specie = 2
        NUM_CARVIZ_LB, NUM_CARVIZ_UB, MAX_ENERGY_C, MAX_LIFE_C
        """
        return super().world_init(grid, cell,idx_specie=2, \
                                  NUM_ANIMALS_LB=const.NUM_CARVIZ_LB, NUM_ANIMALS_UB=const.NUM_CARVIZ_UB, \
                                  MAX_ENERGY=const.MAX_ENERGY_C,      MAX_LIFE=const.MAX_LIFE_C)
    
    def movement(self, grid, cell, neighbours):
        """
        The pride decides whether to move or not, and the Carviz present in the group
        choose whether to follow the herd or separate.
        
        The most appealing cell in the neighborhood is identified (the one with more nutrients). 
        Once the pride of the cell made a decision (stay or move), the individuals can choose
        if they will follow the social group or made a different decision, splitting by the social group.
        Splitting decision can be formed considering the properties of the individual (e.g., the pride will
        move, while the individual having a low value of energy may stay; or, on the contrary, the pride
        will stay, but strong Erbast may want to move, due to the lack of Vegetob in the cell) and is weighted
        with the social attitude of the individual. The movement costs to each Carviz one point of Energy.
        
        Parameters
        ----------
        grid : ndarray
        cell : tuple
            The cell in which is present the pride.
        neighbours : list
            List of the neighbours cells to our cell in analisys.

        Returns
        -------
        res_prides : list
            list with 2 prides (2 if some animals have separated from the pride).
        """
        
        # I need only one erbast in the cell, not as much as erbast as the number of carviz (different from erbast-vegetob)
        # sort the neighbours cell by decreasing (reverse=True) value of Erbast (nutrients)
        neighbours.sort(key=lambda cell: grid[1, cell[0], cell[1]], reverse=True)
        if len(neighbours) != 0:        # check if there is any neighbour
            best_cell = neighbours[0]   # pick the first cell in the list, which is the most suitable one
            if grid[1, best_cell[0], best_cell[1]] == 0: # If there isn't any Erbast, just go in a random cell
                best_cell = random.choice(neighbours)
        else: 
            return [(self, cell)]       # if I don't have any neighbour I don't move
             
        # move_carviz = list()   # res of the movement, Carviz that moved
        # stay_carviz = list()   # res of the movement, Carviz that didn't moved
        # decide if the group will move or not:
        # they move if : in the current cell there aren't any Erbast
        if grid[1, cell[0], cell[1]] == 0 :
            # THE PRIDE WILL MOVE
            # The Carviz with low social attitude and low energy will stay in the current cell
            stay_carviz = [carviz for carviz in self.population if \
                           carviz.energy * carviz.social_attitude < const.MIN_MOVEMENT_C or
                           carviz.energy <= 1] 
            move_carviz = [carviz for carviz in self.population if \
                           carviz.energy * carviz.social_attitude >= const.MIN_MOVEMENT_C and
                           carviz.energy > 1]
            
        else:
            # THE PRIDE WILL NOT MOVE
            # The Carviz with low social attitude and high energy will move
            stay_carviz = [carviz for carviz in self.population if \
                           carviz.energy / carviz.social_attitude > const.MAX_MOVEMENT_C or
                           carviz.energy <= 1]
            move_carviz = [carviz for carviz in self.population if \
                           carviz.energy / carviz.social_attitude <= const.MAX_MOVEMENT_C and
                           carviz.energy > 1]
            
        for carviz in move_carviz:
            carviz.moved = True
            carviz.energy -= 1
            
        for carviz in stay_carviz:
            carviz.moved = False   
          
        # craete a new pride
        other_pride = Pride()
        # update the attributes population
        self.population = stay_carviz                # the Carviz that didn't moved
        other_pride.population = move_carviz         # the Carviz that moved
        res_prides = [(self, cell), (other_pride, best_cell)]  # add the resulting herds to the list res_herds
        # remove the prides that are empty
        res_prides = [pride_cell for pride_cell in res_prides if len(pride_cell[0].population) > 0]
        # RETURN A LIST OF TUPLES (one for each pride)
        # THE FIRST ELEMENT OF THE TUPLE IS THE PRIDE, THE SECOND IS THE CELL
        return res_prides
    
    def unify(self, pride_list):
        """ 
        Unify the prides that are present in the same cell.
        A pride can choose to fight or to join with another pride. In the end only one pride will remain standing.
        The fight between two prides is a last-blood match. In its simplest form, a random number is
        drawn and each pride has a winning probability proportional to the sum of the Energy on its
        components. If two prides fight, the social_attitude of the winning pride is increased.
                        
        Parameters
        ----------
        pride_list : list
            List of the Carviz that are present in the current cell.
        """

        # we join/fight them one by one, starting from the less populated, until only one pride remain 
        while len(pride_list) > 1: # until we have only one pride
            # reorder the list with the prides by increasing number of carviz present in each pride 
            pride_list.sort(key=lambda pride: len(pride.population))
            pride1 = pride_list[0] # first pride
            pride2 = pride_list[1] # second pride
            pride1.update_stats()  # update stats (in particular for total_social_attitude and total_energy)
            pride2.update_stats()  # update stats (in particular for total_social_attitude and total_energy)
            # If the sum of the total_social_attitude is enough and the sum of the number of animals 
            # is not higher then MAX_PRIDE, the prides are joined
            if pride1.total_social_attitude + pride2.total_social_attitude > const.JOIN_PRIDE and \
                len(pride1.population) + len(pride2.population) < const.MAX_PRIDE:
                # [joined pride1, pride2] + the remaining prides
                pride_list = [super().join_groups([pride1, pride2], Pride(), const.MAX_PRIDE)] + pride_list[2:]
            else:
                pride1_fight_value = random.randint(0, pride1.total_energy)
                pride2_fight_value = random.randint(0, pride2.total_energy)
                if pride1_fight_value >= pride2_fight_value: # if pride1 win
                    # increase the social_attitude of the components of the winning pride
                    for carviz in pride1.population:
                        carviz.social_attitude = min(carviz.social_attitude + const.WIN_FIGHT, 1)
                    pride_list = [pride1] + pride_list[2:] # update the list of the pride
                else: # if pride2 win
                    # increase the social_attitude of the components of the winning pride
                    for carviz in pride2.population:
                        carviz.social_attitude = min(carviz.social_attitude + const.WIN_FIGHT, 1)
                    pride_list = [pride2] + pride_list[2:] # update the list of the pride
        # we return the final pride         
        return pride_list[0]
    
    def hunting(self, grid, cell, hunted_herd):
        """
        When only one pride is present in the cell, a hunt takes place. The pride identifies the stronger
        Erbast in the cell and combat with him. The prey is always took down. No Energy consumption for 
        the pride. the Energy of the prey is shared by the pride individuals, increasing their
        energy value (spare energy points are assigned to the Carviz with the lowest Energy).

        Parameters
        ----------
        grid : ndarray
        cell : tuple
            The cell in which is present the pride..
        hunted_herd : Herd or None
            Is the herd present in the cell, have as value "None" if there isn't any herd in the current cell.

        Returns
        -------
        grid : ndarray
            The grid, updated with the removal of the hunted Erbast.
        """
        if hunted_herd == None: # if there isn't any herd
            for carviz in self.population:
                carviz.social_attitude /= const.HUNGER_C
            return grid
        else: # if there is a herd
            # sort the Erbast by decreasing (reverse=True) energy
            hunted_herd.population.sort(key=lambda erbast: erbast.energy, reverse=True)
            # remove the strongest Erbast, because is hunted by the pride, and collect its energy
            gained_energy = hunted_herd.population.pop(0).energy
            # sort the Carviz by increasing energy
            self.population.sort(key=lambda carviz: carviz.energy)
            energy_per_carviz = gained_energy // len(self.population) # min energy for each carviz
            spare_energy = gained_energy % len(self.population)       # number of carviz that gain one point more
            for n in range(spare_energy): # to the weaker Carviz give the spare energy
                # increase energy up to a maximum of MAX_ENERGY_C
                self.population[n].energy = min(self.population[n].energy + energy_per_carviz + 1, const.MAX_ENERGY_C)
                self.population[n].social_attitude += const.EAT_C   # increase social attitude 
            for n in range(spare_energy, len(self.population)):     # add the normal amount to all the other
                # increase energy up to a maximum of MAX_ENERGY_C
                self.population[n].energy = min(self.population[n].energy + energy_per_carviz, const.MAX_ENERGY_C)    
                self.population[n].social_attitude += const.EAT_C   # increase social attitude
            grid[1, cell[0], cell[1]] -= 1 # update the grid
            return grid
            
    def spawning(self, grid, cell):
        """
        We use inheritance for specifying different constants for Erbast and Carviz
        Carviz : idx_specie = 2
        AGING_C, MIN_LIFE_C, MAX_LIFE_C, MAX_PRIDE
        """
        return super().spawning(grid, cell, idx_specie=1, \
                                AGING=const.AGING_C,       MIN_LIFE=const.MIN_LIFE_C, \
                                MAX_LIFE=const.MAX_LIFE_C, MAX_GROUP=const.MAX_PRIDE)
                
    def create_animal(self, energy, lifetime, social_attitude, age=0):
        """
        Create a Carviz

        Parameters
        ----------
        energy : int
        lifetime : int
        social_attitude : float
        age : int, optional

        Returns
        -------
        Carviz
        """
        return Carviz(energy, lifetime, social_attitude, age)
    
    
    
# --------------------------------------------------------------------------------------------------------------------- # 
# The Planisuss World
# --------------------------------------------------------------------------------------------------------------------- #     
class World:
    """
    Rapresent the Planisuss World, which is populated by:
    
    - Vegetob (pl. Vegetob) is a vegetable species. Spontaneously grows on the ground with a regular
    cycle. Vegetob is the nutrient of Erbast.
    
    - Erbast (pl. Erbast) is a herbivore species. Erbast eat Vegetob. They can move on the continent
    to find better living conditions. Individuals can group together, forming a herd.
    
    - Carviz (pl. Carviz) is a carnivore species. Carviz predate Erbast. They can move on the
    continent to find better living conditions. Individuals can group together, forming a pride.
    """
    
    def __init__(self):
        """ 
        grid : ndarray  
            3Dimensional array, with dimension: 3 X NUMCELLS_R X NUMCELLS_C
            Where NUMCELLS_R X NUMCELLS_C consist of the actual planar region of the world
            and in the three depth we have:
                - [0, i, j] rapresent the continent and the densitiy of Vegetob:
                    ==> -100 = water
                    ==> a value in [0, 100] = ground, with the corresponding density of vegetobs
                - [1, i, j] contains the number of Erbast in each cell
                - [2, i, j] contains the number of Carviz in each cell
        
        herds : dictionary 
                - as KEY a tuple (i, j) that rapresent the cell with coordinates (i, j)
                - as VALUE a objects of type Herd, herd.population is a list of the erbast in the cell
            Only the keys that are actually occupied are initialized (not every cell)
            
        prides : dictionary 
                - as KEY a tuple (i, j) that rapresent the cell with coordinates (i, j)
                - as VALUE a objects of type Pride, pride.population is a list of the carviz in the cell
            Only the keys that are actually occupied are initialized (not every cell)
                
        ground_cells : list
                a list of tuples (i, j), that corresponds to the cells with the ground
        """

        self.NR = const.NUMCELLS_R                                  # number of rows of self.grid
        self.NC = const.NUMCELLS_C                                  # number of columns of self.grid
        self.WATER_PROB = const.WATER_PROB                          # probability of water in the grid
        self.grid = np.zeros((3, self.NR, self.NC), dtype='int')    # the grid 3 X NR X NC
        self.day = 1                                                # days of the simulation
        self.ground_cells = list()      # list of cells filled with ground, 0 <= grid[0, i, j] <= 100       
        self.n_ground_cells = 0         # number of cells filled with ground
        self.herds = dict()             # dict with keys the cells and values the Herds
        self.prides = dict()            # dict with keys the cells and values the Prides
        
        # axis data for visualizing the plot
        self.time_data = list()
        self.erbast_population_data = list()
        self.carviz_population_data = list()
        self.vegetob_density_data = list()
        self.erbast_energy_data = list()
        self.erbast_lifetime_data = list()
        self.erbast_age_data = list()
        self.erbast_social_attitude_data = list()
        self.carviz_energy_data = list()
        self.carviz_lifetime_data = list()
        self.carviz_age_data = list()
        self.carviz_social_attitude_data = list()
        
        # fill the grid (create the continent)
        for i in range(1, self.NR - 1):     # Don't fill the first and the last row
            for j in range(1, self.NC - 1): # Don't fill the first and the last column
                if random.random() <= self.WATER_PROB:
                    self.grid[0, i, j] = -100  # Water
                else:
                    n_vegetobs = random.randint(0, 100)
                    self.grid[0, i, j] = n_vegetobs
                    # I add only the cells with the ground
                    self.ground_cells.append((i, j))
        # Water at the boundary
        self.grid[0, 0, :] = -100
        self.grid[0, -1, :] = -100
        self.grid[0, :, 0] = -100
        self.grid[0, :, -1] = -100
        
        self.n_ground_cells = len(self.ground_cells)

        ##### self.herds and self.prides #####
        # Initialize only the keys (i, j) that are filled with animals (not every cell)       
        # HERDS : fill the dictionary self.herds
        occupied_cells = set() # so that I don't spawn two herds in one cell
        num_herds = random.randint(const.NUM_HERDS_LB, const.NUM_HERDS_UB) # random number of herds
        for n in range(num_herds):
            # choose a random cell (not one already occupied)
            cell = random.choice(list(filter(lambda x: x not in occupied_cells, self.ground_cells)))
            occupied_cells.add(cell)
            # Create the Herd, the Erbast present in it and update the grid
            new_herd = Herd()
            self.grid = new_herd.world_init(self.grid, cell)
            self.herds[cell] = new_herd # save the herd in the dictionary
        # PRIDES : fill the dictionary self.prides
        occupied_cells = set() # so that I don't spawn two prides in one cell
        num_prides = random.randint(const.NUM_PRIDES_LB, const.NUM_PRIDES_UB) # random number of prides
        for n in range(num_prides):
            # choose a random cell (not one already occupied)
            cell = random.choice(list(filter(lambda x: x not in occupied_cells, self.ground_cells)))
            occupied_cells.add(cell)
            # Create the Pride, the Carviz present in it and update the grid
            new_pride = Pride()
            self.grid = new_pride.world_init(self.grid, cell)
            self.prides[cell] = new_pride # save the pride in the dictionary
   
    def a_day_on_planysuss(self):
        """
        Update function
        """
        self.growing()
        self.overwhelming()
        self.movement()
        self.unify_groups()
        self.grazing()
        self.hunting()
        self.spawning()
        
        self.remove_empty_groups()
        self.update_stats()
        self.day += 1
        
      
    ###########################################################################
    # PHASES OF A DAY
    ###########################################################################
    def growing(self):
        """
        The Vegetob density is increased by GROWING (up to a maximum of 100).
        """
        # cell = (i, j)
        for i, j in self.ground_cells:
            self.grid[0, i, j] = min(self.grid[0, i, j] + const.GROWING, 100)
    
    def overwhelming(self):
        """
        If a cell is completely surrounded by cells having the maximum Vegetob density, 
        the animals present in the cell are overwhelmed by the Vegetob and terminated.
        """
        # herds that will be overwhelmed
        remove_herds = list()
        # set of cells with a Herd
        for i, j in self.herds.keys():
            # reduce(lambda acc, iter : function, iterable, initial value of acc)
            # y : iterate over the list of neighbours (self.neighbourhood(i, j, 1))
            # x : acc start from 0, and at each iteration I sum the Vegetob of the neighbor cells
            sum_vegetob = reduce(lambda x, y: x + self.grid[0, y[0], y[1]], self.neighbourhood(i, j, 1), 0)
            # if each of the 8 neighbours have 100 of Vegetob, I terminate the animals
            if sum_vegetob == 800:
                remove_herds.append((i, j))
                self.grid[1, i, j] = 0
        for cell in remove_herds:
            del self.herds[cell]
         
        # herds that will be overwhelmed
        remove_prides = list()
        # set of cells with a Pride (same as before)
        for i, j in self.prides.keys():
            sum_vegetob = reduce(lambda x, y: x + self.grid[0, y[0], y[1]], self.neighbourhood(i, j, 1), 0)
            # if each of the 8 neighbours have 100 of Vegetob, I terminate the animals
            if sum_vegetob == 800:
                remove_prides.append((i, j))
                self.grid[2, i, j] = 0
        for cell in remove_prides:
            del self.prides[cell]

    def movement(self):
        """
        In the Movement phase, individuals and social groups evaluate the possibility to move in another
        cell. All the Erbast in a cell at the beginning of the day form a herd. Similarly, all the Carviz 
        in a cell constitute a pride. 
        Once the herd and the pride of the cell made a decision (stay or move), the individuals can choose
        if they will follow the social group or made a different decision, splitting by the social group.
        Movements take place for all the cells at the same time and are instantaneous.
        
        After the movement self.herds and self.prides can have more than one group in some cell,
        ex:  self.herds = { (cell1):[herd1, herd2], (cell2):[herd1]...}
        the structure will go back to the usual one ( cell : herd ) after the unify_groups phase
        """
        # HERDS
        res_herds = dict() # here I will store the results of the movement
        # self.herds = [(cell1, herd1), ...], herd.population = [Erbast1, Erbast2,...]
        for cell, herd in self.herds.items():
            neighbours = self.neighbourhood(cell[0], cell[1], const.NEIGHBORHOOD_E)
            # MOVEMENT DECISION OF THE HERD
            after_movement_herds = herd.movement(self.grid, cell, neighbours)
            # update self.herds
            for new_herd_cell in after_movement_herds:
                # new_herd_cell = (Herd, cell) tuple
                new_cell = new_herd_cell[1]
                # I use the get method, because I don't know if this cell is already occupied by another herd
                res_herds[new_cell] = res_herds.get(new_cell, list()) + [new_herd_cell[0]]
        self.herds = res_herds # save the result
        
        # PRIDES
        res_prides = dict() # here I will store the results of the movement
        # self.herds = [(cell1, herd1), ...], pride.population = [Erbast1, Erbast2,...]
        for cell, pride in self.prides.items():
            neighbours = self.neighbourhood(cell[0], cell[1], const.NEIGHBORHOOD_C)
            # MOVEMENT DECISION OF THE PRIDE
            after_movement_prides = pride.movement(self.grid, cell, neighbours)
            # update self.prides
            for new_pride_cell in after_movement_prides:
                # new_pride_cell = (Pride, cell) tuple
                new_cell = new_pride_cell[1]
                # I use the get method, because I don't know if this cell is already occupied by another pride
                res_prides[new_cell] = res_prides.get(new_cell, list()) + [new_pride_cell[0]]
        self.prides = res_prides # save the result
            
    def unify_groups(self):
        """ 
        Unify the groups that are present in the same cell.
        """
        # for every list of herd, the herds present in it are joined
        for cell, herd_list in self.herds.items():
            self.herds[cell] = herd_list[0].unify(herd_list) # I apply the unify method to the first herd
        # for every list of pride, the prides decide if they fight or simply join
        for cell, pride_list in self.prides.items():
            self.prides[cell] = pride_list[0].unify(pride_list) # I apply the unify method to the first pride
               
        # UPDATE THE GRID
        self.update_grid()
            
    def grazing(self):
        """
        Apply the grazing method to each Herd and Pride, and update the grid
        """
        # For each Herd : apply the grazing method on the Herd, and update the grid 
        for cell, herd in self.herds.items():
            self.grid = herd.grazing(self.grid, cell)
            
    def hunting(self):
        """
        Apply the hunting method to each Pride, and update the grid
        """
        # For each pride
        for cell, pride in self.prides.items():
            # take the herd in the cell, or None if there isn't any herd
            hunted_herd = self.herds.get(cell, None)
            # run the hunting method and update the grid
            self.grid = pride.hunting(self.grid, cell, hunted_herd)
            
    def spawning(self):
        """
        Apply the spawning method to each Herd and Pride, and update the grid
        """
        # For each Herd : apply the spawning method on the Herd, and update the grid
        for cell, herd in self.herds.items():
            self.grid = herd.spawning(self.grid, cell)
        # for each Pride : apply the spawning method on the Pride, and update the grid
        for cell, pride in self.prides.items():
            self.grid = pride.spawning(self.grid, cell)
    
    ###########################################################################
    # UTILITIES
    ###########################################################################
    def update_grid(self):
        """
        Count the number of Erbast and Carviz, and update the grid.
        The vegetob are already updated during growing and grazing.
        """
        def accumulate_animals(acc_layer, item):
            cell, group = item
            acc_layer[cell[0], cell[1]] += len(group.population)
            return acc_layer
           
        erbast_layer = np.zeros((self.NR, self.NC), dtype='int')
        # Use reduce to accumulate population counts into erbast_layer
        self.grid[1] = reduce(accumulate_animals, self.herds.items(), erbast_layer)

        carviz_layer = np.zeros((self.NR, self.NC), dtype='int')
        # Use reduce to accumulate population counts into carviz_layer
        self.grid[2] = reduce(accumulate_animals, self.prides.items(), carviz_layer)
            
    def update_stats(self):
        """
        Update the attributes total_energy, total_lifetime, total_age and total_social_attitude
        of each herd and pride.
        """
        # GROUPS STATS
        # update stats of each Erbast
        for herd in self.herds.values():
            herd.update_stats()
        # update stats of each Pride
        for pride in self.prides.values():
            pride.update_stats()
        
        # update the grid
        erbast_grid = np.zeros((self.NR, self.NC), dtype='int')
        carviz_grid = np.zeros((self.NR, self.NC), dtype='int')
        for cell, herd in self.herds.items():
            erbast_grid[cell[0], cell[1]] = len(herd.population)
        for cell, pride in self.prides.items():
            carviz_grid[cell[0], cell[1]] = len(pride.population)
        self.grid[1] = erbast_grid
        self.grid[2] = carviz_grid
        
        # WORLD STATS FOR PLOT VISUALIZATION
        # ERBAST AND CARVIZ POPULATION
        # Update the total population subplot
        self.time_data.append(self.day)  # Append the current time frame
        tot_erbast = np.sum(self.grid[1])
        tot_carviz = np.sum(self.grid[2])
        self.erbast_population_data.append(tot_erbast)
        self.carviz_population_data.append(tot_carviz)
        
        # MEAN VEGETOB DENSITY HISTO
        # Filter out elements less than 0, take only the vegetob, no water
        filtered_vegetob = self.grid[0][self.grid[0] >= 0]
        # Convert the filtered matrix into a Python list
        self.vegetob_density_data = filtered_vegetob.tolist()
        
        # TOTAL ENERGY, MEAN SOCIAL ATTITUDE, MEAN LIFETIME AND MEAN AGE
        # x = (enrgy, lifetime, age, social_attitude)
        # y = each herd and pride
        if tot_erbast > 0:
            total_stats_herds = reduce(lambda x, y: x + np.array((y.total_energy, y.total_lifetime, y.total_age, y.total_social_attitude)), \
                                   self.herds.values(), np.array((0, 0, 0, 0)))
            self.erbast_energy_data.append(total_stats_herds[0])      
            self.erbast_lifetime_data.append(total_stats_herds[1] / tot_erbast)      
            self.erbast_age_data.append(total_stats_herds[2] / tot_erbast)
            self.erbast_social_attitude_data.append(total_stats_herds[3] / tot_erbast)
        else:
            # if there is no Erbast remaining just put 0
            self.erbast_energy_data.append(0)      
            self.erbast_lifetime_data.append(0)      
            self.erbast_age_data.append(0)
            self.erbast_social_attitude_data.append(0)

        if tot_carviz > 0:
            total_stats_prides = reduce(lambda x, y: x + np.array((y.total_energy, y.total_lifetime, y.total_age, y.total_social_attitude)), \
                                       self.prides.values(), np.array((0, 0, 0, 0))) 
            self.carviz_energy_data.append(total_stats_prides[0])      
            self.carviz_lifetime_data.append(total_stats_prides[1] / tot_carviz)      
            self.carviz_age_data.append(total_stats_prides[2] / tot_carviz)
            self.carviz_social_attitude_data.append(total_stats_prides[3] / tot_carviz)
        else:
            # if there is no Carviz remaining just put 0
            self.carviz_energy_data.append(0)      
            self.carviz_lifetime_data.append(0)      
            self.carviz_age_data.append(0)
            self.carviz_social_attitude_data.append(0)
            
    def remove_empty_groups(self):
        """
        Remove the herds and prides that have no animals present in it, due to
        aging or hunting (for the herds).
        I run it before of updating stats, because I divide by the number of animals
        for computing the mean, which raises an error if the number of animals is 0.
        """
        remove_herds = list() 
        for cell, herd in self.herds.items(): # HERDS
            if len(herd.population) == 0:
                remove_herds.append(cell) # save the herds that we have to remove
        for cell in remove_herds:
            del self.herds[cell]
           
        remove_prides = list() 
        for cell, pride in self.prides.items(): # PRIDES
            if len(pride.population) == 0:
                remove_prides.append(cell) # save the prides that we have to remove
        for cell in remove_prides:
            del self.prides[cell]
                        
    def neighbourhood(self, cell_row, cell_col, radius):
        """
        A function that gives the list of the cells neighbours of my cell
        with coordinates (cell_row, cell_col), within the distance radius

        Parameters
        ----------
        cell_row : int
            the row of the analized cell.
        cell_col : int
            the column of the analized cell.
        radius : int
            radius of the region that a social group can evaluate to decide the movement.
            (radius = 1 if we use neighbourhood() in overwhelming())

        Returns
        -------
        list
            list of tuples (i, j) within the distance 'radius' from my cell
            (only the ground cells are saved).
        """
        neighbourhood = list()
        # explore the grid along the rows
        # use max and min, so that I don't go outside the grid
        for i in range(max(0, cell_row - radius), min(cell_row + radius + 1, self.NR)):
            for j in range(max(0, cell_col - radius), min(cell_col + radius + 1, self.NC)):
                # if (i, j) is a ground cell, I save it
                if (i, j) in self.ground_cells and (i, j) != (cell_row, cell_col): # I don't count my cell
                    neighbourhood.append((i, j))
        return neighbourhood



# --------------------------------------------------------------------------------------------------------------------- # 
# Simulation of the World
# --------------------------------------------------------------------------------------------------------------------- #     
class Simulation:
    """
    Rapresent the simulation of a World. Here we have everything regardings the figure display and interactivity.
    """
    def __init__(self):
        """
        Initializa a World object and everything that is useful for the visualization.
        for example the figure, the axis, the animation and connect the interactive functions,
        and also useful variables like 'flag', 'pause', 'zoom_row' and 'zoom_col'.
        """
        self.world = World()     # a World object, the Planysuss
        self.pause = False       # tell if the visualization is in play/pause
        self.flag = 'Planysuss'  # tell what we want to visualize
        self.zoom_row = None     # row coordinate of the centre of the zoomed area
        self.zoom_col = None     # col coordinate of the centre of the zoomed area
    
        
        self.fig = plt.figure(constrained_layout=False) # Create a figure
        
        # LAYOUT AND AXIS
        # Create a grid layout with different-sized subplots
        # number of rows, columns, and the relative sizes of the subplots
        self.gs_background = self.fig.add_gridspec(nrows=1, ncols=1,
                                                   left=0, right=1,
                                                   top=1, bottom=0)
        self.ax_background = self.fig.add_subplot(self.gs_background[:, :])
        
        # left part of the figure : grid, zoomed_grid and table
        self.gs1 = self.fig.add_gridspec(nrows=3, ncols=3,
                                         left=0.03, right=0.45, wspace=0.01,
                                         top=0.95, bottom=0.05)
        self.ax = self.fig.add_subplot(self.gs1[:-1, :])
        self.zoomed_ax = self.fig.add_subplot(self.gs1[-1, 0])
        self.table_ax = self.fig.add_subplot(self.gs1[-1, 1:])

        # right part of the figure : plots
        self.gs2 = self.fig.add_gridspec(nrows=4, ncols=2,
                                         left=0.5, right=0.97, hspace=0.25, wspace=0.25,
                                         top=0.95, bottom=0.05)
        self.plot_population_ax = self.fig.add_subplot(self.gs2[0, :])
        self.plot_vegetob_ax = self.fig.add_subplot(self.gs2[1, :])
        self.plot_age_ax  = self.fig.add_subplot(self.gs2[2, :])
        self.plot_energy_ax = self.fig.add_subplot(self.gs2[3, 0])
        self.plot_social_attitude_ax = self.fig.add_subplot(self.gs2[3, -1])

        # Disable axis labels and ticks
        self.ax_background.axis('off')
        self.ax.axis('off')
        self.zoomed_ax.axis('off')
        self.table_ax.axis('off') 
        
        # PLOTS
        self.create_plots()
        
        # TABLE
        self.row_labels = ['t_population', 't_energy', 'm_lifetime', 'm_age', 'm_s.attitude']
        self.col_labels = ['', 'Erbast', 'Carviz', 'Vegetob']
        self.create_table() # Create the initial table

        # INTERACTIVITY
        self.cid1 = self.fig.canvas.mpl_connect('button_press_event', self.onClick) # mouse interactivity
        self.cid2 = self.fig.canvas.mpl_connect('key_press_event', self.onKey)      # keyboard interactivity
        self.cid3 = self.fig.canvas.mpl_connect('close_event', self.onClose)        # onClose function
        
        # ANIMATION
        self.ani = FuncAnimation(self.fig, self.update, frames=const.NUMDAYS, repeat=False, interval=1, blit=True)  # Create the animation
        
        plt.show()
    
    
    def update(self, frame):
        """
        Update the animation, consist on updating the world and display it when 'pause' is False.
        If 'pause' is True we wait for a buttom to be pressed, until then the simulation is paused.
        """
        if not self.pause:
            self.world.a_day_on_planysuss() # update the world
            self.create_plots()             # update the plots
            self.display()                  # visualize the world
        # return the axes
        return (self.ax_background, self.ax, self.zoomed_ax, self.table_ax, self.plot_population_ax, self.plot_vegetob_ax,
                self.plot_vegetob_ax, self.plot_age_ax, self.plot_energy_ax, self.plot_social_attitude_ax)
        
    
    ###########################################################################
    # VISUALIZATION + INTERACTIVITY
    ###########################################################################
    def display(self):
        """
        Display the simulation, what we will show dependes on the attribute 'flag'
        """
        vegetob = normalize_matrix(self.world.grid[0])
        erbast = normalize_matrix(self.world.grid[1])
        carviz = normalize_matrix(self.world.grid[2])
        
        if self.flag == 'Planysuss':
            planisuss_visualization = np.dstack((carviz, erbast, vegetob))
        elif self.flag == 'Carviz':
            planisuss_visualization = np.dstack((carviz, np.zeros_like(carviz), np.zeros_like(carviz)))
        elif self.flag == 'Erbast':
            planisuss_visualization = np.dstack((np.zeros_like(erbast), erbast, np.zeros_like(erbast)))
        elif self.flag == 'Vegetob':
            planisuss_visualization = np.dstack((np.zeros_like(vegetob), np.zeros_like(vegetob), vegetob))
        
        # GRID
        self.ax.clear()     # Clear the current axis
        self.ax.axis('off') # Disable axis labels and ticks
        self.ax.imshow(planisuss_visualization)
        self.ax.set_title(f'{self.flag} - day {self.world.day}')
        
        # ZOOMED GRID
        if self.zoom_row is not None:
            self.zoomed_ax.clear()
            self.zoomed_ax.axis('off')
            zoom_planisuss_visualization = planisuss_visualization[ \
                                            max(0, self.zoom_row-2):min(self.zoom_row+3, self.world.NR),
                                            max(0, self.zoom_col-2):min(self.zoom_col+3, self.world.NC)]
            
            # Set the extent to match the clicked cell's coordinates
            extent = [max(0, self.zoom_col - 2.5), min(self.zoom_col + 2.5, self.world.NC),
                      min(self.zoom_row + 2.5, self.world.NR), max(0,self.zoom_row - 2.5)]
            # The extent is useful because when I click a cell in the zoomed grid I take the correct x and y
            self.zoomed_ax.imshow(zoom_planisuss_visualization, extent=extent)
            self.zoomed_ax.set_title(f'Zoom cell ({self.zoom_row}, {self.zoom_col})')
        
        self.fig.canvas.draw() 
        
    def resume_animation(self):
        """
        Resume the animation. The method is executed when we press ' ' and pause is False.
        """
        if hasattr(self.ani, 'event_source') and self.ani.event_source is None:
            self.ani.event_source.start()  
            
    def onClick(self, event):
        """
        'button_press_event' interactivity with the simulation (mouse).
        'click' in the visualization of the world: select the cell in which zooming in
        and the cell choosed to be analized in the table.
        
        You can click either in the complete grid, or in the zoomed one        
        """
        x, y = event.x, event.y
        if self.zoomed_ax.contains_point((x, y)) or self.ax.contains_point((x, y)):
            # Calculate the cell coordinates based on the clicked point
            xdata, ydata = event.xdata, event.ydata
            # update the two coordinates
            self.zoom_row = int(ydata + 0.5)  # Convert to integer
            self.zoom_col = int(xdata + 0.5)

            print(f'%s click: button=%d, cell ({self.zoom_row}, {self.zoom_col}) selected' %
                 ('double' if event.dblclick else 'single', event.button))
                    
            self.update_table()        
            self.display()
        else:
            print('%s click: button=%d, clicked outside the planysuss region' %
                 ('double' if event.dblclick else 'single', event.button))

    def onKey(self, event):
        """
        'key_press_event' interactivity with the simulation (keyboard).
        
        - 'escape': close the simulation;
        - ' ': stop the simulation;
        - 'r': visualize only the Carviz on the grid;
        - 'g': visualize only the Erbast on the grid;
        - 'b': visualize only the Vegetob on the grid;
        - 'a': visualize the complete grid;
        - 'u': update manually to the next day (only while pause is True);
        """  
        if event.key == ' ':
            self.pause = not self.pause
            if not self.pause:
                print(f'you pressed {event.key}, the animation is resumed')
                self.resume_animation()
            else:
                print(f'you pressed {event.key}, the animation is paused')
        if event.key == 'r' or event.key == 'R':
            self.flag = 'Carviz'
            print(f'you pressed {event.key}, visualize only the Carviz')
        if event.key == 'g' or event.key == 'G':
            self.flag = 'Erbast'
            print(f'you pressed {event.key}, visualize only the Erbast')
        if event.key == 'b' or event.key == 'B':
            self.flag = 'Vegetob'
            print(f'you pressed {event.key}, visualize only the Vegetob/ground')
        if event.key == 'a' or event.key == 'A':
            self.flag = 'Planysuss'
            print(f'you pressed {event.key}, visualize the complete planysuss')
        if event.key == 'u' or event.key == 'U' and self.pause == True:
            self.world.a_day_on_planysuss() # update the world
            self.display() # visualize the world
            print(f'you pressed {event.key}, the simulation is updated')
        # Update the current frame when I change what I want to visualize
        if event.key in 'rRgGbBaA' and self.pause == True:
            self.display()
        if event.key == 'escape':
            print(f'you pressed {event.key}, the simulation is closed. Thanks for the attention!')
            print("Figure closed.")
            self.close_all()
        
    def onClose(self, event):
        """
        This function will be called when the figure is manually closed.
        Print a message and stop the animation's background processes.
        """
        print("Figure closed.")
        self.close_all()        

    def create_table(self):
        """
        Function to create the table during the initialization.
        """
        data = np.zeros((5, 3), dtype=str).tolist()
        table_data = [[self.row_labels[i]] + data[i] for i in range(len(data))]
        self.table_ax.clear()  # Clear the previous table
        self.table_ax.axis('off') # Disable axis labels and ticks
        self.table = self.table_ax.table(cellText=table_data, loc='center', cellLoc='center', 
                                         colLabels=self.col_labels)
        self.table.auto_set_font_size(False)
        self.table.set_fontsize(10)
        self.table.scale(0.7, 1.257)  # Adjust the table size

        # Adjust the width of the first column
        column_to_widen = 0
        new_width = 1.4  # Adjust this value as needed

        for i in range(len(data) + 1):
            cell = self.table[i, column_to_widen]
            cell.set_width(new_width * cell.get_width())
    
    def update_table(self):
        """
        Function to update the table data.
        In the table we can find total_population, total_energy, mean_lifetime, mean_age, mean_social_attitude 
        of the Herd and Pride present in the clicked cell (if they are present), and the density of vegetob.
        
        The data in the table are updated only after a 'onClick' event, not every day.
        """
        total_vegetob = self.world.grid[0, self.zoom_row, self.zoom_col]
        if total_vegetob == -100:
            new_data = np.zeros((5, 4), dtype=str).tolist()
        else:
            # VEGETOB
            vegetob_row = [str(total_vegetob), '0', '0', '0', '0']
            
            # ERBAST
            if self.world.grid[1, self.zoom_row, self.zoom_col] == 0:
                erbast_row = ['0', '0', '0', '0', '0']
            else:
                herd = self.world.herds[(self.zoom_row, self.zoom_col)]
                total_population = len(herd.population)
                total_energy = str(int(herd.total_energy))    
                mean_lifetime = str(round(herd.total_lifetime / total_population, 1))
                mean_age = str(round(herd.total_age / total_population, 1))
                mean_social_attitude = str(round(herd.total_social_attitude / total_population, 1))
                
                erbast_row = [str(total_population), total_energy, mean_lifetime, mean_age, mean_social_attitude]
            
            # CARVIZ
            if self.world.grid[2, self.zoom_row, self.zoom_col] == 0:
                carviz_row = ['0', '0', '0', '0', '0']
            else:
                pride = self.world.prides[(self.zoom_row, self.zoom_col)]
                total_population = len(pride.population)
                total_energy = str(int(pride.total_energy))    
                mean_lifetime = str(round(pride.total_lifetime / total_population, 1))
                mean_age = str(round(pride.total_age / total_population, 1))
                mean_social_attitude = str(round(pride.total_social_attitude / total_population, 1))
                
                carviz_row = [str(total_population), total_energy, mean_lifetime, mean_age, mean_social_attitude]
                    
            new_data = [self.row_labels, erbast_row, carviz_row, vegetob_row]
            # Transpose the list
            new_data = [[row[i] for row in new_data] for i in range(len(new_data[0]))]
            
        for i in range(len(new_data)):
            for j in range(len(new_data[i])):
                self.table[(i + 1, j)].get_text().set_text(str(new_data[i][j]))

        self.table_ax.set_title(f'Details cell ({self.zoom_row}, {self.zoom_col})')         
                
    def create_plots(self):
        """
        Create the plots
        """
        t = self.world.time_data
        # CARVIZ AND ERBAST POPULATION
        self.plot_population_ax.clear()
        self.erbast_line_p, = self.plot_population_ax.plot(t, self.world.erbast_population_data, label='E', color='green')
        self.carviz_line_p, = self.plot_population_ax.plot(t, self.world.carviz_population_data, label='C', color='red')
        self.plot_population_ax.legend(loc='upper right')
        # self.plot_population_ax.set_title('Species population')
        self.plot_population_ax.set_ylabel('Species population')
        
        # # MEAN VEGETOB DENSITY HISTO
        self.plot_vegetob_ax.clear()
        self.plot_vegetob_ax.hist(self.world.vegetob_density_data, bins=30, color='blue', alpha=0.7, edgecolor='white')
        # self.plot_vegetob_ax.set_title('Mean vegetob density')
        self.plot_vegetob_ax.set_ylabel('Histo vegetob density')
        
        # TOTAL ENERGY
        self.plot_energy_ax.clear()
        self.erbast_line_e, = self.plot_energy_ax.plot(t, self.world.erbast_energy_data, label='E', color='green')
        self.carviz_line_e, = self.plot_energy_ax.plot(t, self.world.carviz_energy_data, label='C', color='red')
        self.plot_energy_ax.legend(loc='upper right')
        # self.plot_energy_ax.set_title('Total energy')
        self.plot_energy_ax.set_ylabel('Total energy')
        
        # MEAN SOCIAL ATTITUDE
        self.plot_social_attitude_ax.clear()
        self.erbast_line_sa, = self.plot_social_attitude_ax.plot(t, self.world.erbast_social_attitude_data, label='E', color='green')
        self.carviz_line_sa, = self.plot_social_attitude_ax.plot(t, self.world.carviz_social_attitude_data, label='C', color='red')
        self.plot_social_attitude_ax.legend(loc='upper right')
        # self.plot_social_attitude_ax.set_title('Mean social attitude')
        self.plot_social_attitude_ax.set_ylabel('Mean social attitude')
         
        # MEAN LIFETIME AND MEAN AGE
        self.plot_age_ax.clear()
        self.erbast_line_l, = self.plot_age_ax.plot(t, self.world.erbast_lifetime_data, label='E_l.time', linestyle='-', color='green')
        self.carviz_line_l, = self.plot_age_ax.plot(t, self.world.carviz_lifetime_data, label='C_l.time', linestyle='-', color='red')
        self.erbast_line_a, = self.plot_age_ax.plot(t, self.world.erbast_age_data, label='E_age', linestyle=':', color='green')
        self.carviz_line_a, = self.plot_age_ax.plot(t, self.world.carviz_age_data, label='C_age', linestyle=':', color='red')
        self.plot_age_ax.legend(loc='upper right')
        # self.plot_age_ax.set_title('Mean age and lifetime')
        self.plot_age_ax.set_ylabel('Mean age and lifetime')

    def close_all(self):
        """
        Stop any activity
        """
        if hasattr(self, 'ani'):
            if hasattr(self.ani, 'event_source') and self.ani.event_source is not None:
                self.ani.event_source.stop()     
        self.fig.canvas.mpl_disconnect(self.cid1)
        self.fig.canvas.mpl_disconnect(self.cid2)
        self.fig.canvas.mpl_disconnect(self.cid3)
        self.ax.clear()
        self.zoomed_ax.clear()
        self.table_ax.clear()
        self.plot_population_ax.clear()
        self.plot_age_ax.clear()
        self.plot_energy_ax.clear()
        self.plot_social_attitude_ax.clear()
        self.plot_vegetob_ax.clear()
        self.fig.clf()
        plt.close()
        del self

def normalize_matrix(data):
    """ 
    Rescale a matrix in [0, 1] 
    The scaling is done with respect to the maximum number of elements of the corresponding
    social group at the given time (np.nanmin(data) and (np.nanmax(data))
    """
    if (np.nanmax(data)-np.nanmin(data)) != 0:
        return (data-np.nanmin(data))/(np.nanmax(data)-np.nanmin(data))
    else:
        return np.zeros_like(data)



if __name__ == '__main__':
    # For visualizing the interactive simulation in Spyder (in the IDLE gives an error)
    try:
        get_ipython().run_line_magic('matplotlib', 'qt')
    except:
        pass
    
    a_simulation = Simulation()
