import retro
import numpy as np
import cv2
import neat
import pickle

env = retro.make(game = "SonicAndKnuckles3-Genesis", state = "AngelIslandZone.Act1.state")
imgarray = []
xpos_end = 0

resume = True
restore_file = "neat-checkpoint-18"

def eval_genomes(genomes, config):


    for genome_id, genome in genomes:
        ob = env.reset()
        ac = env.action_space.sample()

        inx, iny, inc = env.observation_space.shape

        inx = int(inx/8)
        iny = int(iny/8)

        net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)
        
        current_max_fitness = 0
        fitness_current = 0
        frame = 0
        counter = 0
        xpos = 0
        
        done = False


        while not done:
            
            env.render()
            frame += 1
            ob = cv2.resize(ob, (inx, iny))
            ob = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY)
            ob = np.reshape(ob, (inx,iny))

            imgarray = np.ndarray.flatten(ob)

            nnOutput = net.activate(imgarray)
            
            ob, rew, done, info = env.step(nnOutput)
            
            
            xpos = info['x']
            
            if xpos >= 20000:
                    fitness_current += 10000000
                    done = True
            
            #fitness_current += rew
            fitness_current = info['x'] # just trying
            #print(fitness_current,info['x']) # viewing variables
            if fitness_current > current_max_fitness:
                current_max_fitness = fitness_current
                counter = 0
            else:
                counter += 1
                
            if done or counter == 900:
                done = True
                print(genome_id, fitness_current)
                
            genome.fitness = fitness_current
    
    

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config-feedforward')

if resume == True:
    p = neat.Checkpointer.restore_checkpoint(restore_file)
else:
    p = neat.Population(config)


p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)
p.add_reporter(neat.Checkpointer(1))

winner = p.run(eval_genomes)

with open('winner.pkl', 'wb') as output:
    pickle.dump(winner, output, 1)
