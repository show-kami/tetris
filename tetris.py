import curses
from curses import wrapper
import numpy as np

TetriminoShape = {
    'I': np.array([[0,0,0,0],
                   [0,1,2,3]], dtype='int8') ,
    'O': np.array([[0,0,1,1],
                   [0,1,0,1]], dtype='int8') ,
    'S': np.array([[0,0,1,1],
                   [1,2,0,1]], dtype='int8') ,
    'Z': np.array([[0,0,1,1],
                   [0,1,1,2]], dtype='int8') ,
    'J': np.array([[0,1,1,1],
                   [0,0,1,2]], dtype='int8'), 
    'L': np.array([[0,0,0,1],
                   [0,1,2,0]], dtype='int8'),
    'T': np.array([[0,0,0,1],
                   [0,1,2,1]], dtype='int8')
}


class Tetrimino():

    def __init__(self, PieceType=None):
        assert PieceType in TetriminoShape.keys()
        self._piecepos = TetriminoShape[PieceType]

    def get_piecepos(self, axis=None):
        if axis == None:
            return self._piecepos
        elif axis == 'x':
            return self._piecepos[0]
        elif axis == 'y':
            return self._piecepos[1]

    def shift(self, field, direction):
        assert direction in ['d', 'l', 'r']
        ## calculate the destination coordinate
        xcoords, ycoords = self._piecepos
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
        self._piecepos = np.array([xdest, ydest])
        ## tell the field to update the tetrimino position
        field.update(xcoords, ycoords, xdest, ydest)
        return True

    def rotate(self, field):
        ## calculate the destination, considering clockwise rotation
        xcoords, ycoords = self._piecepos
        ULcorner = xcoords.min(), ycoords.min()
        xdest = (ycoords - ULcorner[1])*(-1) + ULcorner[0]
        ydest = (xcoords - ULcorner[0]) + ULcorner[1]
        if xdest.min() < xcoords.min():
            ## impose the height minimun in order to disturb from climbing
            xdest = xdest - xdest.min() + xcoords.min()
        ## check the availability of the destination
        if field.get_destination_vacancy(xcoords, ycoords, xdest, ydest) == False:
            return False
        ## reshape the tetrimino
        self._piecepos = np.array([xdest, ydest])
        ## tell the field to update the tetrimino position
        field.update(xcoords, ycoords, xdest, ydest)
        return True

    def piece_1D(self):
        return np.reshape(self._piecepos, self._piecepos.size)

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
        if type(xoccupy) == np.ndarray and type(yoccupy) == np.ndarray:
            vacancy[xoccupy, yoccupy] = True
        if np.all([xdest >= 0, xdest < self.get_shape('x')]) \
           and np.all([ydest >= 0 , ydest < self.get_shape('y')]):
            return np.all(vacancy[xdest, ydest])
        else:
            return False

    def update(self, xold, yold, xnew, ynew):
        if type(xold) == np.ndarray and type(yold) == np.ndarray:
            self._field[xold, yold] = False
        if type(xnew) == np.ndarray and type(ynew) == np.ndarray:
            self._field[xnew, ynew] = True
        return True

    def put_new_tetrimino(self, PieceType):
        assert PieceType in TetriminoShape.keys() or PieceType == 'random'
        if PieceType == 'random':
            PieceType = list(TetriminoShape.keys())[np.random.randint(7)]
        NewTetrimino = Tetrimino(PieceType)
        self.update(None,None, NewTetrimino.get_piecepos()[0], NewTetrimino.get_piecepos()[1])
        return NewTetrimino

    def judge_bottom_edge_touch(self, tetrimino):
        vacancy = self.get_vacancy_array()
        xcoords, ycoords = tetrimino.get_piecepos()
        if np.all(tetrimino.get_piecepos('x')+1 < self.get_shape('x')) == False:
            return True
        elif self.get_destination_vacancy(xcoords, ycoords, xcoords+1, ycoords) == False:
            return True
        else:
            return False


def print_field(stdscr):
    stdscr.clear()

    field = Field()
    tet = field.put_new_tetrimino('random')
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
        if field.judge_bottom_edge_touch(tet):
            tet = field.put_new_tetrimino('random')
        stdscr.addstr(field.__repr__())
        stdscr.refresh()

wrapper(print_field)