import numpy as np
import math
import matrices_generator

from angled_square import AngledSquare
from flat_objects import FlatObject


class AngledGrid(FlatObject):
    '''
    Create gcode for 3d Pruca MK3S printer, of square grid, each sub-square is made of parallel lines, in different angels.
    !! each angle is between lines and x axis facing *left* !!
    All square have the same parameters (given as input) except angle.
    Angle of sub-square (i,j) is  defined by input angle matrix[i,j].
    initiate object with array of arrays, ordered parameters: [[size, layers_num, thickness, speed],...]
    '''

    def __init__(self, sq_size, nuzzle_size, layers_num, thickness, speed, file_name, angles_mtx1, angles_mtx2=None,
                 num_mtx1=1, thickness_mtx=None, layer_thickness=None, x_start=150, y_start=100, material='pla'):
        """

        :param sq_size: size of single square in matrix

        :param sq_num: number of squares in matrix
        :param nuzzle_size: nuzzle size
        :param layers_num: number of layers
        :param thickness: thickness of each layer
        :param speed: of printing. mm/min
        :param angles_mtx1: 2d array of angles (degrees!). angles_arr[i,j] = angle of square[i,j] in grid. rectangle.
                representing pixel angles of bottom layers of sheet.
        :param angles_mtx2: must be of same dimensions as angles_mtx1! representing pixel angles of upper layers of sheet
        :param thickness_mtx: 2d array of layer thickness. thickness is defined locally. None by default, meaning
                constant thickness.
        :param x_start: x position of bottom left corner
        :param y_start: y position of bottom left corner
        """
        FlatObject.__init__(self, sq_size, layers_num=layers_num, thickness=thickness, speed=speed,
                            nuzzle_size=nuzzle_size, x_start=x_start, y_start=y_start, material=material)
        self.angles_mtx1 = list(list(x)[::-1] for x in zip(*angles_mtx1))  # rotate for consistency with input
        print(angles_mtx2)
        if angles_mtx2 is not None:
            self.angles_mtx2 = list(list(x)[::-1] for x in zip(*angles_mtx2))
        else:
            self.angles_mtx2 = None
        self.num_mtx1 = num_mtx1
        self.x_sq_num = len(angles_mtx1[0])  # number of squares in the x axis
        self.y_sq_num = len(angles_mtx1)  # number of squares in the y axis
        self.file_name = file_name

        self.thickness_mtx = None
        self.initiate_local_thickness_matrix(thickness_mtx)

        self.x_pos = None
        self.y_pos = None
        self.check_board_limits(x_start, y_start)

        self.layer_thickness = layer_thickness

    def check_board_limits(self, x_start, y_start):
        assert (
                self.size * self.x_sq_num + x_start <= 250), f'X exceeding board\'s limits by {self.size * self.x_sq_num + x_start - 250}'
        assert (
                self.size * self.y_sq_num + y_start <= 200), f'Y exceeding board\'s limits by {self.size * self.y_sq_num + y_start - 200}'  # make sure not exceeding board's limits
        self.x_pos = np.arange(x_start, self.size * self.x_sq_num + x_start, self.size + self.nuzzle_size / 2)
        self.y_pos = np.arange(y_start, self.size * self.y_sq_num + y_start, self.size + self.nuzzle_size / 2)

    def initiate_local_thickness_matrix(self, thickness_mtx):
        if thickness_mtx is not None:
            self.thickness_mtx = list(list(x)[::-1] for x in zip(*thickness_mtx))  # rotate for consistency with input
            # make sure angles and thickness matrix have the same dimensions
            assert (len(self.thickness_mtx) == len(self.angles_mtx1) & len(self.thickness_mtx[0]) == len(
                self.angles_mtx1[0])), 'Angles and thickness matrices are of different dimensions'
        else:
            self.thickness_mtx = thickness_mtx

    def create_gcode(self):
        """

        creating gcode for grid, according to given input
        """

        with open(self.file_name, 'w') as file:
            file.seek(0)

            file.write(self.header)  # header

            # first, iterate over all angle mtx, create corresponding square instance for each angle in grid.
            pos1 = []
            if self.angles_mtx2 is not None:
                pos2 = []
                positions = [pos1, pos2]
            else:
                positions = [pos1]
            angles_mtx = self.angles_mtx1

            print('pos', positions)

            for k in range(len(positions)):
                if k != 0:
                    angles_mtx = self.angles_mtx2

                for i, x_pos in enumerate(self.x_pos):
                    row_pos = []
                    for j, y_pos in enumerate(self.y_pos):
                        print(i, j)
                        angle = angles_mtx[i][j]
                        sq = AngledSquare(self.size, angle=angle, nuzzle_size=self.nuzzle_size,
                                          thickness=self.thickness, x_start=x_pos, y_start=y_pos)  # create instance

                        array = sq.generate_arrays()
                        row_pos.append(array)  # add sq position to row array
                    positions[k].append(row_pos)  # add row positions array to mtx

            # now, iterate to print - meaning, loop over layers, over all grid, by rows than columns, than loop over
            # each square's position - to print, than print them by order w corresponding extrusion (based on distance).
            pos = positions[0]  # default, only one angle mtx
            for layer in range(self.layers_num):
                if (self.angles_mtx2 is not None) and (layer >= self.num_mtx1):
                    pos = positions[1]

                if self.layer_thickness is not None:
                    self.thickness = self.layer_thickness[i]
                self.write_layer_begining(file, layer + 1)

                # iterate to write printing instructions to the file
                for i, row in enumerate(pos):  # iterate row by row over matrix
                    for j, array in enumerate(row):  # iterate of all sqrs in row

                        file.write(
                            f'G1 Z{((layer + 1) + 3) * self.thickness} F{6000.000}; move z up\n')  # move to new position safely: move z up
                        file.write(f'G0 X{self.x_pos[i]} Y{self.y_pos[j]}\n')
                        file.write(f'G1 Z{(layer + 1) * self.thickness}; move z down \n')  # move z back down

                        # new square! iterate of all sqr pos
                        for k in range(len(array)):
                            file.write(f'G1 X{array[k][0]} Y{array[k][1]} '
                                       f'E{sq.get_extrusion(array[k][0] - array[k - 1][0], array[k][1] - array[k - 1][1], (layer + 1))}\n')

            file.write(self.finish)
        self.gcode = file

    def write_layer_begining(self, file, layer):
        """
        assuming layer start at 1 (not 0).
        write down header for new layer (determine z)
        :param file: to write gcode commands to
        :param layer: of print
        """
        file.write('G92 E0.0\n'
                   f';{self.thickness * layer}\n'
                   'G1 E-0.80000 F2100.00000\n'
                   'G1 Z0.600 F10800.000\n'
                   f';AFTER_LAYER_CHANGE\n;{self.thickness * layer}\n'
                   f'G1 X{self.x_start} Y{self.y_start}\n'
                   f'G1 Z{self.thickness * layer}\n'  # change each layer
                   'G1 E0.80000 F2100.00000\n'
                   f'M204 S{self.speed}\n'
                   f'G1 F{self.speed}\n\n')  ## speed

    def get_gcode(self):
        self.create_gcode()
        return self.gcode


mtx2 = [[45, 45, 45], [45, 45, 0], [90, 90, 0], [90, 90, 0]]
mtx1 = [[0,90,90], [0,90,90], [135, 135, 45], [135, 135, 45]]
print('mtx1', mtx1)
print('mtx2', mtx2)

# create square object, get "write_square" func, write into file

grid = AngledGrid(10, 0.37, 4, 0.15, 2000, 'ariels1.gcode', mtx1, angles_mtx2=mtx2, num_mtx1=2, y_start=70,
                  x_start=200)
grid.create_gcode()
# (self, sq_size, nuzzle_size, layers_num, thickness, speed, file_name, angles_mtx1, angles_mtx2=None,
#                  thickness_mtx=None, layer_thickness=None, x_start=150, y_start=100, material='pla'):

# sq_size, nuzzle_size, layers_num, thickness, speed, angles_mtx, file_name, thickness_mtx=None,
# layer_thickness=None,
# x_start=150, y_start=100, material='pla'
# n = 6
# egg_mtx = matrices_generator.egg_carton(n)
# egg_carton = AngledGrid(10, 0.37, 2, 0.1, 2000, egg_mtx, 'egg_carton' + str(n) + 'pla.gcode', material='pla')
# egg_carton.create_gcode()


# waves
# mtx1 = [[0, 0, 0], [90, 90, 90], [0, 0, 0], [90, 90, 90], [0, 0, 0], [90, 90, 90], [0, 0, 0], [90, 90, 90], [0, 0, 0], [90, 90, 90]]
# mtx2 = [[90, 90, 90], [0, 0, 0], [90, 90, 90], [0, 0, 0], [90, 90, 90], [0, 0, 0], [90, 90, 90], [0, 0, 0], [90, 90, 90], [0, 0, 0]]
