import numpy as np
import trimesh
import json
from modules.sdl.object import Object3D
from modules.sdl.scene import SceneHelper

class CorrectionComputer:
    def __init__(self, scene, obj1, obj2, buffer, fix_obj2=False):
        self.BUFFER = buffer
        self.obj1 = obj1
        self.obj2 = obj2
        self.scene = scene
        self.fix_obj2 = fix_obj2
        
        self.structure_affinity_scale = [1, 5, 8, 10, 12, 14, 16, 18, 20]
        self.helper = SceneHelper(self.scene)
        
    def generate_sample_points(self, vertices, num_samples=1000):
        
        def sort_vertices(vertices):
            # Sort the vertices by x and then by y to get the order: bottom-left, bottom-right, top-right, top-left
            vertices_sorted = sorted(vertices, key=lambda x: (x[0], x[1]))
            bottom_left, bottom_right = sorted(vertices_sorted[:2], key=lambda x: x[0])
            top_left, top_right = sorted(vertices_sorted[2:], key=lambda x: x[0], reverse=True)
            return [bottom_left, bottom_right, top_right, top_left]

        sorted_vertices = sort_vertices(vertices)

        # Calculate edge lengths
        edge_lengths = [
            np.linalg.norm(np.array(sorted_vertices[i]) - np.array(sorted_vertices[(i + 1) % 4]))
            for i in range(4)
        ]
        total_perimeter = sum(edge_lengths)

        # Calculate the number of points per edge based on edge length
        points_per_edge = [int(np.round(num_samples * (length / total_perimeter))) for length in edge_lengths]

        # Adjust the points to ensure the total is exactly num_samples
        points_difference = num_samples - sum(points_per_edge)
        points_per_edge[0] += points_difference  # Adjust the first edge to compensate any rounding error

        samples = []
        for i, num_points in enumerate(points_per_edge):
            start_vertex = np.array(sorted_vertices[i])
            end_vertex = np.array(sorted_vertices[(i + 1) % 4])
            
            # Generate points for this edge
            for j in range(num_points):
                t = j / (num_points - 1) if num_points > 1 else 0.5  # Avoid division by zero for single point
                point = (1 - t) * start_vertex + t * end_vertex
                samples.append(point)
        
        return np.array(samples)

    def chamfer_distance(self):
        '''
        Computes the chamfer distance between two objects
        '''
        # pts1 = self.obj1.mesh.sample(1000)[:,[0,2]]
        # pts2 = self.obj2.mesh.sample(1000)[:,[0,2]]
        pts1 = self.generate_sample_points(self.obj1.get_proj2D(), 100)
        pts2 = self.generate_sample_points(self.obj2.get_proj2D(), 100)
        
        all_dists = []
        pt_pairs = []
        for pt1 in pts1:
            for pt2 in pts2:
                all_dists.append(np.linalg.norm(pt1-pt2))
                pt_pairs.append((pt1, pt2)) 
                
        return np.min(all_dists), pt_pairs[np.argmin(all_dists)]
    
    def free_space_affinity(self, space):
        return 1-np.exp(-2*space)
    
    def compute_adjustments_visibility(self, obstructing_obj):
        to_be_viewed = self.obj1
        viewed_from = self.obj2
        
        line_connecting_them = np.mean(to_be_viewed.get_proj2D(), axis=0) - np.mean(viewed_from.get_proj2D(), axis=0)
        obstructing_obj_viewed_from = np.mean(obstructing_obj.get_proj2D(), axis=0) - np.mean(viewed_from.get_proj2D(), axis=0)
        
        obstructing_obj_to_midpoint = obstructing_obj_viewed_from - np.dot(obstructing_obj_viewed_from, line_connecting_them)/np.dot(line_connecting_them, line_connecting_them)*line_connecting_them
        
        vec_obj1 = obstructing_obj_to_midpoint
        vec_obj1 = vec_obj1/np.linalg.norm(vec_obj1)
        
        adjustment = 1.0
        
        return adjustment, vec_obj1
        
    def compute_adjustments_out_of_bound(self):
        xmin, _, zmin, xmax, _, zmax = self.obj1.get_min_max()
        x_adjustment = 0
        z_adjustment = 0
        vec_obj1 = np.array([0.,0.])
        if xmin < 0:
            x_adjustment = np.abs(xmin) + self.BUFFER
            vec_obj1 += np.array([x_adjustment,0])
        if xmax > self.scene.MAX_WIDTH:
            x_adjustment = np.abs(xmax-self.scene.MAX_WIDTH) + self.BUFFER
            vec_obj1 += np.array([-x_adjustment,0])
        if zmin < 0:
            z_adjustment = np.abs(zmin) + self.BUFFER
            vec_obj1 += np.array([0,z_adjustment])
        if zmax > self.scene.MAX_DEPTH:
            z_adjustment = np.abs(zmax-self.scene.MAX_DEPTH) + self.BUFFER
            vec_obj1 += np.array([0,-z_adjustment])
            
        vec_obj1 = vec_obj1/np.linalg.norm(vec_obj1)
        
        return x_adjustment, z_adjustment, vec_obj1
    
    def compute_adjustments_overlap(self):
        xmin1, _, zmin1, xmax1, _, zmax1 = self.obj1.get_min_max()
        xmin2, _, zmin2, xmax2, _, zmax2 = self.obj2.get_min_max()
        
        # Check for x-axis overlap and suggest adjustment
        if xmax1 >= xmin2 and xmin1 <= xmax2:
            x_overlap = min(xmax1 - xmin2, xmax2 - xmin1)
            x_adjustment = x_overlap + self.BUFFER
        else:
            x_adjustment = 0
        # Check for z-axis overlap and suggest adjustment
        if zmax1 >= zmin2 and zmin1 <= zmax2:
            z_overlap = min(zmax1 - zmin2, zmax2 - zmin1)
            z_adjustment = z_overlap + self.BUFFER
        else:
            z_adjustment = 0
            
        x_adjustment = int(100*np.abs(x_adjustment))/100
        z_adjustment = int(100*np.abs(z_adjustment))/100
        
        vec_obj1 = np.mean(self.obj1.get_proj2D(), axis=0) - np.mean(self.obj2.get_proj2D(), axis=0)
        vec_obj1 = vec_obj1/np.linalg.norm(vec_obj1)
        vec_obj2 = -vec_obj1
        
        return x_adjustment, z_adjustment, vec_obj1, vec_obj2
    
    def compute_adjustments_maximum_distance(self, max_dist):
        curr_dist, pt_pair = self.chamfer_distance()
        if curr_dist < max_dist or curr_dist+self.BUFFER < max_dist:
            return -1, -1, -1
        
        adjustment = curr_dist - max_dist + self.BUFFER
        vec = pt_pair[1] - pt_pair[0]
        vec = vec/np.linalg.norm(vec)
        
        vec_obj1 = vec
        vec_obj2 = -vec
        
        return int(100*0.8*adjustment)/100, vec_obj1, vec_obj2
    
    def compute_adjustments_minimum_distance(self, min_dist):
        curr_dist, pt_pair = self.chamfer_distance()
        
        if curr_dist > min_dist or curr_dist-self.BUFFER > min_dist:
            return -1, -1, -1
        
        adjustment = min_dist - curr_dist + self.BUFFER
        vec = pt_pair[0] - pt_pair[1]
        vec = vec/np.linalg.norm(vec)
        
        vec_obj1 = vec
        vec_obj2 = -vec
        
        return int(100*0.8*adjustment)/100, vec_obj1, vec_obj2
    
    def compute_direction_probs(self, x_adjustment, z_adjustment, vec_obj1, vec_obj2):
        
        if self.helper.sg.is_part_of_same_subtree(self.obj1, self.obj2) and self.obj1 != self.obj2:
            run_individually = True
        else:
            run_individually = False
    
        vec_posx = np.array([1,0])
        vec_negx = np.array([-1,0])
        vec_posz = np.array([0,1])
        vec_negz = np.array([0,-1])
        
        def compute_free_space_around_obj(obj):
            obj_posx, obj_negx, obj_posz, obj_negz = self.helper.compute_free_space_around_obj(obj)
            for space in [obj_posx, obj_negx]:
                if space < x_adjustment:
                    space = 0
                    
            for space in [obj_posz, obj_negz]:
                if space < z_adjustment:
                    space = 0
            
            return obj_posx, obj_negx, obj_posz, obj_negz
        
        def compute_free_space_around_obj_sg(obj):
            obj1_posx_0, obj1_negx_0, obj1_posz_0, obj1_negz_0 = compute_free_space_around_obj(obj)
            
            parent = self.helper.sg.get_object(obj.name).parent
            
            anchor = [obj.name]
            free_space = [[obj1_posx_0, obj1_negx_0, obj1_posz_0, obj1_negz_0]]
            for i in range(4):
                if parent is not None and parent != 'root' and not run_individually:
                    obj1_posx, obj1_negx, obj1_posz, obj1_negz = compute_free_space_around_obj(self.scene.get_object(parent))
                else:
                    obj1_posx, obj1_negx, obj1_posz, obj1_negz = 0, 0, 0, 0
                free_space.append([obj1_posx, obj1_negx, obj1_posz, obj1_negz])   
                anchor.append(parent)
                try:
                    parent = self.helper.sg.get_object(parent).parent
                except:
                    parent = 'root'
                
            return anchor, np.array(free_space)
        
        def compute_mass(obj):
            if obj == 'root':
                return 10**6
            _, children = self.helper.sg.get_object(obj).get_all_children()
            total_mass = self.scene.get_object(obj).get_whd()[0]*self.scene.get_object(obj).get_whd()[2]
            for child in children:
                w,h,d = self.scene.get_object(child).get_whd()
                total_mass += w*d
            return total_mass
        
        anchor1, free_space_obj1 = compute_free_space_around_obj_sg(self.obj1)
        anchor2, free_space_obj2 = compute_free_space_around_obj_sg(self.obj2)
        
        ## Compute direction affinity
        dir_affn_obj1_posx = max(vec_obj1@vec_posx,0)
        dir_affn_obj1_negx = max(vec_obj1@vec_negx,0)
        dir_affn_obj1_posz = max(vec_obj1@vec_posz,0)
        dir_affn_obj1_negz = max(vec_obj1@vec_negz,0)
        
        dir_affn_obj2_posx = max(vec_obj2@vec_posx,0)
        dir_affn_obj2_negx = max(vec_obj2@vec_negx,0)
        dir_affn_obj2_posz = max(vec_obj2@vec_posz,0)
        dir_affn_obj2_negz = max(vec_obj2@vec_negz,0)
        
        ## Compute free space affinity
        free_space_affn_obj1 = self.free_space_affinity(free_space_obj1)
        free_space_affn_obj2 = self.free_space_affinity(free_space_obj2)
        
        ## Compute mass affinity
        mass_affn_obj1 = np.array([1/compute_mass(x)**0.5 for x in anchor1])
        mass_affn_obj2 = np.array([1/compute_mass(x)**0.5 for x in anchor2])
        
        ## Compute structure affinity
        struct_affn_obj1 = self.structure_affinity_scale[:len(anchor1)]
        struct_affn_obj2 = self.structure_affinity_scale[:len(anchor2)]
        
        ## Compute weights
        weights_obj1_posx = free_space_affn_obj1[:,0]*mass_affn_obj1*struct_affn_obj1*dir_affn_obj1_posx
        weights_obj1_negx = free_space_affn_obj1[:,1]*mass_affn_obj1*struct_affn_obj1*dir_affn_obj1_negx
        weights_obj1_posz = free_space_affn_obj1[:,2]*mass_affn_obj1*struct_affn_obj1*dir_affn_obj1_posz
        weights_obj1_negz = free_space_affn_obj1[:,3]*mass_affn_obj1*struct_affn_obj1*dir_affn_obj1_negz
        
        weights_obj2_posx = free_space_affn_obj2[:,0]*mass_affn_obj2*struct_affn_obj2*dir_affn_obj2_posx
        weights_obj2_negx = free_space_affn_obj2[:,1]*mass_affn_obj2*struct_affn_obj2*dir_affn_obj2_negx
        weights_obj2_posz = free_space_affn_obj2[:,2]*mass_affn_obj2*struct_affn_obj2*dir_affn_obj2_posz
        weights_obj2_negz = free_space_affn_obj2[:,3]*mass_affn_obj2*struct_affn_obj2*dir_affn_obj2_negz
        
        weight_obj1 = np.hstack([weights_obj1_posx.reshape(-1,1), weights_obj1_negx.reshape(-1,1), weights_obj1_posz.reshape(-1,1), weights_obj1_negz.reshape(-1,1)])
        weight_obj2 = np.hstack([weights_obj2_posx.reshape(-1,1), weights_obj2_negx.reshape(-1,1), weights_obj2_posz.reshape(-1,1), weights_obj2_negz.reshape(-1,1)])
        
        weights = np.vstack([weight_obj1, weight_obj2])
        sum = np.sum(weights)
        weights = weights/sum
        
        anchors = anchor1 + anchor2
        return weights, anchors
        
    def compute_overlap_correction(self):
        x_adjustment, z_adjustment, vec_obj1, vec_obj2 = self.compute_adjustments_overlap()
        weights, anchors = self.compute_direction_probs(x_adjustment, z_adjustment, vec_obj1, vec_obj2)
        
        directions = [np.array([1,0,0]), np.array([-1,0,0]), np.array([0,0,1]), np.array([0,0,-1])]
        magnitudes = [x_adjustment, x_adjustment, z_adjustment, z_adjustment]
        if np.max((x_adjustment,z_adjustment)) < self.BUFFER:
            return None
        if self.fix_obj2:
            weights[len(anchors)//2:] = 0
        idx = np.unravel_index(weights.argmax(), weights.shape)
        anchor = anchors[idx[0]]
        direction = directions[idx[1]]
        magnitude = magnitudes[idx[1]]
        feedback = (anchor, direction, magnitude)
        return feedback
    
    def compute_maximum_distance_correction(self, max_dist):
        adjustments, vec_obj1, vec_obj2 = self.compute_adjustments_maximum_distance(max_dist)
        if adjustments == -1:
            return None
        weights, anchors = self.compute_direction_probs(adjustments, adjustments, vec_obj1, vec_obj2)
        directions = [np.array([1,0,0]), np.array([-1,0,0]), np.array([0,0,1]), np.array([0,0,-1])]
        idx = np.unravel_index(weights.argmax(), weights.shape)
        anchor = anchors[idx[0]]
        direction = directions[idx[1]]
        feedback = (anchor, direction, adjustments)
        return feedback
    
    def compute_minimum_distance_correction(self, min_dist):
        adjustments, vec_obj1, vec_obj2 = self.compute_adjustments_minimum_distance(min_dist)
        if adjustments == -1:
            return None
        weights, anchors = self.compute_direction_probs(adjustments, adjustments, vec_obj1, vec_obj2)
        directions = [np.array([1,0,0]), np.array([-1,0,0]), np.array([0,0,1]), np.array([0,0,-1])]
        idx = np.unravel_index(weights.argmax(), weights.shape)
        anchor = anchors[idx[0]]
        direction = directions[idx[1]]
        feedback = (anchor, direction, adjustments)
        return feedback
    
    def compute_out_of_bound_correction(self):
        x_adjustment, z_adjustment, vec_obj1 = self.compute_adjustments_out_of_bound()
        weights, anchors = self.compute_direction_probs(x_adjustment, z_adjustment, vec_obj1, vec_obj1)
        directions = [np.array([1,0,0]), np.array([-1,0,0]), np.array([0,0,1]), np.array([0,0,-1])]
        magnitudes = [x_adjustment, x_adjustment, z_adjustment, z_adjustment]
        
        weights[len(anchors)//2:] = 0
        idx = np.unravel_index(weights.argmax(), weights.shape)
        anchor = anchors[idx[0]]
        direction = directions[idx[1]]
        magnitude = magnitudes[idx[1]]
        
        feedback = (anchor, direction, magnitude)   
        return feedback
        
    def compute_visibility_correction(self, obstructing_obj):
        
        adjustment, vec_obj1 = self.compute_adjustments_visibility(obstructing_obj)
        self.obj1 = obstructing_obj
        weights, anchors = self.compute_direction_probs(adjustment, adjustment, vec_obj1, vec_obj1)
        weights[len(anchors)//2:] = 0
        directions = [np.array([1,0,0]), np.array([-1,0,0]), np.array([0,0,1]), np.array([0,0,-1])]
        
        idx = np.unravel_index(weights.argmax(), weights.shape)
        anchor = anchors[idx[0]]
        direction = directions[idx[1]]
        magnitude = adjustment
        
        feedback = (anchor, direction, magnitude)   
        return feedback
        
        
        
class Constraints:
    def __init__(self, scene):
        self.scene = scene
        self.helper = SceneHelper(self.scene)
        self.sg = self.helper.sg
        self.MAX_WIDTH = self.scene.MAX_WIDTH
        self.MAX_HEIGHT = self.scene.MAX_HEIGHT
        self.MAX_DEPTH = self.scene.MAX_DEPTH
        self.BUFFER = 0.2
        self.lr = 0.2
        self.weights = {'overlap':1.0, 'out_of_bounds':1.0, 'access':0.5, 'clearance':0.5, 'visible':0.5}
        self.grads = {}
        self.displacement = {}
        for obj in self.scene.objects:
            self.displacement[obj.name] = np.zeros(3)    
        
    def init_grads(self):
        for obj in self.scene.objects:
            if not obj.on_floor or obj.placed_on_wall:
                continue
            self.grads[obj.name] = np.zeros(3)
    
    def __no_out_of_bounds(self, obj):
        xmin, _, zmin, xmax, _, zmax = obj.get_min_max()
        if xmin < 0 or xmax > self.MAX_WIDTH or zmin < 0 or zmax > self.MAX_DEPTH:
            computer = CorrectionComputer(self.scene, obj, obj, self.BUFFER)
            anchor, direction, magnitude = computer.compute_out_of_bound_correction()
            self.grads[anchor] += magnitude*direction*self.weights['out_of_bounds']
        
    def no_out_of_bounds(self):
        for obj in self.scene.objects:
            if not obj.on_floor or obj.placed_on_wall:
                continue
            self.__no_out_of_bounds(obj)
    
    def are_boxes_intersecting(self, obj1, obj2):
            
        xmin1, ymin1, zmin1, xmax1, ymax1, zmax1 = obj1.get_min_max()
        xmin2, ymin2, zmin2, xmax2, ymax2, zmax2 = obj2.get_min_max()
        
        if obj1.ignore_overlap or obj2.ignore_overlap:
            return False
        
        # Check if one box is to the left of the other
        if xmax1 <= xmin2 or xmax2 <= xmin1:
            return False

        # Check if one box is above the other
        if ymax1 <= ymin2 or ymax2 <= ymin1:
            return False

        # Check if one box is in front of the other
        if zmax1 <= zmin2 or zmax2 <= zmin1:
            return False

        # If none of the above cases are true, the boxes are intersecting
        return True
        
    def __no_overlap(self, obj1, obj2):
        if self.are_boxes_intersecting(obj1, obj2):
            computer = CorrectionComputer(self.scene, obj1, obj2, self.BUFFER)
            feedback = computer.compute_overlap_correction()
            if feedback is not None:
                anchor, direction, magnitude = feedback
                self.grads[anchor] += magnitude*direction*self.weights['overlap']
    
    def no_overlaps(self):
        for i in range(len(self.scene.objects)):
            for j in range(i+1, len(self.scene.objects)):
                if self.scene.objects[i] in self.scene.objects[j].support_objs or self.scene.objects[j] in self.scene.objects[i].support_objs:
                    continue
                if self.scene.objects[i] in self.scene.overlap_exceptions or self.scene.objects[j] in self.scene.overlap_exceptions:
                    continue
                if not self.scene.objects[i].on_floor or not self.scene.objects[j].on_floor:
                    continue
                if self.scene.objects[i].placed_on_wall or self.scene.objects[j].placed_on_wall:
                    continue
                self.__no_overlap(self.scene.objects[i], self.scene.objects[j])
    
    def clearance(self, obj, type, dist=0.5, omit_objs=[]):
        left_side, right_side, front_side, back_side = obj.get_sides()
        if len(omit_objs) > 0:
            if isinstance(omit_objs[0], str):
                tmp=[]
                for o in omit_objs:
                    tmp.append(self.scene.get_objects(o))
                omit_objs = tmp
        
        if type == 'front':
            vec = np.array(front_side).mean(axis=0) - np.array(back_side).mean(axis=0)
            vec  = vec/np.linalg.norm(vec)
            
            v11 = front_side[0]
            v12 = front_side[1]
            
            v22 = front_side[1]+dist*vec
            v21 = front_side[0]+dist*vec
            
            v110 = np.array([v11[0], 0, v11[1]])            
            v120 = np.array([v12[0], 0, v12[1]])
            
            v210 = np.array([v21[0], 0, v21[1]])
            v220 = np.array([v22[0], 0, v22[1]])
            
            v111 = np.array([v11[0], 2, v11[1]])
            v121 = np.array([v12[0], 2, v12[1]])
            
            v211 = np.array([v21[0], 2, v21[1]])
            v221 = np.array([v22[0], 2, v22[1]])
            
            ## Create a triangular mesh with the eight vertices
            vertices = np.array([v110, v120, v210, v220, v111, v121, v211, v221])
            faces = np.array([[0,1,2], [1,3,2], [4,5,6], [5,6,7], [0,1,4], [1,5,4], [2,3,6], [3,6,7], [0,2,4], [2,4,6], [1,5,3], [3,5,7]])
            mesh = trimesh.Trimesh(vertices, faces, process=False)
            # mesh.export('test.obj')
             
            rand_id = np.random.randint(1000)
            clearance_obj = Object3D(f'clearance_{rand_id}', desc=None, scene=self.scene, use_mesh=mesh)

        elif type == 'sides':
            
            vec = np.array(left_side).mean(axis=0) - np.array(right_side).mean(axis=0)
            vec  = vec/np.linalg.norm(vec)
            
            v11 = left_side[0]+dist*vec
            v21 = left_side[1]+dist*vec
            
            vec = np.array(right_side).mean(axis=0) - np.array(left_side).mean(axis=0)
            vec  = vec/np.linalg.norm(vec)
            
            v12 = right_side[0]+dist*vec
            v22 = right_side[1]+dist*vec
            
            v110 = np.array([v11[0], 0, v11[1]])
            v120 = np.array([v12[0], 0, v12[1]])
            
            v210 = np.array([v21[0], 0, v21[1]])
            v220 = np.array([v22[0], 0, v22[1]])
            
            v111 = np.array([v11[0], 2, v11[1]])
            v121 = np.array([v12[0], 2, v12[1]])
            
            v211 = np.array([v21[0], 2, v21[1]])
            v221 = np.array([v22[0], 2, v22[1]])
            
            ## Create a triangular mesh with the eight vertices
            vertices = np.array([v110, v120, v210, v220, v111, v121, v211, v221])
            faces = np.array([[0,1,2], [1,2,3], [4,5,6], [5,6,7], [0,1,4], [1,4,5], [2,3,6], [3,6,7], [0,2,4], [2,4,6], [1,3,5], [3,5,7]])
            
            mesh = trimesh.Trimesh(vertices, faces, process=False)
            rand_id = np.random.randint(1000)
            clearance_obj = Object3D(f'clearance_{rand_id}', desc=None, scene=self.scene, use_mesh=mesh)
            
        clearance_obj.init()
        org_obj_list = self.scene.objects.copy()
        self.scene.objects.append(clearance_obj)
        
        for o in self.scene.objects:
            if o in [obj, clearance_obj] or o in obj.support_objs or o in self.scene.overlap_exceptions or o in omit_objs:
                continue
        
            if self.are_boxes_intersecting(o, clearance_obj):
                computer = CorrectionComputer(self.scene, o, clearance_obj, self.BUFFER, fix_obj2=True)
                feedback = computer.compute_overlap_correction()
                
                if feedback is not None:
                    anchor, direction, magnitude = feedback
                    self.grads[anchor] += magnitude*direction*self.weights['clearance']
        
        self.scene.objects = org_obj_list.copy()
    
    def access(self, obj1, obj2, min_dist, max_dist):
        computer = CorrectionComputer(self.scene, obj1, obj2, self.BUFFER)
        feedback = computer.compute_minimum_distance_correction(min_dist)
        if feedback is not None:
            anchor, direction, magnitude = feedback
            self.grads[anchor] += magnitude*direction*self.weights['access']
        
        feedback = computer.compute_maximum_distance_correction(max_dist)
        if feedback is not None:
            anchor, direction, magnitude = feedback
            self.grads[anchor] += magnitude*direction*self.weights['access']
                
    def visible(self, obj, from_obj):
        target_obj=obj
        source_obj=from_obj
        xmin, ymin, zmin = target_obj.get_aabb()[0]
        xmax, ymax, zmax = target_obj.get_aabb()[1]
        
        x = np.random.uniform(xmin, xmax, 1000)
        y = np.random.uniform(ymin, ymax, 1000)
        z = np.random.uniform(zmin, zmax, 1000)
        points = np.array(list(zip(x, y, z)))
        
        ray_origins = source_obj.get_loc()
        ray_origins[1] = 1 ## height of a person sitting
        ray_origins = np.repeat(ray_origins.reshape(1,3), len(points), axis=0)
        
        ray_directions = points - ray_origins
        ray_directions = ray_directions/np.linalg.norm(ray_directions, axis=1).reshape(-1,1)
        
        scene_objs = self.scene.objects.copy()
        if target_obj in scene_objs:
            try:
                scene_objs.remove(target_obj)
            except:
                pass
        try:
            scene_objs.remove(source_obj)
        except:
            pass
        
        for o in scene_objs:
            if o in target_obj.support_objs or o in source_obj.support_objs or o in self.scene.overlap_exceptions or o.placed_on_wall or not o.on_floor:
                try:
                    scene_objs.remove(o)
                except:
                    pass
            
        def obstructing_intersection(ray_origins, index_ray, locations, end_points):
            obstructing = np.linalg.norm(ray_origins[index_ray]-locations, axis=1) < np.linalg.norm(ray_origins[index_ray]-end_points[index_ray], axis=1)
            return obstructing.sum()/len(obstructing) 
        
        obstructing_objects = []
        
        for obj in scene_objs:
            locations, index_ray, _ = obj.mesh.ray.intersects_location(ray_origins=ray_origins, ray_directions=ray_directions)
            frac = locations.shape[0]/ray_origins.shape[0]
            if len(locations)>0:
                frac = frac*obstructing_intersection(ray_origins, index_ray, locations, np.array(points))
                if frac > 0.1:
                    obstructing_objects.append(obj) 

        if len(obstructing_objects) > 0:
            for obs in obstructing_objects:
                computer = CorrectionComputer(self.scene, target_obj, source_obj, self.BUFFER)
                feedback = computer.compute_visibility_correction(obs)
                if feedback is not None:
                    anchor, direction, magnitude = feedback
                    try:
                        self.grads[anchor] += magnitude*direction*self.weights['visible']       
                    except:
                        continue
    
    def update(self):
        before_locs = {}
        obj_steps = {}
        for obj in self.scene.objects:
            before_locs[obj.name] = obj.get_loc()
        
        for obj in self.grads:
            step = self.lr*self.grads[obj]
            self.displacement[obj] += step
            self.scene.get_object(obj).displace(delta_x=step[0], delta_y=step[1], delta_z=step[2])
            obj_steps[obj] = step
            
        step_sizes = [np.max(np.abs(obj_steps[obj])) for obj in self.grads]
        if np.max(step_sizes) < 0.05:
            return True
        
        print("**** update *******")
        for obj in self.grads.keys():
            obj = self.scene.get_object(obj)
            print(obj.name, before_locs[obj.name], '-->', obj.get_loc(), 'actual_change ', obj.get_loc()-before_locs[obj.name], 'step ', obj_steps[obj.name], 'displacement', self.displacement[obj.name])
        
        return False
    
    def save(self):
        def round_off(x):
            return int(100*x)/100
        
        for obj in self.displacement.keys():
            self.displacement[obj] = [round_off(x) for x in self.displacement[obj]]
        
        import json
        with open('tmp/csr.json', 'w') as f:
            json.dump(self.displacement, f)