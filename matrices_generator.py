import numpy as np
from copy import deepcopy


def positive_charge(n, azimuthal=False):
    """

    :param n: dimensions of square mtx
    :return: matrix n x n of angles, in redial or azimuthal direction from center
    """
    center = (n - 1) / 2

    angles = []
    radios = []
    for i in range(n):
        row = []
        r_row = []
        for j in range(n):
            # print('r = ', (i - center) ** 2 + (j - center) ** 2)
            # print('r_floor = ', np.floor((i - center) ** 2 + (j - center) ** 2))
            r_row.append(np.floor((i - center) ** 2 + (j - center) ** 2))

            angle = np.arctan2(i - center, j - center) * 180 / np.pi + 90
            if azimuthal:
                angle += 90
            if angle < 0:
                angle += 180
            if angle > 180:
                angle -= 180
            row.append(angle)
        angles.append(row)
        radios.append(r_row)
        # print(r_row)

    return angles, radios


# ang, r = positive_charge(10)


# print(r)
def alternating_radial_azimutal(n, perp=False):
    center = (n - 1) / 2
    azimut = {2, 8, 12, 14, 26, 24, 40}
    rad = {0, 4, 6, 18, 20, 22, 32}
    thresh = [0, 2, 6, 14, 22, 26, 32, 40]
    angles = []
    for i in range(n):
        row = []
        for j in range(n):
            angle = np.arctan2(i - center, j - center) * 180 / np.pi + 90

            if not perp:
                if (np.floor((i - center) ** 2 + (j - center) ** 2)) in azimut:
                    angle += 90  # azimutal
            else:
                if (np.floor((i - center) ** 2 + (j - center) ** 2)) in rad:
                    angle += 90  # azimutal

            if angle < 0:
                angle += 180
            if angle > 180:
                angle -= 180
            row.append(angle)
        angles.append(row)
    return angles


print(alternating_radial_azimutal(10))


def four_charges(n):
    """
    :param n: dimensions of square mtx
    :return: matrix n x n of angles, in redial or azimuthal direction from center of each quarter of mtx
    """
    angles = []
    for i in range(n):
        row = []
        for j in range(n):
            if j < n / 2 and i < n / 2:
                x_0 = (n - 1) / 4
                y_0 = (n - 1) / 4
            elif j < n / 2 <= i:
                x_0 = 3 * (n - 1) / 4
                y_0 = (n - 1) / 4
            elif j >= n / 2 > i:
                x_0 = (n - 1) / 4
                y_0 = 3 * (n - 1) / 4
            else:
                x_0 = 3 * (n - 1) / 4
                y_0 = 3 * (n - 1) / 4

            angle = np.arctan2(i - x_0, j - y_0) * 180 / np.pi + 90

            if angle < 0:
                angle += 180
            if angle > 180:
                angle -= 180
            row.append(angle)
        angles.append(row)

    return angles


def dome(n):
    center = (n - 1) / 2

    angles = []
    for i in range(n):
        row = []
        for j in range(n):
            angle = np.arctan2(i - center, j - center) * 180 / np.pi

            angle += ((i - center) ** 2 + (j - center) ** 2) * 10

            if angle < 0:
                angle += 180
            if angle > 180:
                angle -= 180
            row.append(angle)
        angles.append(row)

    return angles


def face():
    mtx = [[30, 20, 10, 170, 160, 150, 30, 20, 10, 170, 160, 150],
           [40, 20, 0, 180 - 20, 180 - 40, 0, 0, 40, 20, 0, 180 - 20, 180 - 40],
           [160, 120, 90, 60, 40, 10, 170, ]]
    return


def rotate_as_function_of_y_sqr(n, const):
    mtx = []
    for i in range(n):
        angle = np.arctan2(const * (5 * i) ** 2, 1) * 180 / np.pi  # 5*i in order to work in mm
        mtx.append(np.full(n, angle).tolist())
    return mtx


def rotate_as_function_of_y(n, const):
    mtx = []
    for i in range(n):
        angle = np.arctan2(const * (5 * i), 1) * 180 / np.pi  # 5*i in order to work in mm
        mtx.append(np.full(n, angle).tolist())

    return mtx


def rotate_sin(n, const):
    mtx = []
    for i in range(n):
        angle = const * ((i * 5 + 2.5) + np.sin(
            (i * 5 + 2.5) * 1)) * 90  # * 180 / np.pi  # 5*i+ 2.5 in order to work in mm and get value of mid fixel
        mtx.append(np.full(n, angle).tolist())
    return mtx


def malmala():
    mtx = []
    for i in range(7):
        mtx.append(np.full(15, 0).tolist())
    for i in range(4):
        mtx.append(np.full(15, 90).tolist())
    for i in range(len(mtx)):
        print(mtx[i])
    return mtx


def gradual_malmala(n):
    """

    :param n: length of strip
    :return:
    """
    mtx = []
    for i in range(3):  # make base of straight lines, to prevent parasitic curling
        mtx.append(np.full(n, 0).tolist())
    for i in range(6):
        angle = np.arctan2(0.02 * ((5 * i) ** 2), 1) * 180 / np.pi  # 5*i in order to work in mm
        mtx.append(np.full(n, angle).tolist())

    return mtx


def egg_carton(n, offset=1):
    """
    :param offset: can be 1 or -1. default 1 = no change. -1 causes shift between all squares
    :param n:
    :return: matrix of alternating 45 and -45 degrees matrix
    """
    return [[offset * 45 * (-1) ** (i + j) for i in range(n)] for j in range(n)]


def get_perpendicular(mtx):
    new_mtx = deepcopy(mtx)
    for i in range(len(mtx)):
        for j in range(len(mtx[0])):
            new_mtx[i][j] = mtx[i][j] + 90
    return new_mtx


mtx1 = [[0, 90, 135], [90, 135, 0], [135, 0, 45], [135, 90, 90]]
mtx2 = get_perpendicular(mtx1)
# print(mtx1)
# print(mtx2)
