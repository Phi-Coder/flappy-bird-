import neat
import pygame
import os
import random

# resolution of game window
Window_width = 500
Window_height = 800

# loading images of bird
bird_img = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird1.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird2.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird3.png")))]

# loading images of other parts of the game
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "pipe.png")))
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base.png")))
background_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bg.png")))

# font style of display score
pygame.font.init()
score_font = pygame.font.SysFont("comicsans", 50)


class Bird:
    bird_img = bird_img  # image of bird
    max_rotation = 25  # bird tilt (in degree)
    rot_vel = 20  # rotation on each frame
    animation_time = 5  # frame speed (bird flapping speed )

    def __init__(self, x, y):
        '''starting position '''
        self.x = x  # x coordinate
        self.y = y  # y coordinate

        self.tilt = 0  # initial tilt of bird (i.e levelled )
        self.tick_count = 0  # each frame of bird
        self.vel = 0  # velocity of bird
        self.height = self.y  # height of bird equals to y-coordinate
        self.img_count = 0  # keep track of which bird image is currently showing
        self.img = self.bird_img[0]  # on game starting bird image = 1

    ''' jump function of flappy bird '''

    def jump(self):
        self.vel = -10.5  # negative velocity (i.e up) to jump
        self.tick_count = 0  # account when we last jump
        self.height = self.y  # height equals to y coordinate

    ''' move bird'''

    def move(self):
        self.tick_count += 1  # keeps track how many times it moved after last jump

        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2  # calculating displacement

        # setting terminal velocity
        if d >= 16:
            d = 16
        if d < 0:  # moving upward
            d -= 2  # jump unit

        self.y = self.y + d  # updating y coordinate of bird

        # updating the tilt of the bird
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.max_rotation:
                self.tilt = self.max_rotation
        else:
            if self.tilt > -90:
                self.tilt -= self.rot_vel

    def draw(self, window):
        self.img_count += 1  # keep track of each frame

        if self.img_count < self.animation_time:
            self.img = self.bird_img[0]
        elif self.img_count < self.animation_time * 2:
            self.img = self.bird_img[1]
        elif self.img_count < self.animation_time * 3:
            self.img = self.bird_img[2]
        elif self.img_count < self.animation_time * 4:
            self.img = self.bird_img[1]
        elif self.img_count == self.animation_time * 4 + 1:
            self.img = self.bird_img[1]
            self.img_count = 0

        # tilt of bird if it dies
        if self.tilt <= -80:
            self.img = self.bird_img[1]
            self.img_count = self.animation_time * 2

        # rotate image wrt center of image

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rotated_img, new_rect.topleft)  # blit = draw

    '''get bird image pixels'''

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    gap = 150  # space/gap btw opposite pipes
    pipe_vel = 5

    def __init__(self, x):
        self.x = x
        self.height = 0  # height of pipe

        self.top = 0
        self.bottom = 0
        self.pipe_top = pygame.transform.flip(pipe_img, False,
                                              True)  # flipped image of pipe (pipe image from top) at y axis

        self.pipe_bottom = pipe_img  # normal orientation of pipe

        self.passed = False  # if bird is passed through the pipe or not
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)  # random height
        self.top = self.height - self.pipe_top.get_height()  # top pipe position
        self.bottom = self.height + self.gap  # bottom pipe position

    def move(self):
        self.x -= self.pipe_vel

    def draw(self, window):
        window.blit(self.pipe_top, (self.x, self.top))
        window.blit(self.pipe_bottom, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()

        top_mask = pygame.mask.from_surface(self.pipe_top)  # getting pixel of top pipe using mask
        bottom_mask = pygame.mask.from_surface(self.pipe_bottom)  # getting pixel of bottom pipe using mask

        '''check pixels over each other'''
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)  # point of overlap btw bird and bottom pipe
        top_point = bird_mask.overlap(top_mask, top_offset)  # point of overlap btw bird and bottom pipe

        if top_point or bottom_point:
            return True

        return False


class Base:
    base_vel = 5
    width = base_img.get_width()
    base_img = base_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0  # 1st base image
        self.x2 = self.width  # 2nd base image

    def move(self):
        self.x1 -= self.base_vel  # slowly moving towards left ( out of screen )
        self.x2 -= self.base_vel  # slowly moving left ( in the screen)

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, window):
        window.blit(self.base_img, (self.x1, self.y))  # drawing 1st base img
        window.blit(self.base_img, (self.x2, self.y))  # drawing 2nd base img


def draw_window(window, birds, pipes, base, score):
    window.blit(background_img, (0, 0))
    for pipe in pipes:
        pipe.draw(window)

    text = score_font.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (Window_width - 10 - text.get_width(), 10))

    base.draw(window)
    for bird in birds:
        bird.draw(window)
    pygame.display.update()


def main(genomes, config):
    score = 0

    # neural net and genomes
    nets = []
    ge = []

    ''' for multiple bird'''
    birds = []

    ''' genome(tuple) is (genome, genome_object*) therefore _, g'''
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)  # create feed forward neural net
        nets.append(net)  # entering neural net type to nets for our genome 'g'
        birds.append(Bird(230, 350))  # every bird start at this position
        g.fitness = 0  # initial fitness
        ge.append(g)

    '''for one bird'''
    # bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)]  # list of pipe
    window = pygame.display.set_mode((Window_width, Window_height))
    clock = pygame.time.Clock()  # frame rate

    run = True
    while run:
        clock.tick(40)
        for event in pygame.event.get():  # keep track of all the click, key click etc
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipe_top.get_width():
                pipe_index = 1
        else:  # if no birds left quit game
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1  # fitness to survive

            output = nets[x].activate(
                (bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:  # we only have one output neuron i.e "JUMP"
                bird.jump()

        rem = []
        add_pipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1  # birds that hit the pipe will have lower fitness score

                    # removing that particular bird
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.pipe_top.get_width() < 0:
                rem.append(pipe)
            pipe.move()

        if add_pipe:
            score += 1

            # if bird get through the pipe , increase fitness
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        # checks for the bird hitting the ground + bird hitting at top of screen and removing it from the list/game
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y <= 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(window, birds, pipes, base, score)


def run(config_path):
    # all the subheading/properties are called
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    # setting up the population
    population = neat.Population(config)  # checks fitness of all genomes

    # statistics output of our model
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    print(stats)

    #
    winner = population.run(main, 60)  # (fitness function , no. of generation )


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)  # gives path of current directory to load config file(neat config)
    config_path = os.path.join(local_dir, "neat_config.txt")
    run(config_path)
