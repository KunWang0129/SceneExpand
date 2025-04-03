'''
Scene Setup:
- Axes: x (left to right), y (bottom to top), z (back to front).
- Room Walls: left (x=0), right (x=4), front (z=4), back (z=0), floor (y=0), ceiling (y=3).
- Rotations: Allowed only around y-axis; valid degrees: 0, 45, 90, 135, 180, 225, 270, 315.

Create scene with scene = Scene(dims=(WIDTH,DEPTH,HEIGHT)). Note that minimum dimensions are 5x5x3 meters. Each object to be added in the scene has a unique name such as 'window1', 'door2', etc.
API for adding wall elements:
- scene.add_walls(wall_color, floor_texture, ceiling_texture): Add walls with respective textures or colors specified in plain english.
For the following set variables wall ∈ {{'left_wall', 'right_wall', 'front_wall', 'back_wall'}} and position ∈ {{'left', 'middle', 'right', 'full'}}.
- scene.place_window(name, wall, type, position, place_curtain=False): Add window. type ∈ {{'floor_to_ceiling', 'standard', 'picture'}}, set place_curtain=True to add curtain. Note that position must be 'full' for 'floor_to_ceiling' and 'picture' windows.
- scene.place_door(name, wall, position): Add door.

Adding Objects:
- scene.add(name, desc, dims=(width,depth,height)): Add object with a description. dims is optional for objects where particular dimensions can be specified.

Object Access:
- Direct scene.<object_name> or via scene.get_object('name') for Object3D instances.
- Properties: .width, .height, .depth, .x, .y, .z for dimensions and coordinates.

Object Manipulation:
- scene.<obj_name>.set_rotation(rot): Rotate object; rot ∈ {{0, 45, 90, 135, 180, 225, 270, 315}}.
- scene.<obj_name>.place_relative(relation, obj, dist=0, sideways_shift=0, face_towards=None): Position object relative to another. relation ∈ {{'left_of', 'right_of', 'in_front_of', 'behind_of', 'on_top_of', 'left_adj', 'right_adj'}}. obj should be the Object3D instance (and NOT its name). face_towards can be another Object3D instance or names of walls ∈ {{'left_wall', 'right_wall', 'front_wall', 'back_wall'}}.
- scene.<obj_name>.place_global(x, y='floor', z, delta_x=0, delta_y=0, delta_z=0, face_towards=None): Position object in global coordinates. (x,y,z) can either be coordinates or x ∈ {{'left_wall', 'right_wall', 'center'}}, y ∈ {{'floor', 'ceiling'}}, z ∈ {{'front_wall', 'back_wall', 'center'}}. face_towards can be another Object3D instance or names of walls ∈ {{'left_wall', 'right_wall', 'front_wall', 'back_wall'}}.
- scene.<obj_name>.place_seats_around_round_arrangement(list_of_seats): Arrange seats in a circle.
- scene.<obj_name>.place_seats_rectangular_arrangement(first_longer_side, second_longer_side, first_shorter_side, second_shorter_side): Arrange seats in a rectangle. first_longer_side and second_longer_side are along the longer side of the table while first_shorter_side and second_shorter_side are along the shorter side of the table. All four arguments accept only list of Object3D instances.
- scene.<obj_name>.place_on_wall(wall, horizontal_position='middle', vertical_position='middle'): Place object on a wall. wall ∈ {{'left_wall', 'right_wall', 'front_wall', 'back_wall'}}. horizontal_position ∈ {{'left', 'middle', 'right'}}. vertical_position ∈ {{'top', 'middle', 'bottom'}}.

Constraints:
csr.init_grads(): to initialize gradients for constraints.
csr.no_overlaps(): to ensure that no objects overlaps are there in the scene
csr.no_out_of_bounds(): to ensure that no objects are out of bounds
csr.visible(obj, from_obj): to ensure that obj is visible from from_obj
csr.access(obj1, obj2, min_dist, max_dist): to ensure that obj1 is accessible from obj2 within min_dist and max_dist
csr.clearance(obj, type, dist, omit_objs=[]): to ensure that obj has clearance of dist around it for easy use. type ∈ {{'front', 'sides'}}. omit_objs is a list of objects to ignore while checking clearance.
csr.update(): to update the scene with the constraints.
Typically, this is implemented as part of the for loop to optimize the scene based on the constraints at the end of the scene program.
csr.save(): to save the output of constraint resolution to disk. 

Save scene:
scene.save(path) to save the scene to disk for path.
Export scene:
scene.export() builds and exports scene to disk.
'''