import angled_square
from flat_objects import FlatObject


class MultiSquare(FlatObject):
    '''
    Create gcode for 3d Pruca MK3S printer, of separate multiple squares laying one next to another.
    Initiate object with array of arrays, ordered parameters: [[size, layers_num, thickness, speed],...]
    '''

    # self, size, layers_num = 1, thickness = 0.15, x_start = 150, y_start = 100, speed = 2000, nuzzle_size = 0.4):

    def __init__(self, name, array, start_x=150, start_y=100):
        FlatObject.__init__(self, 10, x_start=start_x, y_start=start_y)
        self.array = array

        self.name = name

    def create_gcode(self, frame=False):
        '''
        :param frame:
        :return:
        '''
        with open(self.name, 'w') as file:
            file.seek(0)

            ### header ###
            file.write(self.header)

            start = [self.x_start, self.y_start]

            for i, item in enumerate(self.array):
                # print(start)
                # sq = squre.Square(size=item[0], layers_num=item[1], thickness=item[2], speed=item[3],
                #                   nuzzle_size=item[4], x_start=start[0],
                #                   y_start=start[1])

                # self, size, nuzzle_size=0.4, layers_num=1, thickness=0.15, x_start=150, y_start=100, speed=2000

                sq = angled_square.AngledSquare(item[0], nuzzle_size=item[1], layers_num=item[2], thickness=item[3],
                                                speed=item[4], x_start=start[0],
                                                y_start=start[1])
                file.write(f'\n; sqr number {i + 1}\n\n')
                sq.fill_inside(file)

                # move position of square
                if start[0] < 200:
                    start[0] = start[0] + sq.size + 5
                else:
                    start[0] = self.x_start
                    start[1] = start[1] + sq.size + 5
                # else:
                #     raise NameError('exceeded plate boundaries')

            # finish print
            file.write(self.finish)
        self.gcode = file

    def get_gcode(self, frame=False):
        self.create_gcode(frame)
        return self.gcode


# create square object, get "write_square" func, write into file
#

# size, nuzzle_size, layers_num=1, thickness=0.15, speed=2000

def get_scaling_mtx():
    """
    grid of increasing layer num and thickness
    :return:
    """
    lst = []
    J = [0.1, 0.125, 0.2, 0.25, 0.3]
    for i in range(5):
        for j in range(len(J)):
            print('l_num is ', i + 1, 'thickness is ', J[j])
            lst.append([20, 0.37, i, J[j], 2000])
        print(lst)
    return lst








mtx=[[20, 0.37, 1, 0.15, 2000],[20, 0.37, 1, 0.15, 2000], [20, 0.37, 1, 0.15, 2000], [20, 0.37, 1, 0.15, 2000],
    [20, 0.37, 2, 0.15, 2000],[20, 0.37, 2, 0.15, 2000], [20, 0.37, 2, 0.15, 2000], [20, 0.37, 2, 0.15, 2000],
    [20, 0.37, 3, 0.15, 2000], [20, 0.37, 3, 0.15, 2000], [20, 0.37, 3, 0.15, 2000], [20, 0.37, 3, 0.15, 2000]]


sqs = MultiSquare('calibrate.gcode', mtx, start_y=50, start_x=70)
sqs.get_gcode()


# sqs = MultiSquare('0.07 layers.gcode',
#     [[20, 0.35, 3, 0.1, 2000], [20, 0.35, 3, 0.07, 2000], [20, 0.35, 3, 0.07, 2000], [20, 0.35, 3, 0.07, 2000],
#     [20, 0.35, 4, 0.07, 2000], [20, 0.35, 4, 0.07, 2000], [20, 0.35, 4, 0.07, 2000], [20, 0.35, 4, 0.07, 2000],
#     [20, 0.35, 2, 0.07, 2000], [20, 0.35, 2, 0.07, 2000], [20, 0.35, 5, 0.07, 2000], [20, 0.35, 5, 0.07, 2000],
#     [20, 0.35, 6, 0.07, 2000], [20, 0.35, 6, 0.07, 2000], [20, 0.35, 6, 0.07, 2000], [20, 0.35, 6, 0.07, 2000],
#     [20, 0.35, 7, 0.07, 2000], [20, 0.35, 7, 0.07, 2000], [20, 0.35, 7, 0.07, 2000], [20, 0.35, 7, 0.07, 2000],
#     [20, 0.35, 8, 0.07, 2000], [20, 0.35, 8, 0.07, 2000], [20, 0.35, 8, 0.07, 2000], [20, 0.35, 8, 0.07, 2000]
#      ])

# [size, layers_num, thickness, speed,nuzz]

# [20, 0.32, 3, 0.05, 2500],[20, 0.32, 3, 0.05, 2500],[20, 0.32, 4, 0.05, 2500],[20, 0.32, 4, 0.05, 2500],
#      [20, 0.32, 5, 0.05, 2500],[20, 0.32, 5, 0.05, 2500],[20, 0.32, 6, 0.05, 2500],[20, 0.32, 6, 0.05, 2500],
#      [20, 0.32, 7, 0.05, 2500],[20, 0.32, 7, 0.05, 2500],[20, 0.32, 8, 0.05, 2500],[20, 0.32, 8, 0.05, 2500],

#      [20, 0.4, 4, 0.05, 2500], [20, 0.4, 4, 0.05, 2500], [20, 0.4, 4, 0.05, 2500], [20, 0.4, 4, 0.05, 2500],
#      [20, 0.32, 5, 0.05, 2500], [20, 0.32, 5, 0.05, 2500], [20, 0.32, 5, 0.05, 2500], [20, 0.32, 5, 0.05, 2500],
#      [20, 0.32, 6, 0.05, 2500], [20, 0.32, 6, 0.05, 2500], [20, 0.32, 6, 0.05, 2500], [20, 0.32, 6, 0.05, 2500],
#      [20, 0.32, 7, 0.05, 2500], [20, 0.32, 7, 0.05, 2500], [20, 0.32, 7, 0.05, 2500], [20, 0.32, 7, 0.05, 2500],
#      [20, 0.32, 8, 0.05, 2500], [20, 0.32, 8, 0.05, 2500], [20, 0.32, 8, 0.05, 2500], [20, 0.32, 8, 0.05, 2500]


# [20, 1, 0.07, 2500, 0.35], [20, 1, 0.07, 2500, 0.35], [20, 1, 0.07, 2500, 0.35], [20, 1, 0.15, 2500, 0.35],
#      [20, 2, 0.07, 2500, 0.35], [20, 2, 0.07, 2500, 0.35], [20, 2, 0.07, 2500, 0.35], [20, 2, 0.15, 2500, 0.35],
#      [20, 8, 0.07, 2500, 0.35], [20, 3, 0.07, 2500, 0.35], [20, 3, 0.07, 2500, 0.35], [20, 3, 0.15, 2500, 0.35],


# todo: for thicknesses lower than 0.15, try and "take down" z in ~0.02mm to componsate for irregularities
