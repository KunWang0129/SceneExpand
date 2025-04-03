##@##   
'''
Two sofas are arranged in L-shape around a coffee table. First sofa is placed along the back wall while the second one is placed along the left wall. 
In front of the sofas, there is a coffee table which forms the center piece of the room. Right of the table is a single armchair. 
An end table is placed in the corner between the two sofas.'''
##@##
## Initialize scene with dimensions suitable for a living room
scene = Scene(dims=(5, 5, 3))  # Width, Depth, Height in meters
## Add walls with cream white color
scene.add_walls('cream white', 'wooden', 'plain')  # wall color, floor texture, ceiling texture
## Add windows and doors
scene.place_window('window1', wall='left_wall', position='full', type='picture', place_curtain=False)
scene.place_door('door1', wall='front_wall', position='middle')
## Add furniture
scene.add('sofa1', desc='A two-seater sofa')
scene.add('sofa2', desc='A two-seater sofa')
scene.add('coffee_table', desc='A low-profile, rectangular, glass coffee table')
scene.add('armchair', desc='A single armchair')
scene.add('end_table', desc='A small end table')
## Place furniture
# Place sofa1 along the back wall
scene.sofa1.place_global(x=2.5, y='floor', z='back_wall')
# Place the coffee table in front of sofa1 with a gap of 0.5 meters
scene.coffee_table.place_relative(relation='in_front_of', obj=scene.sofa1, dist=0.5)
# Place sofa2 to the left of the coffee table with a distance of 0.45 meters and a sideways shift of 0.2 meters
scene.sofa2.place_relative(relation='left_of', obj=scene.coffee_table, dist=0.45, sideways_shift=0.2, face_towards=scene.coffee_table)
# Place the armchair to the right of the coffee table with a gap of 0.45 meters
scene.armchair.place_relative(relation='right_of', obj=scene.coffee_table, dist=0.45, face_towards=scene.coffee_table)
# Place the end table to the left of sofa1, with a gap of 0.1 meters
scene.end_table.place_relative(relation='left_of', obj=scene.sofa1, dist=0.1)
## Add and place decor
scene.add('plant1', desc='A tall indoor plant')
scene.plant1.place_global(x='right_wall', y='floor', z='back_wall')
scene.add('plant2', desc='A small indoor plant')
scene.plant2.place_relative(relation='on_top_of', obj=scene.coffee_table)
scene.add('decor1', desc='A small decorative item')
scene.decor1.place_relative(relation='on_top_of', obj=scene.coffee_table)
scene.add('rug1', desc='A beautiful area rug')
scene.rug1.place_global(x='center', y='floor', z='center')
## Place wall items
scene.add('painting1', desc='A beautiful painting of a forest')
scene.painting1.place_on_wall('back_wall', horizontal_position='middle', vertical_position='middle')
scene.add('clock1', desc='A wall clock')
scene.clock1.place_on_wall('front_wall', horizontal_position='right', vertical_position='top')
## Add and place lighting
scene.add('table_lamp1', desc='A designer table lamp')
scene.table_lamp1.place_relative(relation='on_top_of', obj=scene.end_table)
scene.add('floor_lamp1', desc='A tall floor lamp')
scene.floor_lamp1.place_global(x='right_wall', y='floor', z='front_wall')
scene.add('floor_lamp2', desc='A tall floor lamp')
scene.floor_lamp2.place_global(x='left_wall', y='floor', z='front_wall')
scene.add('chandelier1', desc='A beautiful chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.sofa1)
csr.access(scene.sofa1, scene.end_table, 0.1, 0.3)
csr.access(scene.sofa1, scene.coffee_table, 0.4, 0.5)
csr.access(scene.sofa2, scene.coffee_table, 0.4, 0.5)
csr.access(scene.armchair, scene.coffee_table, 0.4, 0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
##@##
'''
A sofa is placed against the back wall. There is a coffee table in front of the sofa with a lamp on it. 
To the right of the coffee table is a single armchair. While to the left of the sofa there is a lamp on an end table.
'''
##@##
## Initialize scene with dimensions big appropriate for a living room
scene = Scene(dims=(5,5,3)) ## Width, Depth, Height in meters
## Add walls with cream white color
scene.add_walls('cream white', 'wooden', 'plain')  # wall color, floor texture, ceiling texture
## Add windows and doors 
scene.place_window('window1', wall='right_wall', position='full',type='picture', place_curtain=False)
scene.place_door('door1', wall='front_wall', position='middle')
## Add furniture
scene.add('sofa',desc='A two seater sofa')
scene.add('end_table', desc='Wooden, round, end table')
scene.add('coffee_table', desc='Black coffee table')
scene.add('armchair', desc='Modern armchair in a light cream color')

## Place the sofa against the center of back wall. We will set the x coordinate to be 2.0 given that the room is 4 meters wide.
scene.sofa.place_global(x=2.5, y='floor', z='back_wall')
## Place the coffee table in front of the sofa. Typically, the gap should be between 0.4 to 0.5 meters
scene.coffee_table.place_relative(relation='in_front_of', obj=scene.sofa, dist=0.45)

## Place the armchair to the right of the coffee table. The gap should be between 0.4 to 0.5 meters. It should also face towards the coffee table.
scene.armchair.place_relative(relation='right_of', obj=scene.coffee_table, dist=0.45, face_towards=scene.coffee_table)
## Place the end table to the left adjacent of the sofa. Typical gap between a seat and end table is 0.1 meters for easy access.
scene.get_object('end_table').place_relative(relation='left_adj', obj=scene.sofa, dist=0.1)

## Add decor
scene.add('rug1', desc='A beautiful modern area rug')
scene.rug1.place_global(x='center', y='floor', z='center')
scene.add('painting1', desc='A beautiful painting of snow')
scene.painting1.place_on_wall('back_wall', horizontal_position='middle', vertical_position='middle')
scene.add('painting2', desc='A beautiful painting of fruits')
scene.painting2.place_on_wall('left_wall', horizontal_position='middle', vertical_position='middle')
## Add lighting
# Place the lamp on the coffee table.
scene.add('lamp1', desc='Lamp with a classic design and a beige lampshade')
scene.lamp1.place_relative(relation='on_top_of', obj=scene.coffee_table)
# Place the lamp on the end table
scene.add('lamp2', desc='Silver table lamp')
scene.lamp2.place_relative(relation='on_top_of', obj=scene.end_table)
scene.add('floor_lamp1', desc='A tall floor lamp')
scene.floor_lamp1.place_global(x='right_wall', y='floor', z='front_wall')
scene.add('floor_lamp2', desc='A tall floor lamp')
scene.floor_lamp2.place_global(x='right_wall', y='floor', z='back_wall')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.armchair)
csr.visible(scene.painting2, scene.sofa)
csr.access(scene.sofa, scene.end_table, 0.1, 0.3)
csr.access(scene.sofa, scene.coffee_table, 0.4, 0.5)
csr.access(scene.armchair, scene.coffee_table, 0.4, 0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
##@##
'''
A grey sofa is placed against the back wall. There is a coffee table in front of the sofa. 
To the left of the coffee table is a single armchair. While to the right of the coffee table there is a blue sofa. 
There are two side tables in the room. One is placed to the right of the grey sofa and the other is placed to the left of the blue sofa.
'''
##@##
## Initialize scene with dimensions big appropriate for a living room
scene = Scene(dims=(5,5,3)) ## Width, Depth, Height in meters
## Add walls with a mint green shade
scene.add_walls('mint_green', 'clay_brick', 'white')
## Add windows and doors.
scene.place_window('window1', wall='back_wall', position='middle',type='standard', place_curtain=True)
scene.place_window('window2', wall="right_wall", position='middle', type='standard', place_curtain=True)
scene.place_door('door1', wall='left_wall', position='left')
## Add furniture
scene.add('sofa1', desc='A blue sofa')
scene.add('sofa2', desc='A grey sofa')
scene.add('coffee_table',desc='A rectangular coffee table')
scene.add('armchair',desc='A single armchair')
scene.add('side_table1',desc='A side table')
scene.add('side_table2',desc='A side table')
## Let's begin by placing the grey sofa against the back wall. We can place it against the center of the back wall and have it face the front wall.
scene.sofa2.place_global(x='center', y='floor', z='back_wall', face_towards='front_wall')
## Next, place the coffee table in front of the grey sofa. Typically, the gap should be between 0.4 to 0.5 meters. We can face the table towards the grey sofa.
scene.coffee_table.place_relative(relation='in_front_of', obj=scene.sofa2, dist=0.5, face_towards=scene.sofa2)
## Place the armchair to the left of the coffee table. The gap should be between 0.4 to 0.5 meters. It should also face towards the coffee table.
scene.armchair.place_relative(relation='left_of', obj=scene.coffee_table, dist=0.5, face_towards=scene.coffee_table)
## Place the blue sofa to the right of the coffee table. The gap should be between 0.4 to 0.5 meters. It should also face towards the coffee table.
scene.sofa1.place_relative(relation='right_of', obj=scene.coffee_table, dist=0.5, face_towards=scene.coffee_table)
## Place the first side table to the left of the grey sofa. The gap should be between 0.1 to 0.2 meters so people can reach it from the sofa.
scene.side_table1.place_relative(relation='right_of', obj=scene.sofa2, dist=0.15)
## Place the second side table to the right of the blue sofa. The gap should be between 0.1 to 0.2 meters so people can reach it from the sofa.
scene.side_table2.place_relative(relation='right_of', obj=scene.sofa1, dist=0.15)
## Add decor
# Add a painting along the front wall since there are already things placed along the other walls.
scene.add('painting1', desc='A beautiful painting of a New York skyline')
scene.painting1.place_on_wall('front_wall', horizontal_position='middle', vertical_position='middle')
# Add some plants on top of the coffee tables and end tables
scene.add('plant1', desc='A small plant')
scene.plant1.place_relative(relation='on_top_of', obj=scene.coffee_table)
scene.add('plant2', desc='A small indoor plant')
scene.plant2.place_relative(relation='on_top_of', obj=scene.side_table1)
scene.add('plant3', desc='A small succulent plant')
scene.plant3.place_relative(relation='on_top_of', obj=scene.side_table2)
# Add a clock on the left wall. We can place it in the center since the door is on the left side.
scene.add('clock1', desc='A modern wall clock')
scene.clock1.place_on_wall('left_wall', horizontal_position='middle', vertical_position='top')
# Now, we should add a rug to the room. We can place it in the center of the room.
scene.add('rug1', desc='A beautiful, modern area rug')
scene.rug1.place_global(x='center', y='floor', z='center')
## Add lighting
# Since we have two windows to provide some natural light, we should add one floor lamp to the room along the front wall to provide some additional lighting.
scene.add('floor_lamp1', desc='A tall floor lamp')
# We can place the lamp in the corner next to the front wall and right wall.
scene.floor_lamp1.place_global(x='right_wall', y='floor', z='front_wall')
# Let's also add a hanging chandelier to the room to complete the lighting.
scene.add('chandelier1', desc='A beautiful chandelier')
# Let's hang the chandelier in the center of the room.
scene.chandelier1.place_global(x='center', y='ceiling', z='center')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.sofa1)
csr.visible(scene.painting1, scene.sofa2)
csr.visible(scene.painting1, scene.armchair)
csr.access(scene.sofa1, scene.side_table2, 0.1, 0.3)
csr.access(scene.sofa2, scene.side_table1, 0.1, 0.3)
csr.access(scene.sofa1, scene.coffee_table, 0.4, 0.5)
csr.access(scene.sofa2, scene.coffee_table, 0.4, 0.5)
csr.access(scene.armchair, scene.coffee_table, 0.4, 0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
##@##   
'''
A white sofa is placed against the back wall. There is a square coffee table in front of the sofa. There are two armchairs on each side of the coffee table, looking towards the front wall. An end table is placed to the left of the sofa.
'''
##@##
## Initialize scene with dimensions big appropriate for a living room
scene = Scene(dims=(5,5,3)) ## Width, Depth, Height in meters
## Add walls with sky blue color
scene.add_walls('sky blue', 'wooden', 'plain')  # wall color, floor texture, ceiling texture
## Add windows and doors 
scene.place_window('window1', wall='right_wall', position='left',type='standard', place_curtain=True)
scene.place_window('window2', wall='front_wall', position='full',type='floor_to_ceiling', place_curtain=False)
scene.place_door('door1', wall='left_wall', position='left')
## Add furniture
scene.add("sofa", desc="A white three-seater sofa")
scene.add("armchair1", desc="An armchair")
scene.add("armchair2", desc="An armchair")
scene.add("end_table", desc="Round end table")
scene.add("coffee_table", desc="A square coffee table")
# Place the sofa against the center of back wall. We will set the x coordinate to be 2.0 given that the room is 4 meters wide.
scene.sofa.place_global(x='center', y='floor', z='back_wall')
# Place the coffee table in front of the sofa. Typically, the gap should be between 0.4 to 0.5 meters
scene.coffee_table.place_relative(relation='in_front_of', obj=scene.sofa, dist=0.45)
# Place the armchair to the left of the coffee table. The gap should be between 0.4 to 0.5 meters. It should also face towards the front wall.
scene.armchair1.place_relative(relation='left_of', obj=scene.coffee_table, dist=0.45, face_towards='front_wall')
# Place the armchair to the right of the coffee table. The gap should be between 0.4 to 0.5 meters. It should also face towards the front wall.
scene.armchair2.place_relative(relation='right_of', obj=scene.coffee_table, dist=0.45, face_towards='front_wall')
# Place the end table to the left adjacent of the sofa. Typical gap between a seat and side table is 0.1 meters for easy access.
scene.end_table.place_relative(relation='left_adj', obj=scene.sofa, dist=0.1)
## Add decor
scene.add('plant1', desc='A tall indoor plant')
scene.plant1.place_global(x='right_wall', y='floor', z='back_wall')
scene.add('plant2', desc='A tall indoor plant')
scene.plant2.place_global(x='right_wall', y='floor', z='front_wall')
scene.add('plant3', desc='A small indoor plant')
scene.plant3.place_relative(relation='on_top_of', obj=scene.coffee_table)
scene.add('decor1', desc='An elegant decor item')
scene.decor1.place_relative(relation='on_top_of', obj=scene.coffee_table)
scene.add('painting1', desc='A beautiful painting of a couple sitting in a garden')
scene.add('painting2', desc='A beautiful painting of a dog')
scene.painting1.place_on_wall('back_wall', horizontal_position='middle', vertical_position='middle')
scene.painting2.place_on_wall('right_wall', horizontal_position='middle', vertical_position='middle')
scene.add('rug1', desc='A beautiful area rug')
scene.rug1.place_global(x='center', y='floor', z='center')
scene.add('clock1', desc='A modern wall clock')
scene.clock1.place_on_wall('left_wall', horizontal_position='right', vertical_position='top')
## Add lighting
scene.add('table_lamp1', desc='A designer table lamp')
scene.table_lamp1.place_relative(relation='on_top_of', obj=scene.end_table)
scene.add('floor_lamp1', desc='A tall floor lamp')
scene.floor_lamp1.place_global(x='right_wall', y='floor', z=scene.plant2.z-0.5)
scene.add('chandelier1', desc='A beautiful chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')
scene.add('pendant1', desc='A pendant lamp')
scene.pendant1.place_global(x=scene.end_table.x, y='ceiling', z=scene.end_table.z)
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.sofa)
csr.visible(scene.painting2, scene.armchair1)
csr.visible(scene.painting2, scene.armchair2)
csr.access(scene.sofa, scene.end_table, 0.1, 0.3)
csr.access(scene.sofa, scene.coffee_table, 0.4, 0.5)
csr.access(scene.armchair1, scene.coffee_table, 0.4, 0.5)
csr.access(scene.armchair2, scene.coffee_table, 0.4, 0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
##@##
'''
The dining table is placed in the center of the room aligned with a slight 45 degree offset towards the back right corner. It is surrounded by four chairs. There is a plant on the table. 
There is a sideboard against the right wall. On top of the sideboard, there is a vase with a plant. There is a chandelier in the center of the ceiling.
'''
##@##
## Initialize scene with dimensions big appropriate for a living room
scene = Scene(dims=(5,5,3)) ## Width, Depth, Height in meters
## Add walls with dark color
scene.add_walls('dark blue', 'granite', 'crimson')
## Add windows and doors 
scene.place_window('window1', wall='left_wall', position='full',type='floor_to_ceiling', place_curtain=False)
scene.place_window('window2', wall='back_wall', position='full',type='floor_to_ceiling', place_curtain=True)
scene.place_door('door1', wall='front_wall', position='left')
## Add furniture
scene.add('dining_table',desc='A dining table')
for i in range(4):
    scene.add('chair'+str(i+1), desc='A dining chair')
scene.add('sideboard',desc='Dark brown, long sideboard')
## Place the dining table in the center of the room. We will set the x coordinate to be 2.0 given that the room is 4 meters wide.
scene.dining_table.place_global(x=2, y='floor', z=2)
## Rotate the dining table by 45 degrees
scene.dining_table.set_rotation(45)
## Place chairs on all sides of the dining table in a rectangular arrangement
scene.dining_table.place_seats_rectangular_arrangement(first_longer_side=[scene.chair1], second_longer_side=[scene.chair2], first_shorter_side=[scene.chair3], second_shorter_side=[scene.chair4])
## Place the sideboard against the right wall. We will set the z coordinate to be 2.0 given that the room is 4 meters long.
scene.sideboard.place_global(x='right_wall', y='floor', z=2)
## Add decor
scene.add('plant1', desc='A small green indoor plant')
scene.plant1.place_relative(relation='on_top_of', obj=scene.dining_table)
scene.add('plant2', desc='A small indoor plant')
scene.plant2.place_relative(relation='on_top_of', obj=scene.sideboard)
scene.add('decor1', desc='A bowl with fruits')
scene.decor1.place_relative(relation='on_top_of', obj=scene.sideboard)
scene.add('clock1', desc='A stylish clock')
scene.clock1.place_on_wall('front_wall', horizontal_position='middle', vertical_position='top')
scene.add('painting1', desc='A beautiful painting of a forest')
scene.painting1.place_on_wall('right_wall', horizontal_position='middle', vertical_position='middle')
## Add lighting
scene.add('chandelier1', desc='A stylish, contemporary chandelier chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.chair1)
csr.clearance(scene.sideboard, type='front', dist=0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
##@##
'''
A large bed is placed against the back wall. Two bedside tables are placed on either side of the bed.
An armchair is placed left of the bed, facing the front wall. A dresser is placed against the right and back walls.
'''
##@##
## Initialize scene with dimensions big appropriate for a bedroom
scene = Scene(dims=(5,5,3)) ## Width, Depth, Height in meters
## Add walls with a soft gray shade
scene.add_walls('soft gray', 'wooden', 'white')
## Add windows and doors
scene.place_door('door1', wall='right_wall', position='right')
scene.place_window('window1', wall='left_wall', position='full',type='picture', place_curtain=True)
## Add furniture
scene.add('bed', desc='A double bed')
scene.add('bedside_table1', desc='A round bedside table')
scene.add('bedside_table2', desc='A round bedside table')
scene.add('armchair', desc='A leather armchair')
scene.add('dresser', desc='A wooden dresser')
# Place the bed against the back wall. Since the bed is placed in the center of the back wall and face it towards the front wall
scene.bed.place_global(x='center', y='floor', z='back_wall', face_towards='front_wall')
# Place each beside table along the back wall, on either side of the bed. The gap between the bed and bedside table should be around 0.1 meters.
scene.bedside_table1.place_relative(relation='right_adj', obj=scene.bed, dist=0.1)
scene.bedside_table2.place_relative(relation='left_adj', obj=scene.bed, dist=0.1)
# Place the armchair in front of one of the bedside tables. The gap between the armchair and bedside table should be around 0.25 meters. The armchair should face the front wall.
scene.armchair.place_relative(relation='left_of', obj=scene.bed, dist=0.25, face_towards='front_wall')
# Place the dresser against the right wall in the back corner facing the left wall.
scene.dresser.place_global(x='right_wall', y='floor', z='back_wall', face_towards='left_wall')
## Add decor
scene.add('plant1', desc='A tall indoor plant')
scene.plant1.place_global(x='left_wall', y='floor', z='front_wall')
scene.add('clock1', desc='A wall clock')
scene.clock1.place_on_wall('right_wall', horizontal_position='left', vertical_position='top')
scene.add('painting1', desc='A beautiful painting of an ocean wave')
scene.add('painting2', desc='A beautiful painting of sea animals') 
scene.painting1.place_on_wall('back_wall', horizontal_position='middle', vertical_position='middle')
scene.painting2.place_on_wall('front_wall', horizontal_position='left', vertical_position='middle')
# Place a decor item on top of the wardrobe
scene.add('decor1', desc='A small figurine')
scene.decor1.place_relative(relation='on_top_of', obj=scene.dresser)
## Add lighting
# There is a window on the left for natural lighting. Let's add lamps to the two bedside tables
scene.add('table_lamp1', desc='A designer table lamp')
scene.table_lamp1.place_relative(relation='on_top_of', obj=scene.bedside_table1)
scene.add('table_lamp2', desc='A designer table lamp')
scene.table_lamp2.place_relative(relation='on_top_of', obj=scene.bedside_table2)
# We can also add a hanging chandelier for additional lighting
scene.add('chandelier1', desc='A beautiful chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')
# Let's also add a rug under the bed
scene.add('rug1', desc='A beautiful round area rug')
scene.rug1.place_global(x='center', y='floor', z='center')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.bed)
csr.visible(scene.painting2, scene.armchair)
csr.access(scene.bed, scene.bedside_table1, 0.1, 0.3)
csr.access(scene.bed, scene.bedside_table2, 0.1, 0.3)
csr.clearance(scene.bed, type='sides', dist=0.5, omit_objs=[scene.bedside_table1, scene.bedside_table2])
csr.clearance(scene.sideboard, type='front', dist=0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
##@##   
'''
The bed is positioned against the center of right wall flanked by two nightstands. A dresser is placed against the left wall.
'''
##@##  
## Initialize scene with dimensions big appropriate for a bedroom
scene = Scene(dims=(5, 5, 3))  # Width, Depth, Height in meters
## Add walls with Light Lavender color
scene.add_walls(wall_color='Light Lavender', floor_texture='wooden', ceiling_texture='plain')  # wall color as a descriptive string, with floor and ceiling textures
## Add windows and doors
scene.place_window('window1', wall='back_wall', position='full', type='floor_to_ceiling', place_curtain=False)
scene.place_door('door1', wall='front_wall', position='middle')
## Add furniture
scene.add('bed', desc='Bed featuring a navy blue comforter with a nautical theme, including illustrations of boats and sea life')
scene.add('nightstand1', desc='Dark brown, rectangular nightstand')
scene.add('nightstand2', desc='Dark brown, rectangular nightstand')
scene.add('dresser', desc='Tall, dark brown dresser with multicolored drawers')
# Place the bed against the right wall in the center and facing the left wall
scene.bed.place_global(x='right_wall', y='floor', z='center', face_towards='left_wall')
# Place nightstands adjacent to the left and right of the bed
scene.nightstand1.place_relative(relation='left_adj', obj=scene.bed, dist=0.1)
scene.nightstand2.place_relative(relation='right_adj', obj=scene.bed, dist=0.1)
# Place the dresser against the left wall in the center
scene.dresser.place_global(x='left_wall', y='floor', z='center')
## Add decor
scene.add('plant1', desc='A tall indoor plant')
scene.plant1.place_global(x='left_wall', y='floor', z='back_wall')
scene.add('plant2', desc='A tall indoor plant')
scene.plant2.place_global(x='left_wall', y='floor', z='front_wall')
scene.add('plant3', desc='A small indoor plant')
scene.plant3.place_relative(relation='on_top_of', obj=scene.dresser)
scene.add('decor1', desc='An elegant decor item')
scene.decor1.place_relative(relation='on_top_of', obj=scene.dresser)
scene.add('painting1', desc='A beautiful scenery of the Milky Way')
scene.painting1.place_on_wall('right_wall', horizontal_position='middle', vertical_position='middle')
scene.add('painting2', desc='A beautiful painting of the solar system')
scene.painting2.place_on_wall('left_wall', horizontal_position='middle', vertical_position='middle')
scene.add('rug1', desc='A beautiful area rug')
scene.rug1.place_global(x='center', y='floor', z='center')
scene.add('clock1', desc='A stylish wall clock')
scene.clock1.place_on_wall('front_wall', horizontal_position='right', vertical_position='top')
## Add lighting
scene.add('table_lamp1', desc='A designer table lamp')
scene.table_lamp1.place_relative(relation='on_top_of', obj=scene.nightstand1)
scene.add('table_lamp2', desc='A designer table lamp')
scene.table_lamp2.place_relative(relation='on_top_of', obj=scene.nightstand2)
scene.add('floor_lamp1', desc='A tall floor lamp')
scene.floor_lamp1.place_global(x='right_wall', y='floor', z='front_wall')
scene.add('chandelier1', desc='A beautiful chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.bed)
csr.visible(scene.painting2, scene.bed)
csr.access(scene.bed, scene.nightstand1, 0.1, 0.3)
csr.access(scene.bed, scene.nightstand2, 0.1, 0.3)
csr.clearance(scene.dresser, type='front', dist=0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
csr.clearance(scene.bed, type='sides', dist=0.5, omit_objs=[scene.nightstand1, scene.nightstand2])
##$##
##@##
'''
A desk is placed against the left wall. There is a chair in front of the desk. There is a tall cabinet placed along the left and back walls with a lamp on top of it. There is a credenza placed against the back wall. On top of the credenza, there is a white vase and two glass vases.
'''
##@##
## Initialize scene with dimensions big appropriate for a living room
scene = Scene(dims=(5,5,3)) ## Width, Depth, Height in meters
## Add walls with a sandy brown shade
scene.add_walls(wall_color='sandy brown', floor_texture='wooden', ceiling_texture='plain')

## Add walls with sandy brown shade
scene.place_window('window1', wall='left_wall', position='full', type='standard', place_curtain=True)
## Add windows and doors 
scene.place_window('window1', wall='left_wall', position='full',type='standard', place_curtain=True)
scene.place_door('door1', wall='front_wall', position='middle')
## Add furniture
scene.add('desk', desc='Rectangular desk')
scene.add('chair', desc='Wooden chair with a slatted back and a brown cushion')
scene.add('cabinet', desc='Tall wooden cabinet with a simple design')
scene.add('credenza', desc='Wooden credenza with sliding glass doors')
scene.add('sideboard', desc='A wooden sideboard with a simple design')

# Place the desk against the left wall. We will set the z coordinate to be 2.0 given that the room is 4 meters long.
scene.desk.place_global(x='left_wall', y='floor', z=2)
# Place the chair along the first longer side of the desk.
scene.desk.place_seats_rectangular_arrangement(first_longer_side=[scene.chair])
# Place the cabinet against the left wall and back wall. The cabinet faces the right wall.
scene.cabinet.place_global(x='left_wall', y='floor', z='back_wall', face_towards='right_wall')
# Place the credenza against the back wall. We will set the x coordinate to be 2.0 given that the room is 4 meters wide.
scene.credenza.place_global(x=2, y='floor', z='back_wall')
# Place the sideboard against the right wall. We will set the z coordinate to be 2.0 given that the room is 4 meters wide.
scene.sideboard.place_global(x='right_wall', y='floor', z=2)
                   
## Add decor
scene.add('rug1', desc='A white rug')
scene.rug1.place_global(x='center', y='floor', z='center')

# Place a painting on the back wall and one on the right wall
scene.add('painting1', desc='A beautiful abstract art painting')
scene.painting1.place_on_wall('back_wall', horizontal_position='middle', vertical_position='middle')
scene.add('painting2', desc='A beautiful painting of a lake')
scene.painting2.place_on_wall('right_wall', horizontal_position='middle', vertical_position='middle')

# Add a clock on the front wall
scene.add('clock1', desc='A modern wall clock')
scene.clock1.place_on_wall('front_wall', horizontal_position='right', vertical_position='top')

scene.add('white_vase', desc='A small white vase')
scene.add('glass_vase1', desc='small glass vase')
scene.add('glass_vase2', desc='Tall glass vase with red flowers')

for i in range(3):
    if i == 0:
        scene.get_object('white_vase').place_relative(relation='on_top_of', obj=scene.credenza)
    else:
        scene.get_object('glass_vase'+str(i)).place_relative(relation='on_top_of', obj=scene.credenza)

scene.add('white_vase2', desc='A small white vase')
scene.get_object('white_vase2').place_relative(relation='on_top_of', obj=scene.cabinet)

## Add lighting
# Place a lamp on top of the cabinet
scene.add('lamp1', desc='Lamp with a classic design and a beige lampshade')
scene.lamp1.place_relative(relation='on_top_of', obj=scene.cabinet)
# Place a floor lamp near the front wall
scene.add('lamp2', desc='A tall silver standing lamp')
scene.lamp2.place_global(x='left_wall', y='floor', z='front_wall')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.chair)
csr.visible(scene.painting2, scene.chair)
csr.access(scene.desk, scene.chair, 0.1, 0.3)
csr.clearance(scene.cabinet, type='front', dist=0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
##@##
'''
A wide five seater sofa is placed against the back wall with end tables on either side. In front of the sofa is a rectangular coffee table. 
There are two upholstered armchairs on the left side of the coffee table and two wooden armchairs, with another end table in between them, on the right side of the coffee table. 
'''
##@##
## Initialize scene with dimensions appropriate for a living room
scene = Scene(dims=(7, 7, 4))  # Width, Depth, Height in meters

## Add walls with a pale yellow shade
scene.add_walls(wall_color='pale yellow', floor_texture='wooden', ceiling_texture='plain')

## Add windows and doors
scene.place_door('door1', wall='front_wall', position='middle')
scene.place_window('window1', wall='right_wall', position='full', type='floor_to_ceiling', place_curtain=False)

## Add objects (furniture) to the scene
scene.add('sofa', desc='A wide five-seater sofa')
for i in range(2):
    scene.add(f'upholstered_armchair{i+1}', desc='A brown, upholstered armchair')
    scene.add(f'wooden_armchair{i+1}', desc='A wooden armchair')
scene.add('coffee_table', desc='Rectangular coffee table made of marble')
for i in range(3):
    scene.add(f'end_table{i+1}', desc='A small round, marble end table')

# Place the sofa against the back wall centered at x=2.5, facing the front wall
scene.sofa.place_global(x='center', y='floor', z='back_wall', face_towards='front_wall')
scene.end_table1.place_relative(relation='left_adj', obj=scene.sofa, dist=0.1)
scene.end_table2.place_relative(relation='right_adj', obj=scene.sofa, dist=0.1)
scene.coffee_table.place_relative(relation='in_front_of', obj=scene.sofa, dist=1.0)

# Place wooden armchairs and end table to the right of the coffee table, facing left
x_coordinate = scene.coffee_table.x + 0.5 + (scene.wooden_armchair1.width/2 + scene.coffee_table.width/2)
scene.wooden_armchair1.place_global(x=x_coordinate, z=2.0, face_towards='left_wall')
z_coordinate = scene.wooden_armchair1.z + 0.5 + scene.wooden_armchair1.depth/2 + scene.end_table3.depth/2
scene.end_table3.place_global(x=x_coordinate, z=z_coordinate, face_towards='left_wall')
z_coordinate = scene.end_table3.z + 0.5 + scene.end_table3.depth/2 + scene.wooden_armchair2.depth/2
scene.wooden_armchair2.place_global(x=x_coordinate, z=z_coordinate, face_towards='left_wall')

# Place upholstered armchairs to the left of the coffee table, facing right
x_coordinate = scene.coffee_table.x - 0.5 - (scene.upholstered_armchair1.width/2 + scene.coffee_table.width/2)
scene.upholstered_armchair1.place_global(x=x_coordinate, z=scene.wooden_armchair1.z, face_towards='right_wall')
scene.upholstered_armchair2.place_global(x=x_coordinate, z=scene.wooden_armchair2.z, face_towards='right_wall')

## Add decor
scene.add('plant1', desc='A plant with several flowers')
scene.plant1.place_relative(relation='on_top_of', obj=scene.end_table1)
scene.add('plant2', desc='A plant with several flowers')
scene.plant2.place_relative(relation='on_top_of', obj=scene.end_table2)
scene.add('plant3', desc='A small potted plant')
scene.plant3.place_relative(relation='on_top_of', obj=scene.end_table3)
scene.add('painting1', desc='A painting of the Grand Canyon')
scene.painting1.place_on_wall('back_wall', horizontal_position='middle', vertical_position='middle')
scene.add('painting2', desc='Abstract art painting')
scene.painting2.place_on_wall('left_wall', horizontal_position='middle', vertical_position='middle')
scene.add('clock1', desc='A modern wall clock')
scene.clock1.place_on_wall('front_wall', horizontal_position='middle', vertical_position='top')
scene.add('floor_lamp1', desc='A tall floor lamp')
scene.floor_lamp1.place_global(x='left_wall', y='floor', z='front_wall')
scene.add('floor_lamp2', desc='A modern floor lamp')
scene.floor_lamp2.place_global(x='right_wall', y='floor', z='back_wall')
scene.add('floor_lamp3', desc='A modern floor lamp')
scene.floor_lamp3.place_global(x='left_wall', y='floor', z='back_wall')
scene.add('chandelier1', desc='A chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')
scene.add('rug1', desc='A rectangular area rug')
scene.rug1.place_global(x='center', y='floor', z='center')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.sofa)
csr.visible(scene.painting2, scene.sofa)
csr.access(scene.sofa, scene.end_table1, 0.1, 0.3)
csr.access(scene.sofa, scene.end_table2, 0.1, 0.3)
csr.access(scene.sofa, scene.coffee_table, 0.4, 0.5)
csr.access(scene.upholstered_armchair1, scene.coffee_table, 0.4, 0.5)
csr.access(scene.upholstered_armchair2, scene.coffee_table, 0.4, 0.5)
csr.access(scene.wooden_armchair1, scene.coffee_table, 0.4, 0.5)
csr.access(scene.wooden_armchair2, scene.coffee_table, 0.4, 0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
##@##   
'''
A wooden dining table is placed against the left wall with two chairs on either of its long side. The chairs are placed such they are aligned with respect to the back wall. There is a cabinet placed against the back and left wall. 
'''
##@##
## Initialize scene with dimensions appropriate for a dining room
scene = Scene(dims=(5, 5, 3))  # Width, Depth, Height in meters

## Add walls with Light Lavender color
scene.add_walls(wall_color='light lavender', floor_texture='wooden', ceiling_texture='plain')

## Add windows and doors
scene.place_window('window1', wall='right_wall', position='full', type='picture', place_curtain=False)
scene.place_door('door1', wall='front_wall', position='left')

## Add furniture
scene.add('dining_table', desc='A wooden dining table')
for i in range(4):
    scene.add(f'chair{i+1}', desc='A wooden chair')
scene.add('cabinet', desc='A small wooden cabinet')

# Place the dining table against the left wall, centered at z=2
scene.dining_table.place_global(x='left_wall', y='floor', z=2, face_towards='front_wall')
scene.cabinet.place_global(x='left_wall', y='floor', z='back_wall', face_towards='front_wall')
first_length = [scene.get_object(f'chair{i+1}') for i in range(2)]
second_length = [scene.get_object(f'chair{i+3}') for i in range(2)]
scene.dining_table.place_seats_rectangular_arrangement(first_longer_side=first_length, second_longer_side=second_length)

## Add decor
for i in range(2):
    scene.add(f'small_plant{i+1}', desc='A small decorative indoor plant')
    scene.get_object(f'small_plant{i+1}').place_relative(relation='on_top_of', obj=scene.dining_table)
    scene.add(f'decor{i+1}', desc='A decorative item')
    scene.get_object(f'decor{i+1}').place_relative(relation='on_top_of', obj=scene.cabinet)
scene.add('plant1', desc='A tall indoor plant')
scene.plant1.place_global(x='right_wall', y='floor', z='back_wall')
scene.add('plant2', desc='A tall indoor plant')
scene.plant2.place_global(x='right_wall', y='floor', z='front_wall')
scene.add('painting1', desc='A painting of forests and wildlife')
scene.painting1.place_on_wall('left_wall', horizontal_position='middle', vertical_position='middle')
scene.add('painting2', desc='A solar system painting')
scene.painting2.place_on_wall('back_wall', horizontal_position='middle', vertical_position='middle')
scene.add('painting3', desc='A solar system painting')
scene.painting3.place_on_wall('front_wall', horizontal_position='middle', vertical_position='middle')
scene.add('rug1', desc='An area rug')
scene.rug1.place_global(x='center', y='floor', z='center')
scene.add('clock1', desc='A wall clock')
scene.clock1.place_on_wall('front_wall', horizontal_position='right', vertical_position='top')
scene.add('chandelier1', desc='A chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.chair1)
csr.visible(scene.painting2, scene.chair1)
csr.visible(scene.painting3, scene.chair1)
csr.clearance(scene.cabinet, type='front', dist=0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
##@##
'''
A dining and living arrangement. A sofa is placed against the back wall.
A coffee table is placed in front of the sofa. An armchair is placed to the right of the coffee table.
A cabinet is placed against the back wall left of the sofa. A dining table is placed in front of the coffee table.
Four chairs are placed around the dining table, two on either side. A vase is placed on the dining table.
'''
##@##
## Initialize scene with dimensions appropriate for a dining-living room
scene = Scene(dims=(7, 6, 3))  # Width, Depth, Height in meters

## Add walls with a slate blue color
scene.add_walls(wall_color='slate blue', floor_texture='wooden', ceiling_texture='plain')

## Add windows and doors
scene.place_window('window1', wall='back_wall', position='full', type='picture', place_curtain=False)
scene.place_door('door1', wall='right_wall', position='right')
scene.place_door('door2', wall='left_wall', position='left')

## Add objects (furniture) to the scene
scene.add('sofa', desc='A wide three-seater sofa')
scene.add('coffee_table', desc='A round coffee table')
scene.add('armchair', desc='A comfortable armchair')
scene.add('cabinet', desc='A short but wide cabinet')
scene.add('dining_table', desc='A rectangular dining table')
for i in range(4):
    scene.add(f'chair{i+1}', desc='A dining chair')

# Place the sofa against the back wall at x=3.5, facing the front wall
scene.sofa.place_global(x=3.5, y='floor', z='back_wall', face_towards='front_wall')

# Place the coffee table in front of the sofa with a 0.45-meter gap, facing the sofa
scene.coffee_table.place_relative(relation='in_front_of', obj=scene.sofa, dist=0.45, face_towards=scene.sofa)

# Place the armchair to the right of the coffee table with a 0.45-meter gap, facing the coffee table
scene.armchair.place_relative(relation='right_of', obj=scene.coffee_table, dist=0.45, face_towards=scene.coffee_table)

# Place the cabinet to the left of the sofa along the back wall, with a 0.2-meter gap, facing the front wall
scene.cabinet.place_relative(relation='left_of', obj=scene.sofa, dist=0.2, face_towards='front_wall')
scene.cabinet.place_global(x=scene.cabinet.x, y='floor', z='back_wall')  # Place cabinet against the back wall

# Place the dining table behind the coffee table, at a distance of 1.2 meters, facing the back wall
scene.dining_table.place_relative(relation='behind_of', obj=scene.coffee_table, dist=1.2, face_towards='back_wall')

# Place chairs along the longer sides of the dining table
scene.dining_table.place_seats_rectangular_arrangement(first_longer_side=[scene.chair1, scene.chair2], second_longer_side=[scene.chair3, scene.chair4])

## Add decor
# Plants on top of the coffee table and dining table
scene.add('plant1', desc='A small potted plant')
scene.plant1.place_relative(relation='on_top_of', obj=scene.coffee_table)
scene.add('plant2', desc='A small potted succulent')
scene.plant2.place_relative(relation='on_top_of', obj=scene.dining_table)

# Sculptures on top of the cabinet
scene.add('decor1', desc='A small sculpture')
scene.decor1.place_relative(relation='on_top_of', obj=scene.cabinet)
scene.add('decor2', desc='A small vase')
scene.decor2.place_relative(relation='on_top_of', obj=scene.cabinet)

# Add a painting on the front wall
scene.add('painting1', desc='A painting of the beach')
scene.painting1.place_on_wall('front_wall', horizontal_position='middle', vertical_position='middle')

# Add a clock on the left wall
scene.add('clock1', desc='A modern wall clock')
scene.clock1.place_on_wall('left_wall', horizontal_position='right', vertical_position='top')

## Add lighting
scene.add('floor_lamp1', desc='A tall floor lamp')
scene.floor_lamp1.place_global(x='right_wall', y='floor', z='back_wall')
scene.add('chandelier1', desc='A chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')

# Add a rug under the sofa along the back wall
scene.add('rug1', desc='A rectangular area rug')
scene.rug1.place_global(x='center', y='floor', z='back_wall')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.sofa)
csr.access(scene.sofa, scene.coffee_table, 0.4, 0.5)
csr.access(scene.armchair, scene.coffee_table, 0.4, 0.5)
csr.clearance(scene.cabinet, type='front', dist=0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##

##@##
'''
A living room scene consists of a sofa placed against the back wall. A coffee table is placed in front of the sofa. An armchair is placed to the right of the coffee table. A plant is placed on top of the coffee table. An end table is placed to the right of the sofa. A tv cabinet is placed against the front wall. A tv is placed on top of the tv cabinet.
'''
##@##
## Initialize scene with dimensions suitable for a living room
scene = Scene(dims=(5, 5, 3))  # Width, Depth, Height in meters

## Add walls with cream white color
scene.add_walls(wall_color='cream white', floor_texture='wooden', ceiling_texture='plain')

## Add windows and doors
scene.place_window('window1', wall='right_wall', position='full', type='picture', place_curtain=True)
scene.place_door('door1', wall='left_wall', position='left')

## Add furniture
scene.add('sofa1', desc='L-shaped sofa')
scene.add('armchair', desc='A comfortable armchair')
scene.add('coffee_table', desc='A square coffee table')
scene.add('end_table', desc='A small end table')
scene.add('tv_cabinet', desc='A small but wide TV cabinet')
scene.add('tv', desc='A large TV')

# Place the sofa against the back wall at x=2, centered
scene.sofa1.place_global(x=2, y='floor', z='back_wall')

# Place the coffee table in front of the sofa with a 0.45-meter gap
scene.coffee_table.place_relative(relation='in_front_of', obj=scene.sofa1, dist=0.45)

# Place the armchair to the right of the coffee table with a 0.45-meter gap, facing the coffee table
scene.armchair.place_relative(relation='right_of', obj=scene.coffee_table, dist=0.45, face_towards=scene.coffee_table)

# Place the end table to the right of the sofa with a 0.1-meter gap
scene.end_table.place_relative(relation='right_of', obj=scene.sofa1, dist=0.1)

# Place the TV cabinet against the front wall at x=2
scene.tv_cabinet.place_global(x=2, y='floor', z='front_wall')

# Place the TV on top of the TV cabinet, facing the back wall
scene.tv.place_relative(relation='on_top_of', obj=scene.tv_cabinet, face_towards='back_wall')

## Add decor
scene.add('rug1', desc='A white area rug')
scene.rug1.place_global(x='center', y='floor', z='center')
scene.add('painting1', desc='A beautiful painting of a horse')
scene.painting1.place_on_wall('left_wall', horizontal_position='middle', vertical_position='middle')

# Add a small plant on top of the coffee table
scene.add('plant1', desc='A small indoor plant')
scene.plant1.place_relative(relation='on_top_of', obj=scene.coffee_table)

## Add lighting
scene.add('chandelier1', desc='A beautiful chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.sofa1)
csr.visible(scene.tv, scene.sofa)
csr.access(scene.sofa1, scene.coffee_table, 0.4, 0.5)
csr.access(scene.armchair, scene.coffee_table, 0.4, 0.5)
cs.access(scene.end_table, scene.sofa1, 0.1, 0.3)
csr.clearance(scene.tv_cabinet, type='front', dist=0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
##@##
'''
A bed is placed against the back wall with bedside tables on either side. A lamp is placed on each bedside table. A wardrobe is placed against the right wall. A desk and a chair are placed to the right of the wardrobe.
'''
##@##
## Initialize scene with dimensions appropriate for a bedroom
scene = Scene(dims=(5, 5, 3))  # Width, Depth, Height in meters

## Add walls with cream white color
scene.add_walls(wall_color='cream white', floor_texture='wooden', ceiling_texture='plain')

## Add windows and doors
scene.place_window('window1', wall='left_wall', position='full', type='picture', place_curtain=False)
scene.place_door('door1', wall='front_wall', position='left')

## Add furniture
scene.add('bed', desc='A king-sized bed')
scene.add('bedside_table1', desc='A bedside table')
scene.add('bedside_table2', desc='A bedside table')
scene.add('wardrobe', desc='A wardrobe')
scene.add('desk', desc='A desk')
scene.add('chair', desc='A chair')

# Place the bed against the back wall at x=2, centered
scene.bed.place_global(x=2, y='floor', z='back_wall')

# Place the bedside tables on either side of the bed with a 0.1-meter gap
scene.bedside_table1.place_relative(relation='left_adj', obj=scene.bed, dist=0.1)
scene.bedside_table2.place_relative(relation='right_adj', obj=scene.bed, dist=0.1)

# Place the wardrobe against the right wall at z=1.7
scene.wardrobe.place_global(x='right_wall', y='floor', z=1.7)

# Place the desk to the right of the wardrobe with a 0.3-meter gap, facing the right wall
scene.desk.place_relative(relation='right_of', obj=scene.wardrobe, dist=0.3)

# Place the chair along the long side of the desk
scene.desk.place_seats_rectangular_arrangement(first_longer_side=[scene.chair])

## Add decor
scene.add('rug1', desc='A dark area rug')
scene.rug1.place_global(x='center', y='floor', z='center')
scene.add('clock1', desc='A wall clock')
scene.clock1.place_on_wall('front_wall', horizontal_position='right', vertical_position='top')

## Add lighting
scene.add('pendant1', desc='A large modern pendant light')
scene.pendant1.place_global(x='center', y='ceiling', z='center')

# Place lamps on each bedside table
scene.add('lamp1', desc='A table lamp')
scene.lamp1.place_relative(relation='on_top_of', obj=scene.bedside_table1)
scene.add('lamp2', desc='A table lamp')
scene.lamp2.place_relative(relation='on_top_of', obj=scene.bedside_table2)
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.clock1, scene.bed)
csr.access(scene.bed, scene.bedside_table1, 0.1, 0.3)
csr.access(scene.bed, scene.bedside_table2, 0.1, 0.3)
csr.clearance(scene.wardrobe, type='front', dist=0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
csr.clearance(scene.bed, type='sides', dist=0.5, omit_objs=[scene.bedside_table1, scene.bedside_table2])
##$##
##@##
'''
A sofa is placed against the back wall with end tables on either side. There is a plant on each end table. A coffee table is placed in front of the sofa. There are armchairs on either side of the coffee table. A pair of ottomans are placed in front of the coffee table. A TV cabinet is placed against the front wall. A TV is placed on the TV cabinet. A chandelier is placed in the center of the room.
'''
##@##
## Initialize scene with dimensions appropriate for a living room
scene = Scene(dims=(5, 6, 3))  # Width, Depth, Height in meters

## Add walls with cream white color
scene.add_walls(wall_color='cream white', floor_texture='wooden', ceiling_texture='plain')

## Add windows and doors
scene.place_window('window1', wall='right_wall', position='full', type='picture', place_curtain=False)
scene.place_door('door1', wall='left_wall', position='left')

## Add furniture
scene.add('sofa', desc='A sofa with a curved back')
scene.add('coffee_table', desc='A coffee table')
scene.add('tv_cabinet', desc='A TV cabinet')
scene.add('tv', desc='A TV')

for i in range(2):
    scene.add(f'end_table{i+1}', desc='A small end table')
    scene.add(f'armchair{i+1}', desc='An armchair')
    scene.add(f'ottoman{i+1}', desc='An ottoman')

# Place the sofa against the back wall at x=2.5, centered
scene.sofa.place_global(x=2.5, y='floor', z='back_wall')

# Place end tables on either side of the sofa with a 0.1-meter gap
scene.end_table1.place_relative(relation='left_of', obj=scene.sofa, dist=0.1)
scene.end_table2.place_relative(relation='right_of', obj=scene.sofa, dist=0.1)

# Place the coffee table in front of the sofa with a 0.45-meter gap
scene.coffee_table.place_relative(relation='in_front_of', obj=scene.sofa, dist=0.45)

# Place the armchairs on either side of the coffee table, each with a 0.45-meter gap, facing the table
scene.armchair1.place_relative(relation='left_of', obj=scene.coffee_table, dist=0.45, face_towards=scene.coffee_table)
scene.armchair2.place_relative(relation='right_of', obj=scene.coffee_table, dist=0.45, face_towards=scene.coffee_table)

# Place the ottomans in front of the coffee table with a 0.45-meter gap and sideways shifts for alignment
scene.ottoman1.place_relative(relation='in_front_of', obj=scene.coffee_table, dist=0.45, sideways_shift=0.4, face_towards=scene.coffee_table)
scene.ottoman2.place_relative(relation='in_front_of', obj=scene.coffee_table, dist=0.45, sideways_shift=-0.4, face_towards=scene.coffee_table)

# Place the TV cabinet against the front wall at x=2.5
scene.tv_cabinet.place_global(x=2.5, y='floor', z='front_wall')

# Place the TV on top of the TV cabinet, facing the back wall
scene.tv.place_relative(relation='on_top_of', obj=scene.tv_cabinet, face_towards='back_wall')

## Add decor
scene.add('painting1', desc='A beautiful painting of a horse')
scene.painting1.place_on_wall('back_wall', horizontal_position='middle', vertical_position='middle')

# Place plants on top of each end table
for i in range(2):
    scene.add(f'plant{i+1}', desc='A small indoor plant')
    scene.get_object(f'plant{i+1}').place_relative(relation='on_top_of', obj=scene.get_object(f'end_table{i+1}'))

# Add a rug in the center of the room
scene.add('rug1', desc='A beautiful white area rug')
scene.rug1.place_global(x='center', y='floor', z='center')

# Add a clock on the left wall
scene.add('clock1', desc='A modern wall clock')
scene.clock1.place_on_wall('left_wall', horizontal_position='right', vertical_position='top')

## Add lighting
scene.add('chandelier1', desc='A large chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')

# Add floor lamps near the front wall
scene.add('lamp1', desc='A tall silver standing lamp')
scene.lamp1.place_global(x='left_wall', y='floor', z='front_wall')
scene.add('lamp2', desc='A tall silver standing lamp')
scene.lamp2.place_global(x='right_wall', y='floor', z='front_wall')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.sofa)
csr.visible(scene.tv, scene.sofa)
csr.access(scene.sofa, scene.coffee_table, 0.4, 0.5)
csr.access(scene.armchair1, scene.coffee_table, 0.4, 0.5)
csr.access(scene.armchair2, scene.coffee_table, 0.4, 0.5)
csr.clearance(scene.tv_cabinet, type='front', dist=0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
##@##
'''
A bed is placed against the back wall with a bedside table on the left. A cabinet is placed against the left wall.
A desk and a chair are placed to the right of the bed, placed against the back wall.
'''
##@##
## Initialize scene with dimensions suitable for a bedroom
scene = Scene(dims=(6, 5, 3))  # Width, Depth, Height in meters

## Add walls with a light lavender shade
scene.add_walls(wall_color='light lavender', floor_texture='wooden', ceiling_texture='plain')

## Add windows and doors
scene.place_window('window1', wall='right_wall', position='full', type='picture', place_curtain=True)
scene.place_door('door1', wall='left_wall', position='left')

## Add objects (furniture) to the scene
scene.add('bed', desc='A double bed')
scene.add('bedside_table', desc='A bedside table')
scene.add('cabinet', desc='A cabinet')
scene.add('desk', desc='A desk')
scene.add('chair', desc='A chair')

# Place the bed against the back wall at x=2.5
scene.bed.place_global(x=2.5, y='floor', z='back_wall')

# Place the bedside table to the left of the bed with a 0.1-meter gap
scene.bedside_table.place_relative(relation='left_adj', obj=scene.bed, dist=0.1)

# Place the cabinet against the left wall at z=2, facing the right wall
scene.cabinet.place_global(x='left_wall', y='floor', z=2, face_towards='right_wall')

# Place the desk to the right of the bed against the back wall with a 0.1-meter gap, facing the front wall
scene.desk.place_relative(relation='right_of', obj=scene.bed, dist=0.1, face_towards='front_wall')
scene.desk.place_global(x=scene.desk.x, y='floor', z='back_wall')

# Place the chair along the long side of the desk
scene.desk.place_seats_rectangular_arrangement(first_longer_side=[scene.chair])

## Add decor
# Place a plant on top of the cabinet
scene.add('plant1', desc='A small potted succulent')
scene.plant1.place_relative(relation='on_top_of', obj=scene.cabinet)

# Place a sculpture on the cabinet and a vase on the desk
scene.add('decor1', desc='A small sculpture')
scene.decor1.place_relative(relation='on_top_of', obj=scene.cabinet)
scene.add('decor2', desc='A small vase')
scene.decor2.place_relative(relation='on_top_of', obj=scene.desk)

# Add paintings on the back and front walls
scene.add('painting1', desc='A beautiful painting of space')
scene.painting1.place_on_wall('back_wall', horizontal_position='middle', vertical_position='middle')
scene.add('painting2', desc='A painting of a forest')
scene.painting2.place_on_wall('front_wall', horizontal_position='middle', vertical_position='middle')

## Add lighting
scene.add('table_lamp1', desc='A designer table lamp')
scene.table_lamp1.place_relative(relation='on_top_of', obj=scene.bedside_table)
scene.add('floor_lamp1', desc='A tall floor lamp')
scene.floor_lamp1.place_global(x='right_wall', y='floor', z='front_wall')
scene.add('chandelier1', desc='A beautiful glass chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')

# Add a rug under the bed
scene.add('rug1', desc='A rectangular area rug')
scene.rug1.place_global(x='center', y='floor', z='center')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.bed)
csr.visible(scene.painting2, scene.bed)
csr.access(scene.bed, scene.bedside_table, 0.1, 0.3)
csr.access(scene.desk, scene.chair, 0.1, 0.3)
csr.clearance(scene.cabinet, type='front', dist=0.5)
csr.clearance(scene.door1, type='front', dist=1.0)
csr.clearance(scene.bed, type='sides', dist=0.5, omit_objs=[scene.bedside_table])
##$##
##@##
'''
A round table is placed in the center left of the room with four chairs around it.
A rectangular table is placed against the right wall with two chairs on one side.
A pair of ottomans are placed at some distance from the front wall.
'''
##@##
## Initialize scene with dimensions appropriate for a dining room
scene = Scene(dims=(6, 5, 3))  # Width, Depth, Height in meters

## Add walls with a tea rose pink shade
scene.add_walls(wall_color='tea rose pink', floor_texture='wooden', ceiling_texture='plain')

## Add windows and doors
scene.place_window('window1', wall='left_wall', position='full', type='floor_to_ceiling', place_curtain=True)
scene.place_window('window2', wall='back_wall', position='left', type='standard', place_curtain=True)
scene.place_door('door1', wall='back_wall', position='right')

## Add objects (furniture) to the scene
scene.add('round_table', desc='A round table')
for i in range(6):
    scene.add(f'chair{i+1}', desc='A chair')
scene.add('rectangular_table', desc='A small rectangular table')
for i in range(2):
    scene.add(f'ottoman{i+1}', desc='An ottoman')

# Place the round table in the center left of the room at x=1.75, z=2
scene.round_table.place_global(x=1.75, y='floor', z=2)

# Place four chairs around the round table
scene.round_table.place_seats_around_round_arrangement(list_of_seats=[scene.get_object(f'chair{i+1}') for i in range(4)])

# Place the rectangular table against the right wall at z=3, facing the back wall
scene.rectangular_table.place_global(x='right_wall', y='floor', z=3.0, face_towards='back_wall')

# Place two chairs along the long side of the rectangular table
scene.rectangular_table.place_seats_rectangular_arrangement(first_longer_side=[scene.chair5, scene.chair6])

# Place the ottomans near the front wall with a sideways shift for alignment
scene.ottoman1.place_global(x=1.7, y='floor', z='front_wall')
scene.ottoman2.place_global(x=2.3, y='floor', z='front_wall')

## Add decor
# Place plants on top of each table
scene.add('plant1', desc='A small potted succulent')
scene.plant1.place_relative(relation='on_top_of', obj=scene.round_table)
scene.add('plant2', desc='A small potted plant')
scene.plant2.place_relative(relation='on_top_of', obj=scene.rectangular_table)

# Add paintings on the right and front walls
scene.add('painting1', desc='A beautiful painting of plants')
scene.painting1.place_on_wall('right_wall', horizontal_position='middle', vertical_position='middle')
scene.add('painting2', desc='A painting of snow')
scene.painting2.place_on_wall('front_wall', horizontal_position='middle', vertical_position='middle')

## Add lighting
scene.add('floor_lamp1', desc='A tall floor lamp')
scene.floor_lamp1.place_global(x='left_wall', y='floor', z='front_wall')
scene.add('chandelier1', desc='A beautiful glass chandelier')
scene.chandelier1.place_global(x='center', y='ceiling', z='center')
##$##
csr.no_out_of_bounds()
csr.no_overlaps()
csr.visible(scene.painting1, scene.chair5)
csr.visible(scene.painting2, scene.ottoman1)
csr.clearance(scene.door1, type='front', dist=1.0)
##$##
