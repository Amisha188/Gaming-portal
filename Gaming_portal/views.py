from django.shortcuts import render
from django.http.response import HttpResponse
from django.http import HttpResponse
from asyncio import events
from http.client import ACCEPTED
from pickle import FALSE
from turtle import position
import pygame
import random
import time
from pygame.locals import *
from django.shortcuts import render,redirect
from tkinter import *
from django.contrib import messages

import Gaming_portal
from .models import Gamers_list

SIZE = 40
BACKGROUNDCOLOR = (110,110,5)

def register(request):
    if(request.method == "POST"):
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        # print(username + password1)
        if password1 == password2:
            if(Gamers_list.objects.filter(name = username).exists()):
                messages.info(request, 'User name is not available')
                return redirect('register')
            elif(Gamers_list.objects.filter(email = email).exists()):
                messages.info(request, 'Email id is already taken')
                return redirect('register')
            else:
                user = Gamers_list()
                user.name = username
                user.password = password1
                user.email = email
                user.save()
                return redirect('login')
        else:
            messages.info(request, 'Password not matching.')
            return redirect('register')
    else:
        return render(request, 'register.html')

def login(request):
    if(request.method == "POST"):
        username = request.POST['username']
        password = request.POST['password']
        if(Gamers_list.objects.filter(name = username).exists() and Gamers_list.objects.filter(password = password).exists()):
            request.session['id'] = (Gamers_list.objects.get(name=username)).id
            request.session['name'] = (Gamers_list.objects.get(name=username)).name
            return render(request,'index.html')
        else:
            messages.info(request, 'Username or Password not matching.')
            return render(request,'login.html')
    else:
        return render(request,'login.html')

def logout(request):
    request.session.pop('id')
    return redirect('/login/')
    
# Create your views here.
def home(request):
    return render(request, 'index.html')

def tetris_game(request):
    
    pygame.font.init()

    screen_width = 800
    screen_height = 700
    play_width = 300 
    play_height = 600 
    block_size = 30

    top_left_x = (screen_width - play_width)/2 +30
    top_left_y = (screen_height - play_height)/2 +30


    S = [['.....',
        '.....',
        '..00.',
        '.00..',
        '.....'],
        ['.....',
        '.0...',
        '.00..',
        '..0..',
        '.....']]

    Z = [['.....',
        '.....',
        '.00..',
        '..00.',
        '.....'],
        ['.....',
        '..0..',
        '.00..',
        '.0...',
        '.....']]

    I = [['..0..',
        '..0..',
        '..0..',
        '..0..',
        '.....'],
        ['.....',
        '0000.',
        '.....',
        '.....',
        '.....']]

    O = [['.....',
            '.....',
            '.00..',
            '.00..',
            '.....']]

    J = [['.....',
        '.0...',
        '.000.',
        '.....',
        '.....'],
        ['.....',
        '.00..',
        '.0...',
        '.0...',
        '.....'],
        ['.....',
        '.000.',
        '...0.',
        '.....',
        '.....'],
        ['.....',
        '..0..',
        '..0..',
        '.00..',
        '.....']]

    L = [['.....',
        '...0.',
        '.000.',
        '.....',
        '.....'],
        ['.....',
        '..0..',
        '..0..',
        '..00.',
        '.....'],
        ['.....',
        '.....',
        '.000.',
        '.0...',
        '.....'],
        ['.....',
        '.00..',
        '..0..',
        '..0..',
        '.....']]

    T = [['.....',
        '..0..',
        '.000.',
        '.....',
        '.....'],
        ['.....',
        '..0..',
        '..00.',
        '..0..',
        '.....'],
        ['.....',
            '.....',
            '.000.',
            '..0..',
            '.....'],
            ['.....',
            '..0..',
            '.00..',
            '..0..',
            '.....']]

    shapes = [S, Z, I, O, J, L, T]
    shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0),
                    (0, 0, 255), (128, 0, 128)]

    class Piece(object):
        def __init__(self, x, y, shape):
            self.x = x
            self.y = y
            self.shape = shape
            self.color = shape_colors[shapes.index(shape)]
            self.rotation = 0

    def create_grid(locked_pos = {}):
        grid = [[(0,0,0)for x in range(10)] for x in range(20)]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if(j,i) in locked_pos:
                    c = locked_pos[(j,i)]
                    grid[i][j] = c

        return grid

    def convert_shape_format(shape):
        positions = []
        format = shape.shape[shape.rotation % len(shape.shape)] 

        for i,line in enumerate(format):
            row = list(line)
            for j,column in enumerate(row):
                if column == '0':
                    positions.append((shape.x + j, shape.y + i))

        for i,pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)

        return positions


    def valid_space(shape, grid):
        accepted_pos = [[(j,i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
        accepted_pos = [j for sub in accepted_pos for j in sub]

        formatted = convert_shape_format(shape)

        for pos in formatted:
            if pos not in accepted_pos:
                if pos[1] > -1:
                    return False
        return True

    def check_lost(positions):
        for pos in positions:
            x,y = pos
            if y < 1:
                return True

        return False


    def get_shape():
        return Piece(5, 0,random.choice(shapes)) 

    def draw_text_middle(surface, text, size, color):
        font  = pygame.font.SysFont('comicsans', size, bold = True) 
        label = font.render(text, 1, color)

        surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))


    def draw_grid(surface, grid):
        sx = top_left_x
        sy = top_left_y

        for i in range(len(grid)):
            pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx + play_width,sy + i*block_size))
            for j in range(len(grid[i])):
                pygame.draw.line(surface, (128,128,128), (sx + j*block_size, sy), (sx + j*block_size,sy+ play_height))


    def clear_rows(grid, locked):
        
        inc = 0
        for i in range(len(grid)-1, -1, -1):
            row = grid[i]
            if(0,0,0) not in row:
                inc += 1
                ind = i
                for j in range(len(row)):
                    try:
                        del locked[(j,i)]
                    except:
                        continue
        
        if inc > 0:
            for key in sorted(list(locked), key = lambda x: x[1])[::-1]:
                x, y = key
                if y < ind:
                    newKey = (x, y + inc)
                    locked[newKey] = locked.pop(key)


        return inc
        

    def draw_next_shape(shape, surface):
        font = pygame.font.SysFont('comicsans', 25)
        label = font.render('Next shape', 1, (255, 255, 255))

        sx = top_left_x + play_width + 50
        sy = top_left_y + play_height/2 -100
        format = shape.shape[shape.rotation % len(shape.shape)]

        for i,line in enumerate(format):
            row = list(line)
            for j,column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size),0)
        
        surface.blit(label, (sx+10, sy-30))


    def update_score(nscore):
        score = max_score()
        gamer = Gamers_list.objects.get(id = request.session['id'])
        if int(score) > nscore:
            gamer.tetrisMaxScore = score
        else:
            gamer.tetrisMaxScore = nscore
        gamer.save()

    def max_score():
        score = (Gamers_list.objects.get(id = request.session['id'])).tetrisMaxScore
        return score

    def draw_window(surface, grid, score = 0, last_score=0):
        surface.fill((0,0,0)) 

        pygame.font.init()
        font = pygame.font.SysFont('comicsans', 30)
        label = font.render('Tetris', 1, (255,255,255))

        surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), 30))

        font = pygame.font.SysFont('comicsans', 25)
        label = font.render('Score : ' + str(score), 1, (255, 255, 255))

        sx = top_left_x + play_width + 50
        sy = top_left_y + play_height/2 -100

        surface.blit(label, (sx + 10, sy + 150))

        font = pygame.font.SysFont('comicsans', 25)
        label = font.render('High Score : ' + str(last_score), 1, (255, 255, 255))

        sx = top_left_x -200
        sy = top_left_y + 200

        surface.blit(label, (sx + 10, sy + 150))
    
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                pygame.draw.rect(surface, grid[i][j], (top_left_x + j * block_size, top_left_y + i*block_size, block_size, block_size), 0)

        pygame.draw.rect(surface, (255,0,0), (top_left_x, top_left_y, play_width, play_height), 5)

        draw_grid(surface, grid)
        # pygame.display.update()



    def main(win):
        last_score = 0
        # last_score = max_score()
        
        locked_positions = {}
        grid = create_grid(locked_positions)

        change_piece = False
        run = True
        current_piece = get_shape()
        next_piece = get_shape()
        clock = pygame.time.Clock()
        fall_time = 0
        fall_speed = 0.27
        level_time = 0
        score = 0

        while run:
            grid = create_grid(locked_positions)
            fall_time += clock.get_rawtime()
            level_time += clock.get_rawtime()
            clock.tick()

            if level_time/1000 > 5:
                level_time = 0
                if level_time > 0.12:
                    level_time -= 0.005 


            if fall_time/1000 > fall_speed:
                fall_time = 0
                current_piece.y += 1
                if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                    current_piece.y -= 1
                    change_piece = True


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.x += 1

                    if event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.x -= 1
                        
                    if event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.y -= 1

                    if event.key == pygame.K_UP:
                        current_piece.rotation += 1
                        if not(valid_space(current_piece, grid)):
                            current_piece.rotation -= 1

            shape_pos = convert_shape_format(current_piece)

            for i in range(len(shape_pos)):
                x,y = shape_pos[i]
                if y > -1:
                    grid[y][x] = current_piece.color

            if change_piece:
                for pos in shape_pos:
                    p = (pos[0],pos[1])
                    locked_positions[p] = current_piece.color
                current_piece = next_piece
                next_piece = get_shape()
                change_piece = False
                score += clear_rows(grid, locked_positions) * 10

            draw_window(win, grid, score, last_score)
            draw_next_shape(next_piece, win)
            pygame.display.update()

            if check_lost(locked_positions):
                draw_text_middle(win, "YOU LOST!",80, (255,255,255))
                pygame.display.update()
                pygame.time.delay(1500)
                run = False
                update_score(score)


    def main_menu(win):
        run = True
        while run:
            win.fill((0,0,0))
            draw_text_middle(win, 'Press Any Key To Play', 60, (255,255,255))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                if event.type == pygame.KEYDOWN:
                    main(win)
        pygame.display.quit()


    win = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Tetris')
    main_menu(win)
    return redirect('/index/')


def snake_game(request):
    class Apple:
        def __init__(self, parent_screen):
            self.parent_screen = parent_screen
            self.image = pygame.image.load("static/apple.jpg").convert()
            self.x = 120
            self.y = 120

        def move(self):
            self.x = random.randint(1, 24)*SIZE
            self.y = random.randint(1, 15)*SIZE

        def draw(self):
            self.parent_screen.blit(self.image, (self.x, self.y))
            pygame.display.flip()
        

    class Snake:
        def __init__(self, parent_screen, length): 
            self.length = length
            self.parent_screen = parent_screen
            self.block = pygame.image.load("static/block.jpg").convert()
            self.x = [SIZE] * length
            self.y = [SIZE] * length
            self.direction = 'down'

        def increase_length(self):
            self.length += 1
            self.x.append(-1)
            self.y.append(-1)
            
        def move_left(self):
            self.direction = 'left'
        
        def move_right(self):
            self.direction = 'right'
        
        def move_up(self):
            self.direction = 'up'
            
            
        def move_down(self):
            self.direction = 'down'
        
        def walk(self):
            for i in range(self.length-1,0,-1):
                self.x[i] = self.x[i-1]
                self.y[i] = self.y[i-1]

            if self.direction == 'left':
                self.x[0] -= SIZE
            if self.direction == 'right':
                self.x[0] += SIZE
            if self.direction == 'up':
                self.y[0] -= SIZE
            if self.direction == 'down':
                self.y[0] += SIZE
            self.draw()

        def draw(self):
            self.parent_screen.fill(BACKGROUNDCOLOR)

            for i in range(self.length):
                self.parent_screen.blit(self.block, (self.x[i], self.y[i]))
            pygame.display.flip()

    class Game:
        def __init__(self):
            pygame.init()
            pygame.display.set_caption("Codebasics Snake And Apple Game")
            self.surface = pygame.display.set_mode((1000,640))
            self.surface.fill(BACKGROUNDCOLOR)
            self.snake = Snake(self.surface, 1)
            self.snake.draw()
            self.apple = Apple(self.surface)
            self.apple.draw()

        def is_collision(self, x1, y1, x2, y2):
            if x1 >= x2 and x1 < x2 + SIZE:
                if y1 >= y2 and y1 < y2 + SIZE:
                    return True
            return False

        def play(self):
            self.snake.walk()
            self.apple.draw()
            self.display_score()
            pygame.display.flip()

            if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
                self.snake.increase_length()
                self.apple.move()

            for i in range(3, self.snake.length):
                if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                    raise "Game over"

        def display_score(self):
            font = pygame.font.SysFont('arial',30)
            score = font.render(f"score: {self.snake.length}", True, (255,255,255))
            self.surface.blit(score, (850,10))

        def show_game_over(self):
            self.surface.fill(BACKGROUNDCOLOR)
            font = pygame.font.SysFont('arial',30)
            score = font.render(f"Game is over! Your score is: {self.snake.length}", True, (255,255,255))
            self.surface.blit(score, (200,300))
            line2 = font.render("To play again press Enter.To exit press Escape!", True, (255,255,255))
            self.surface.blit(line2, (200,350))    
            pygame.display.flip() 

        def reset(self):
            self.snake = Snake(self.surface, 1)
            self.apple = Apple(self.surface)

        def run(self):
            running = True
            pause = False

            while running:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            running = False

                        if event.key == K_RETURN:
                            pause = False
                        
                        if not pause:
                            if event.key == K_LEFT:
                                self.snake.move_left()
                            if event.key == K_RIGHT:
                                self.snake.move_right()
                            if event.key == K_UP:
                                self.snake.move_up()
                            if event.key == K_DOWN:
                                self.snake.move_down()
                        
                    elif event.type == QUIT:
                        running = False

                try:
                    if not pause:
                        self.play()
                except Exception as e:
                    self.show_game_over()
                    pause = True
                    self.reset()
                
                time.sleep(0.25)


    def main_menu():
        game = Game()
        game.run()
    
    main_menu()
    return redirect('/index/')

def sudoku_game(request):
    N=9
    def isSafe(sudoku, row, col, num):
        for i in range(9):
            if sudoku[row][i] == num:
                return False

        for i  in range(9):
            if sudoku[i][col] == num:
                return False


        startRow = row - row % 3
        startCol = col - col % 3
        for i in range(3):
            for j in range(3):
                if sudoku[startRow + i][startCol + j] == num:
                    return False
        return True

    def solvedSudoku(sudoku, row, col):
        if row==N-1 and col==N:
            return True

        if col == N:
            row+=1
            col =0

        if sudoku[row][col] > 0:
            return solvedSudoku(sudoku, row, col+1)
        
        for num in range(1, N+1):
            if isSafe(sudoku, row, col, num):
                sudoku[row][col] = num

                if solvedSudoku(sudoku, row, col+1):
                    return True

            sudoku[row][col] = 0
        return False

    def solver(sudoku):
        if solvedSudoku(sudoku, 0, 0):
            return sudoku
        else:
            return "no"

    root = Tk()
    root.title("Sudoko Solver")
    root.geometry("324x55")

    label = Label(root, text="Fill in the numbers and click solve").grid(row=0, column=1, columnspan=10)

    errLabel = Label(root, text="", fg="red")
    errLabel.grid(row=15, column=1, columnspan=10, pady=5)

    solvedLabel = Label(root, text="", fg="green")
    solvedLabel.grid(row=15, column=1, columnspan=10, pady=5)

    cells = {}

    def ValidateNumber(P):
        out = (P.isdigit() or P == "") and len(P) < 2
        return out

    reg = root.register(ValidateNumber)

    def draw3x3Grid(row, column, bgcolor):
        for i in range(3):
            for j in range(3):
                e = Entry(root, width=5, bg = bgcolor, justify="center", validate="key", validatecommand=(reg, "%P"))
                e.grid(row=row+i+1, column=column+j+1, sticky="nsew", padx=1, pady=1, ipady=5)
                cells[(row+i+1, column+j+1)] = e

    def draw9x9Grid():
        color = "#C8C8C8"
        for rowNo in range(1,10,3):
            for colNo in range(0,9,3):
                draw3x3Grid(rowNo, colNo, color)
                if(color=="#C8C8C8"):
                    color="#ffffd0"
                else:
                    color = "#C8C8C8"

    def clearValues():
        errLabel.configure(text="")
        solvedLabel.configure(text="")
        for row in range(2,11):
            for col in range(1,10):
                cell = cells[(row, col)]
                cell.delete(0, "end")

    def getValues():
        board = []
        errLabel.configure(text="")
        solvedLabel.configure(text="")
        for row in range(2,11):
            rows = []
            for col in range(1,10):
                val = cells[(row, col)].get()
                if val == "":
                    rows.append(0)
                else:
                    rows.append(int(val))

            board.append(rows)    
        updateValues(board)   

    btn = Button(root, command=getValues, text="Solve", width=10)
    btn.grid(row=20, column=1, columnspan=5, pady=20)

    btn = Button(root, command=clearValues, text="Clear", width=10)
    btn.grid(row=20, column=5, columnspan=5, pady=20)

    def updateValues(s):
        sol = solver(s)
        if sol != "no":
            for rows in range(2,11):
                for col in range(1, 10):
                    cells[(rows, col)].delete(0, "end")
                    cells[(rows, col)].insert(0, sol[rows-2][col-1])
            solvedLabel.configure(text="Sudoku solved!")
        else:
            errLabel.configure(text="No solution exists for this sudoku")

    draw9x9Grid()
    root.mainloop()

    return redirect('/index/')

def tic(request):
    return render(request, 'tic.html')