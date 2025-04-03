
# Initialize scene with dimensions appropriate for a small bedroom
scene = Scene(dims=(5, 5, 3))  # Corrected to meet the minimum dimensions of 5x5x3 meters

# Add walls with a soft beige color
scene.add_walls(wall_color='soft beige', floor_texture='carpet', ceiling_texture='white')

# Add windows and doors
scene.place_window('window1', wall='right_wall', type='standard', position='middle', place_curtain=True)  # Corrected position for 'standard' window type
scene.place_door('door1', wall='front_wall', position='left')

# Add furniture
scene.add('bed', desc='A single bed with a simple headboard')
scene.add('nightstand', desc='A small wooden nightstand')
scene.add('dresser', desc='A compact dresser')
scene.add('desk', desc='A small writing desk')
scene.add('chair', desc='A simple wooden chair')

# Place the bed against the left wall at z=1.5, centered
scene.bed.place_global(x='left_wall', y='floor', z=1.5)

# Place the nightstand to the right of the bed with a 0.1-meter gap
scene.nightstand.place_relative(relation='right_of', obj=scene.bed, dist=0.1)  # Corrected relation to 'right_of'

# Place the dresser against the back wall at x=2, facing the front wall
scene.dresser.place_global(x=2, y='floor', z='back_wall', face_towards='front_wall')

# Place the desk against the right wall at z=1, facing the left wall
scene.desk.place_global(x='right_wall', y='floor', z=1, face_towards='left_wall')

# Place the chair along the longer side of the desk
scene.desk.place_seats_rectangular_arrangement(first_longer_side=[scene.chair], second_longer_side=[], first_shorter_side=[], second_shorter_side=[])  # Corrected the method call with required four lists

# Add decor
scene.add('rug', desc='A small area rug')
scene.rug.place_global(x='center', y='floor', z='center')

# Add lighting
scene.add('table_lamp', desc='A small table lamp')
scene.table_lamp.place_relative(relation='on_top_of', obj=scene.nightstand)
scene.add('ceiling_light', desc='A simple ceiling light')
scene.ceiling_light.place_global(x='center', y='ceiling', z='center')
