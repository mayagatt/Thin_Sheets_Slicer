from flat_objects import FlatObject
import numpy as np


class AngledSquare(FlatObject):
    '''
    Single square of dimensions lxlxdz, filled with parallel lines which are aligned in the same (given) angle, to be
    printed by 3d printer. Can have many layers.
    !! Angle is between lines and x axis facing *left* !!
    Has method generate_gcode to generate 3d printing instructions. Gcode file is saved to folder when calling
    create_gcode method.
    '''

    def __init__(self, size, file_name='test', angle=0, nuzzle_size=0.38, layers_num=1, thickness=0.15, x_start=150,
                 y_start=100,
                 speed=2000, material='pla'):

        """
        :param size: of each squre
        :param angle: angle between lines and positive x axis (facing left)
        :param layers_num: number of layers, to print
        :param thickness: of each layer
        :param x_start: x position of bottom left corner
        :param y_start: y position of bottom left corner
        :param speed: of print, mm/min
        :param material: lower case string of print material. effect temperatures.

        """

        FlatObject.__init__(self, size, layers_num, thickness, x_start, y_start, speed, material)
        self.file_name = file_name
        self.rotated = False

        angle = angle % 360

        if 180 <= angle < 270:
            angle = 270 - angle
        if 270 <= angle < 360:
            angle = 360 - angle
            self.rotated = True
        if angle < 0:
            angle = 180 + angle
        # now, angle should be between 0 to 180 deg.
        #  edge cases: angles nearing 0 or 90
        if 0 < angle < 5:
            self.angle = 0

        if np.abs(angle - 90) < 5:
            self.angle = np.pi / 2

        # finally apply
        elif angle > 90:
            self.angle = (180 - angle) * np.pi / 180
            self.rotated = True

        else:
            self.angle = angle * np.pi / 180

        # edge cases
        self.dx = nuzzle_size / np.abs(np.sin(self.angle)) if self.angle != 0 else self.size
        self.dy = nuzzle_size / np.cos(self.angle) if self.angle != 90 else self.size

    def create_gcode(self):
        """
        write to self.gcode the printing instructions by order: write header (print settings), than location and
        extrusion of specific print, than end print.
        """
        with open(f'{self.file_name}.gcode', 'w') as file:
            file.write(self.header)
            self.fill_inside(file)

            file.write(self.finish)

        self.gcode = file

    def fill_inside(self, file):
        for i in range(self.layers_num):
            height = self.thickness * (i + 1)
            # if self.thickness < 0.15 and i == 0:  # not working try to get thinner layers
            #     height = self.thickness * 0.6 * (i + 1)

            file.write(';BEFORE_LAYER_CHANGE '
                       'G92 E0.0'
                       ';0.15'
                       f';{height}\n'
                       'G1 E-0.80000 F2100.00000\n'
                       'G1 Z0.600 F10800.000\n'
                       f';AFTER_LAYER_CHANGE\n;{height}\n'
                       f'G1 X{self.x_start} Y{self.y_start}\n'
                       f'G1 Z{height}\n'  # change each layer
                       'G1 E0.80000 F2100.00000\n'
                       f'M204 S{self.speed}\n'
                       f'G1 F{self.speed}\n\n')  ## speed

            pos = self.generate_arrays()
            for i in range(len(pos)):
                if i == 0:
                    # write lines in format: 'G1 Xx Yy Ee', where E == extrusion.
                    file.write(
                        f'G1 X{pos[i][0]} Y{pos[i][1]} E{self.get_extrusion(pos[i][0] - self.x_start, pos[i][1] - self.y_start, layer=i)}\n')
                else:
                    file.write(
                        f'G1 X{pos[i][0]} Y{pos[i][1]} E{self.get_extrusion(pos[i][0] - pos[i - 1][0], pos[i][1] - pos[i - 1][1], layer=i)}\n')

    def generate_arrays(self):
        """
        create 4 arrays for 4 edges of the square. links them to 2 arrays of 2 adges, accordeing to the travel wanted.
        combines two arrays in a zipper method, 2 locations of each one at a time, to create the weave pattern.
        the locations ans their order are providing the geometry of the shape.
        two edge cases: angle=0 and angle=90
        :return: merged list of location, to iterate and print accordingly
        """

        x_array = np.round(np.arange(self.x_start, self.x_end, self.dx), 6)
        y_array = np.round(np.arange(self.y_start, self.y_end, self.dy), 4)

        if self.angle == 0:  # iterate only over right and left edges.
            array2 = [[self.x_start, y] for y in y_array]
            array1 = [[self.x_end, y] for y in y_array]

        elif self.angle == np.pi / 2:  # iterate only over bottom and upper edges.
            array2 = [[x, self.y_start] for x in x_array]
            array1 = [[x, self.y_end] for x in x_array]

        else:  # just a nice midvalue angle.

            # adjust positions to corners, to keep angle and nuzzle size.
            k = self.y_end - y_array[-1]  # gap between last location on edge to the end of the edge

            m = self.dx - k / np.tan(self.angle)  # simple geometry leads to this conclusion
            x_up = np.round(np.arange(self.x_start + m, self.x_end, self.dx), 4).tolist()

            # right and left up-shift
            k = self.x_end - x_array[-1]
            m = self.dy - k * np.tan(self.angle)
            y_right = np.round(np.arange(self.y_start + m, self.y_end, self.dy), 4).tolist()

            # x_up, y_right = self.get_shifted_arrays(x_bottom, y_left) if self.angle != 0 else [],np.round(np.arange(self.y_start, self.y_end, self.dy), 4)

            if self.rotated:  # angle > 90, hence starting from bottom right corner.
                # mirrored x positions around x axis
                bottom = [[self.x_end + self.x_start - x, self.y_start] for x in x_array]  # bottom array
                up = [[self.x_end + self.x_start - x, self.y_end] for x in x_up]  # upper array

                # mirror y array around x axis: y positions stay same, but left and right edges switch sides
                left = [[self.x_start, y] for y in y_right]  # left edge initiated with right y positions
                right = [[self.x_end, y] for y in y_array]  # same, vice-versa

                array1, array2 = right + up, bottom + left  # first array goes from bottom right corner, up and left. second array goes left and up.

            else:  # angle <= 90, hence starting from bottom left corner.
                bottom = [[x, self.y_start] for x in x_array]
                up = [[x, self.y_end] for x in x_up]

                left = [[self.x_start, y] for y in y_array]
                right = [[self.x_end, y] for y in y_right]

                array1, array2 = bottom + right, left + up

        # now, merge two arrays into one, alternating 2 position from array1 and then 2 from array2
        arr = self.merge_two_arrays(array1, array2)

        return arr

    def merge_two_arrays(self, array1, array2):
        """
        merging 2 lists of positions, zipper way, for 3d printer to alternate between both. small step (nuzzle size) on
        each line, and long steps between them.
        :param array1: python list of [x_pos,y_pos]. positions on two edges, for printer to stop on.
        :param array2: python list of [x_pos,y_pos]. positions on two edges, for printer to stop on.
        :return: merged array of positions, for printer to stop on. will fill up the surface between the travel lines
        with perallal lines in certain angle.
        """
        arr = []
        i, j = 0, 1
        while i < len(array1) - 1 and j < len(array2) - 1:
            # add 2 from first array
            arr.append(array1[i])
            arr.append(array1[i + 1])

            # add 2 from second array
            arr.append(array2[j])
            arr.append(array2[j + 1])

            i, j = i + 2, j + 2  # move counters
        arr = arr + array1[i::] + array2[j::]  # add leftovers
        return arr

    def get_shifted_arrays(self, x_arr, y_arr):
        """
        find the shift between upper verticis and lower ones. same for right and left
        :param x_arr:
        :param y_arr:
        :return: shifted x anf y array, according to shift found and with nuzzle size steps.
        """

        # geomtery to find the shift between upper verticis and lower ones. same for right anf left after.
        k = self.y_end - y_arr[-1]  # gap between last location on edge to the end of the edge
        m = self.dx - k / np.tan(self.angle)  # simple geometry leads to this conclusion
        x_up_arr = np.round(np.arange(self.x_start + m, self.x_end, self.dx), 4).tolist()

        # right and left up-shift
        k = self.x_end - x_arr[-1]
        m = self.dy - k * np.tan(self.angle)
        y_right_arr = np.round(np.arange(self.y_start + m, self.y_end, self.dy), 4).tolist()
        return x_up_arr, y_right_arr

    def get_extrusion(self, dx, dy, layer):
        """
        still un-sealed formula. not linear with all the parameters.
        :param dx: distance traveled by machine in x direction
        :param dy: distance traveled by machine in y direction
        :return: amount of material to extrude by printer in this move.
        """
        if layer == 0:
            if self.thickness < 0.1:
                const = 3
            else:
                const = 1.55

        else:
            const = 0.45

        print(self.thickness, ' ', layer)

        return ((dx ** 2 + dy ** 2) ** (1 / 2)) * self.extrusion_const * self.thickness * self.speed * const


sq = AngledSquare(20, file_name='test0.05', thickness=0.05, layers_num=1, angle=0, nuzzle_size=0.3, material='pla')
sq.create_gcode()
