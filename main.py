from modules.sdl.scene import Scene

# Initialize scene with reduced dimensions suitable for a small bedroom
scene = Scene(dims=(5, 5, 3))  # Width, Depth, Height in meters (height adjusted for occupancy)

# Add walls with a soft beige color
scene.add_walls(wall_color='soft beige', floor_texture='carpet', ceiling_texture='white')

# Add windows and doors
scene.place_window(name='window1', wall='left_wall', type='standard', position='left', place_curtain=True)
scene.place_door(name='door1', wall='front_wall', position='middle')

# Add furniture
scene.add(name='bed', desc='A twin bed')
scene.add(name='nightstand', desc='A small nightstand')
scene.add(name='dresser', desc='A compact dresser')
scene.add(name='desk', desc='A small writing desk')
scene.add(name='chair', desc='A lightweight chair')
scene.add(name='rug1', desc='A decorative rug')

# Place the bed against the back wall at the center
scene.bed.place_global(x='center', y='floor', z='back_wall', delta_x=0.0, delta_y=0.0, delta_z=0.0)

# Place the nightstand to the left of the bed with a 0.1-meter gap
scene.nightstand.place_relative(relation='left_adj', obj=scene.bed, dist=0.1)

# Move the dresser to the front half for better balance and place it against the right wall at z=3.0, facing the left wall
scene.dresser.place_global(x='right_wall', y='floor', z=3.0, face_towards='left_wall', delta_x=0.0, delta_y=0.0, delta_z=0.0)

# Place the desk against the left wall at z=1.5, facing the right wall
scene.desk.place_global(x='left_wall', y='floor', z=1.5, face_towards='right_wall', delta_x=0.0, delta_y=0.0, delta_z=0.59)

# Place the chair along the desk, facing it
scene.desk.place_seats_rectangular_arrangement(first_longer_side=[scene.chair], second_longer_side=[], first_shorter_side=[], second_shorter_side=[])

# Move the rug to balance the scene better in the front half
scene.rug1.place_global(x='center', y='floor', z=2.5, delta_x=0.0, delta_y=0.0, delta_z=0.0)

# Add decor
scene.add(name='painting1', desc='A framed landscape painting')
scene.painting1.place_on_wall(wall='back_wall', horizontal_position='middle', vertical_position='top')

# Add lighting
scene.add(name='table_lamp1', desc='A small table lamp')
scene.table_lamp1.place_relative(relation='on_top_of', obj=scene.nightstand)

scene.add(name='ceiling_light', desc='A ceiling light fixture')
scene.ceiling_light.place_global(x='center', y='ceiling', z='center', delta_x=0.0, delta_y=0.0, delta_z=0.0)

scene.export()
breakpoint()