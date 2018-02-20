import curses
from curses import wrapper
import numpy as np

TetriminoShape = {
    'I': np.array([[1,1,1,1]], dtype=bool) ,
    'O': np.array([[1,1],
                   [1,1]], dtype=bool) ,
    'S': np.array([[0,1,1],
                   [1,1,0]], dtype=bool) ,
    'Z': np.array([[1,1,0],
                   [0,1,1]], dtype=bool) ,
    'J': np.array([[1,0,0],
                   [1,1,1]], dtype=bool), 
    'L': np.array([[0,0,1],
                   [1,1,1]], dtype=bool),
    'T': np.array([[0,1,0],
                   [1,1,1]], dtype=bool)
}


class Tetrimino():

    def __init__(self, PieceType=None, ULloc=[0,0]):
       assert PieceType in TetriminoShape.keys()
       assert type(ULloc) == list, 'ULloc should be list.'
       self._tetrimino = TetriminoShape[PieceType]
       self._PieceType = PieceType
       self._ULloc = ULloc

    def obtain_location(self, ExcludeVoid=False):
        xlength, ylength = self._tetrimino.shape
        xcoords, ycoords = [], []
        for xi, xloc in enumerate(self._tetrimino):
            for yi, yloc in enumerate(xloc):
                xcoords.append(xi)
                ycoords.append(yi)
        if ExcludeVoid==True:
            for coord in zip(xcoords, ycoords):
                if self._tetrimino[coord] == False:
                    xcoords.remove(coord[0])
                    ycoords.remove(coord[1])
        return np.array(xcoords) + self._ULloc[0], np.array(ycoords) + self._ULloc[1]

    def can_move(self, direction, field):
        ## obtain the destination coordinates
        xcoords, ycoords = self.obtain_location()
        if direction == 'd':
            xcoords += 1
        elif direction == 'l':
            ycoords -= 1
        elif direction == 'r':
            ycoords += 1
        else:
            raise Exception('Invalid direction specified')
        ## check whether the tetrimino is at edge or not
        xAvailability = np.all([xcoords >= 0, xcoords < field.get_shape()[0]])
        yAvailability = np.all([ycoords >= 0, ycoords < field.get_shape()[1]])
        if (xAvailability and yAvailability) == False:
            return False
        ## check the vacancy of destination
        vacancy_array = field.get_vacancy_array()
        vacancy_array[self.obtain_location(ExcludeVoid=True)] = True
        vacancy = np.all(vacancy_array[xcoords, ycoords])
        ## return
        return (xAvailability and yAvailability) and vacancy

    def move(self, direction):
        if direction == 'd':
            self._ULloc[0] += 1
        elif direction == 'l':
            self._ULloc[1] -= 1
        elif direction == 'r':
            self._ULloc[1] += 1
        else:
            raise Exception('Invalid direction specified.')

    def piece_1D(self):
        return np.reshape(self._tetrimino, self._tetrimino.size)

    def piece_remove_array(self):
        return np.array([0,0,0,0])


class Field():
    def __init__(self):
        self._field = np.zeros(shape=(20,10), dtype=bool)

    def __repr__(self):
        xlen, ylen = self._field.shape
        represent = '@'*(ylen+2) + '\n'
        for row in self._field:
            represent += '@'
            for each in row:
                if each==False:
                    represent += ' '
                else:
                    represent += '*'
            represent += '@\n'
        represent += '@'*(ylen+2) + '\n'
        return represent

    def get_shape(self):
        return self._field.shape

    def get_vacancy_array(self):
        return np.invert(self._field)


    def put_new_tetrimino(self, PieceType, ULloc):
        assert PieceType in TetriminoShape.keys()
        NewTetrimino = Tetrimino(PieceType, ULloc)
        self._field[NewTetrimino.obtain_location()] = NewTetrimino.piece_1D()
        return NewTetrimino

    def shift_tetrimino(self, tetrimino, direction):
        if tetrimino.can_move(direction, self):
            ## remove tetrimino from existing place
            self._field[tetrimino.obtain_location(ExcludeVoid=True)] = tetrimino.piece_remove_array()
            ## update the tetrimino's position
            tetrimino.move(direction)
            ## put the tetrimino into the destination place
            self._field[tetrimino.obtain_location()] = tetrimino.piece_1D()

    def select_TetriminoShape_random(self):
        return list(TetriminoShape.keys())[np.random.randint(7)]


def print_field(stdscr):
    stdscr.clear()

    field = Field()
    tet = field.put_new_tetrimino('I', [0,0])
    stdscr.addstr(field.__repr__())

    KeyAndDir = {
        curses.KEY_DOWN: 'd',
        curses.KEY_LEFT: 'l',
        curses.KEY_RIGHT: 'r'
    }
    stdscr.refresh()
    while True:
        c = stdscr.getch()
        if c in KeyAndDir.keys():
            field.shift_tetrimino(tet, direction=KeyAndDir[c])
            stdscr.clear()
            stdscr.addstr(field.__repr__())
        elif c == ord('q'):
            break
        stdscr.refresh()

wrapper(print_field)