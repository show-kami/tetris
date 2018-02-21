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

    def shift(self, field, direction):
        assert direction in ['d', 'l', 'r']
        ## calculate the destination coordinate
        xcoords, ycoords = self.obtain_location(ExcludeVoid=True)
        if direction == 'd':
            xdest, ydest = xcoords+1, ycoords
        elif direction == 'l':
            xdest, ydest = xcoords, ycoords-1
        elif direction == 'r':
            xdest, ydest = xcoords, ycoords+1
        ## check the availability of the destination
        if field.get_destination_vacancy(xcoords, ycoords, xdest, ydest) == False:
            return False
        ## shift the tetrimino
        if direction == 'd':
            self._ULloc[0] += 1
        elif direction == 'l':
            self._ULloc[1] -= 1
        elif direction == 'r':
            self._ULloc[1] += 1
        ## tell the field to update the tetrimino position
        field.update(xcoords, ycoords, xdest, ydest)
        return True

    def rotate(self, field):
        ## calculate the destination, considering clockwise rotation
        xcoords, ycoords = self.obtain_location(ExcludeVoid=True)
        xdest = ycoords - self._ULloc[1] + self._ULloc[0]
        ydest = xcoords[::-1] - self._ULloc[0] + self._ULloc[1]
        ## check the availability of the destination
        if field.get_destination_vacancy(xcoords, ycoords, xdest, ydest) == False:
            return False
        ## reshape the tetrimino
        self._tetrimino = self._tetrimino.T[:,::-1]
        ## tell the field to update the tetrimino position
        field.update(xcoords, ycoords, xdest, ydest)
        return True

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

    def get_shape(self, axis=None):
        if axis==None:
            return self._field.shape
        elif axis=='x':
            return self._field.shape[0]
        elif axis=='y':
            return self._field.shape[1]

    def get_vacancy_array(self):
        return np.invert(self._field)

    def get_destination_vacancy(self, xoccupy, yoccupy, xdest, ydest):
        ''' This method answers whether a piece can occupy the destination area.
        If True is returned, the destination is vacant.'''
        vacancy = self.get_vacancy_array()
        vacancy[xoccupy, yoccupy] = True
        if np.all([xdest >= 0, xdest < self.get_shape('x')]) \
           and np.all([ydest >= 0 , ydest < self.get_shape('y')]):
            return np.all(vacancy[xdest, ydest])
        else:
            return False

    def update(self, xold, yold, xnew, ynew):
        self._field[xold, yold] = False
        self._field[xnew, ynew] = True
        return True

    def put_new_tetrimino(self, PieceType, ULloc):
        assert PieceType in TetriminoShape.keys()
        NewTetrimino = Tetrimino(PieceType, ULloc)
        self._field[NewTetrimino.obtain_location()] = NewTetrimino.piece_1D()
        return NewTetrimino

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
        stdscr.clear()
        if c in KeyAndDir.keys():
            tet.shift(field=field, direction=KeyAndDir[c])
        elif c == curses.KEY_UP:
            tet.rotate(field)
        elif c == ord('q'):
            break
        stdscr.addstr(field.__repr__())
        stdscr.refresh()

wrapper(print_field)