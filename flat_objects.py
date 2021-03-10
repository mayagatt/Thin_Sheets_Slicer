from abc import ABC, abstractmethod

EXTRUDER_TEMP = 200
BED_TEMP = 60


class FlatObject(ABC):
    """
    Abstract class, to be inherited from.
    """

    def __init__(self, size, layers_num=1, thickness=0.15, x_start=150, y_start=100, speed=2000, nuzzle_size=0.38,
                 material='pla'):
        self.size = size  # mm
        self.x_start = x_start
        self.x_end = x_start + size
        self.y_start = y_start
        self.y_end = y_start + size
        self.layers_num = layers_num
        # self.thickness = thickness if isinstance(thickness, list) else [thickness] * layers_num
        self.thickness = thickness  # mm
        self.gcode = None
        self.extrusion_const = 0.00018275333333  # to multiply by: self.thickness * self.size * self.speed
        self.speed = speed
        self.material = material
        self.nuzzle_size = nuzzle_size
        self.material_dict = {'pla': [200, 60], 'abs': [250, 100], 'petg': [240, 70]}
        self.header = '\n; external perimeters extrusion width = 0.45mm\n' \
                      '; perimeters extrusion width = 0.45mm\n' \
                      '; infill extrusion width = 0.45mm\n' \
                      '; solid infill extrusion width = 0.45mm\n' \
                      '; top infill extrusion width = 0.40mm\n' \
                      '; first layer extrusion width = 0.42mm\n' \
                      'M73 P0 R1\n' \
                      'M73 Q0 S1\n' \
                      'M201 X1000 Y1000 Z1000 E5000 ; sets maximum accelerations, mm/sec^2\n' \
                      'M203 X200 Y200 Z12 E120 ; sets maximum feedrates, mm/sec\n' \
                      'M204 P1250 R1250 T1250 ; sets acceleration (P, T) and retract acceleration (R), mm/sec^2\n' \
                      'M205 X8.00 Y8.00 Z0.40 E4.50 ; sets the jerk limits, mm/sec\n' \
                      'M205 S0 T0 ; sets the minimum extruding and travel feed rate, mm/sec\n' \
                      'M862.3 P "MK3" ; printer model check\n' \
                      'M862.1 P0.4 ; nozzle diameter check\n' \
                      'M115 U3.8.1 ; tell printer latest fw version\n' \
                      'G90 ; use absolute coordinates\n' \
                      'M83 ; extruder relative mode\n' \
                      f'M104 S{self.material_dict[self.material][0]} ; set extruder temp\n' \
                      f'M140 S{self.material_dict[self.material][1]} ; set bed temp\n' \
                      f'M190 S{self.material_dict[self.material][1]} ; wait for bed temp\n' \
                      f'M109 S{self.material_dict[self.material][0]} ; wait for extruder temp\n' \
                      'G28 W ; home all without mesh bed level\n' \
                      'G80 ; mesh bed leveling\n' \
                      'G1 Y-3.0 F1000.0 ; go outside print area\n' \
                      'G92 E0.0\n' \
                      'G1 X60.0 E9.0 F1000.0 ; intro line\n' \
                      'M73 Q5 S1\n' \
                      'M73 P5 R1\n' \
                      'G1 X100.0 E12.5 F1000.0 ; intro line\n' \
                      'G92 E0.0\n' \
                      'M221 S95\n' \
                      'G21 ; set units to millimeters\n' \
                      'G90 ; use absolute coordinates\n' \
                      'M83 ; use relative distances for extrusion\n' \
                      'M900 K30 ; Filament gcode\n' \
                      'M106 S255'

        self.finish = '; Filament-specific end gcode\nG4 ; wait\nM221 S100\nM104 S0 ; turn off temperature\n' \
                      'M140 S0 ; turn off heatbed\nM107 ; turn off fan\nG1 Z30.9 ; Move print head up\nG1 X0 Y200 F3000 ; home X axis\n' \
                      'M84 ; disable motors\nM73 P100 R0\nM73 Q100 S0'

    def create_gcode(self):
        with open(f'gfile.gcode', 'w') as file:
            pass
        self.gcode = file

    def get_gcode(self):
        self.create_gcode()
        return self.gcode
