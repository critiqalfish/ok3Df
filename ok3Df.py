import pygame
import math

class Scene:
    def __init__(self, screen, cam, objects = []):
        self.screen = screen
        cam.scene = self
        self.cam = cam
        for object in objects:
            object.screen = screen
            object.scene = self
            object.cam = cam
        self.objects = objects
        self.active = 0
        self.objmode = True
        self.cammode = False
    
    def render_objects(self):
        self.screen.fill("black")
        for obj in self.objects:
            obj.draw_obj()
        pygame.display.flip()

    def add_object(self, object):
        object.cam = self.cam
        self.objects.append(object)

    def focus_object(self, index):
        self.active = index

class Camera:
    def __init__(self, d):
        self.scene = None
        self.d = d
        self.position = pygame.Vector3(0.0, 0.0, 0.0)
        self.rotation = pygame.Vector3(0.0, 0.0, 0.0)
    
    def move_x(self, by):
        self.position.x += by
        self.scene.render_objects()

    def move_y(self, by):
        self.position.y += by
        self.scene.render_objects()

    def move_z(self, by):
        self.position.z += by
        self.scene.render_objects()

    def rotate_x(self, by):
        self.rotation.x += by
        self.scene.render_objects()

    def rotate_y(self, by):
        self.rotation.y += by
        self.scene.render_objects()

    def rotate_z(self, by):
        self.rotation.z += by
        self.scene.render_objects()

class Cube:
    def __init__(self, x, y, z, width, height, depth):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth
        self.screen = None
        self.cam = None
        """
        front side:
        0   1

        2   3
        back side:
        4   5

        6   7
        """
        self.vertices = [
            pygame.Vector3(self.x, self.y, self.z),
            pygame.Vector3(self.x + self.width, self.y, self.z),
            pygame.Vector3(self.x, self.y + self.height, self.z),
            pygame.Vector3(self.x + self.width, self.y + self.height, self.z),
            pygame.Vector3(self.x, self.y, self.z + self.depth),
            pygame.Vector3(self.x + self.width, self.y, self.z + self.depth),
            pygame.Vector3(self.x, self.y + self.height, self.z + self.depth),
            pygame.Vector3(self.x + self.width, self.y + self.height, self.z + self.depth)
        ]
    
    def project_vertex(self, vertex):
        vertex = self.vertices[vertex]

        translated_x = vertex.x - self.cam.position.x
        translated_y = vertex.y - self.cam.position.y
        translated_z = vertex.z - self.cam.position.z

        # Apply camera rotation around the z-axis
        rotated_x1 = translated_x * math.cos(self.cam.rotation.z) - translated_y * math.sin(self.cam.rotation.z)
        rotated_y1 = translated_x * math.sin(self.cam.rotation.z) + translated_y * math.cos(self.cam.rotation.z)
        rotated_z1 = translated_z

        # Apply camera rotation around the y-axis
        rotated_x2 = rotated_x1 * math.cos(self.cam.rotation.y) + rotated_z1 * math.sin(self.cam.rotation.y)
        rotated_y2 = rotated_y1
        rotated_z2 = -rotated_x1 * math.sin(self.cam.rotation.y) + rotated_z1 * math.cos(self.cam.rotation.y)

        # Apply camera rotation around the x-axis
        rotated_x3 = rotated_x2
        rotated_y3 = rotated_y2 * math.cos(self.cam.rotation.x) - rotated_z2 * math.sin(self.cam.rotation.x)
        rotated_z3 = rotated_y2 * math.sin(self.cam.rotation.x) + rotated_z2 * math.cos(self.cam.rotation.x)

        # Apply perspective projection
        projected_x = rotated_x3 / (rotated_z3 / self.cam.d)
        projected_y = rotated_y3 / (rotated_z3 / self.cam.d)

        return pygame.Vector2(projected_x, projected_y)

    def draw(self):
        vertices = []
        for i in range(8):
            calc = self.project_vertex(i)
            x = screen.get_width() / 2 + (screen.get_width() * calc.x)
            y = screen.get_height() / 2 + (screen.get_height() * calc.y)
            vertices.append(pygame.Vector2(x, y))

        # back lines
        pygame.draw.line(screen, (0, 0, 255), vertices[4], vertices[5])
        pygame.draw.line(screen, (0, 0, 255), vertices[5], vertices[7])
        pygame.draw.line(screen, (0, 0, 255), vertices[7], vertices[6])
        pygame.draw.line(screen, (0, 0, 255), vertices[6], vertices[4])

        # side lines
        pygame.draw.line(screen, (0, 255, 0), vertices[0], vertices[4])
        pygame.draw.line(screen, (0, 255, 0), vertices[1], vertices[5])
        pygame.draw.line(screen, (0, 255, 0), vertices[2], vertices[6])
        pygame.draw.line(screen, (0, 255, 0), vertices[3], vertices[7])

        # front lines
        pygame.draw.line(screen, (255, 0, 0), vertices[0], vertices[1])
        pygame.draw.line(screen, (255, 0, 0), vertices[1], vertices[3])
        pygame.draw.line(screen, (255, 0, 0), vertices[3], vertices[2])
        pygame.draw.line(screen, (255, 0, 0), vertices[2], vertices[0])

    def move_x(self, by):
        for v in self.vertices:
            v.x += by
    
    def move_y(self, by):
        for v in self.vertices:
            v.y += by
    
    def move_z(self, by):
        for v in self.vertices:
            v.z += by

    def get_center(self):
        sum_vector = pygame.Vector3(0, 0, 0)
        for vertex in self.vertices:
            sum_vector += vertex
        return sum_vector / len(self.vertices)

    def rotate_x(self, by):
        center = self.get_center()
        for i in range(8):
            translated = self.vertices[i] - center
            rotated = pygame.Vector3(translated.x,
                                     translated.y * math.cos(by) - translated.z * math.sin(by),
                                     translated.y * math.sin(by) + translated.z * math.cos(by))
            final = rotated + center
            self.vertices[i] = final

    def rotate_y(self, by):
        center = self.get_center()
        for i in range(8):
            translated = self.vertices[i] - center
            rotated = pygame.Vector3(translated.x * math.cos(by) + translated.z * math.sin(by),
                                     translated.y,
                                     -translated.x * math.sin(by) + translated.z * math.cos(by))
            final = rotated + center
            self.vertices[i] = final

    def rotate_z(self, by):
        center = self.get_center()
        for i in range(8):
            translated = self.vertices[i] - center
            rotated = pygame.Vector3(translated.x * math.cos(by) - translated.y * math.sin(by),
                                     translated.x * math.sin(by) + translated.y * math.cos(by),
                                     translated.z)
            final = rotated + center
            self.vertices[i] = final

class TriObject:
    def __init__(self):
        self.screen = None
        self.scene = None
        self.cam = None
        self.caching = False
        self.triangles = []

    def project_tri(self, tri):
        proj_tri = []
        for vertex in tri:
            # Apply vertex translation relative to camera
            translated_x = vertex.x - self.cam.position.x
            translated_y = vertex.y - self.cam.position.y
            translated_z = vertex.z - self.cam.position.z

            # Apply camera rotation around the z-axis
            rotated_x1 = translated_x * math.cos(self.cam.rotation.z) - translated_y * math.sin(self.cam.rotation.z)
            rotated_y1 = translated_x * math.sin(self.cam.rotation.z) + translated_y * math.cos(self.cam.rotation.z)
            rotated_z1 = translated_z

            # Apply camera rotation around the y-axis
            rotated_x2 = rotated_x1 * math.cos(self.cam.rotation.y) + rotated_z1 * math.sin(self.cam.rotation.y)
            rotated_y2 = rotated_y1
            rotated_z2 = -rotated_x1 * math.sin(self.cam.rotation.y) + rotated_z1 * math.cos(self.cam.rotation.y)

            # Apply camera rotation around the x-axis
            rotated_x3 = rotated_x2
            rotated_y3 = rotated_y2 * math.cos(self.cam.rotation.x) - rotated_z2 * math.sin(self.cam.rotation.x)
            rotated_z3 = rotated_y2 * math.sin(self.cam.rotation.x) + rotated_z2 * math.cos(self.cam.rotation.x)

            # Apply perspective projection
            projected_x = rotated_x3 / (rotated_z3 / self.cam.d + 0.000001)
            projected_y = rotated_y3 / (rotated_z3 / self.cam.d + 0.000001)

            proj_tri.append(pygame.Vector2(projected_x, projected_y))
        return proj_tri

    def draw_obj(self):
        if self.caching:
            calculated_results = {}
            for tri in self.triangles:
                tri_tuple = tuple(tuple(vertex) for vertex in tri)

                if tri_tuple in calculated_results:
                    projected_vertices = calculated_results[tri_tuple]
                else:
                    projected_vertices = self.project_tri(tri)
                    calculated_results[tri_tuple] = projected_vertices

                real_tri = []
                for vertex in projected_vertices:
                    real_x = screen.get_width() / 2 + (screen.get_width() * vertex.x)
                    real_y = screen.get_height() / 2 + (screen.get_height() * vertex.y)
                    real_tri.append(pygame.Vector2(real_x, real_y))

                pygame.draw.line(self.screen, (255, 255, 255), real_tri[0], real_tri[1])
                pygame.draw.line(self.screen, (255, 255, 255), real_tri[1], real_tri[2])
                pygame.draw.line(self.screen, (255, 255, 255), real_tri[2], real_tri[0])
        else:
            for tri in self.triangles:
                real_tri = []
                for vertex in self.project_tri(tri):
                    real_x = screen.get_width() / 2 + (screen.get_width() * vertex.x)
                    real_y = screen.get_height() / 2 + (screen.get_height() * vertex.y)
                    real_tri.append(pygame.Vector2(real_x, real_y))
                pygame.draw.line(self.screen, (255, 255, 255), real_tri[0], real_tri[1])
                pygame.draw.line(self.screen, (255, 255, 255), real_tri[1], real_tri[2])
                pygame.draw.line(self.screen, (255, 255, 255), real_tri[2], real_tri[0])

    def load_file(self, file):
        tris = []
        with open(file, "r") as f:
            tris_c = int(f.readline())
            for i in range(tris_c):
                tri = []
                for t in range(3):
                    vec = []
                    line = f.readline()
                    pos = 0
                    for n in range(3):
                        if line[pos] == "-":
                            vec.append(float(line[pos:pos + 9]))
                            pos += 10
                        else:
                            vec.append(float(line[pos:pos + 8]))
                            pos += 9
                    tri.append(pygame.Vector3(vec))
                f.readline()
                tris.append(tri)
        self.triangles = tris

    def move_x(self, by):
        for tri in self.triangles:
            for v in tri:
                v.x += by
        self.scene.render_objects()
    
    def move_y(self, by):
        for tri in self.triangles:
            for v in tri:
                v.y += by
        self.scene.render_objects()
    
    def move_z(self, by):
        for tri in self.triangles:
            for v in tri:
                v.z += by
        self.scene.render_objects()

pygame.init()
fps_font = pygame.font.Font(pygame.font.get_default_font(), 12)
screen = pygame.display.set_mode((720, 720))
clock = pygame.time.Clock()
running = True

#cube0 = Cube(-0.7, -0.5, 1, 0.5, 0.5, 0.5)
#cube1 = Cube(0.5, 0.5, 0.8, 0.3, 0.3, 0.3)
teapot = TriObject()
teapot.load_file("teapot_bezier1.tris")
teapot.caching = False
cam = Camera(0.3)
scene = Scene(screen, cam, [teapot])
cam.move_z(3)
cam.move_y(2)
scene.render_objects()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_u:
                scene.objmode, scene.cammode = scene.cammode, scene.objmode
            if event.key == pygame.K_f:
                if scene.active < len(scene.objects) - 1:
                    scene.active += 1
                else:
                    scene.active = 0

    keys = pygame.key.get_pressed()
    # move controls
    if scene.objmode:
        if keys[pygame.K_LEFT] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
            scene.objects[scene.active].move_x(-0.01)
        if keys[pygame.K_RIGHT] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
            scene.objects[scene.active].move_x(0.01)
        if keys[pygame.K_UP] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
            scene.objects[scene.active].move_y(-0.01)
        if keys[pygame.K_DOWN] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
            scene.objects[scene.active].move_y(0.01)
        if keys[pygame.K_UP]:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
                    scene.objects[scene.active].move_z(0.01)
        if keys[pygame.K_DOWN]:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
                    scene.objects[scene.active].move_z(-0.01)
        # rotate controls
        if keys[pygame.K_LEFT] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            scene.objects[scene.active].rotate_y(0.01)
        if keys[pygame.K_RIGHT] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            scene.objects[scene.active].rotate_y(-0.01)
        if keys[pygame.K_UP] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            scene.objects[scene.active].rotate_x(-0.01)
        if keys[pygame.K_DOWN] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            scene.objects[scene.active].rotate_x(0.01)
        if keys[pygame.K_LEFT]:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                    scene.objects[scene.active].rotate_z(-0.01)
        if keys[pygame.K_RIGHT]:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                    scene.objects[scene.active].rotate_z(0.01)
    elif scene.cammode:
        # move controls
        if keys[pygame.K_LEFT] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
            scene.cam.move_x(-0.01)
        if keys[pygame.K_RIGHT] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
            scene.cam.move_x(0.01)
        if keys[pygame.K_UP] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
            scene.cam.move_y(-0.01)
        if keys[pygame.K_DOWN] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
            scene.cam.move_y(0.01)
        if keys[pygame.K_UP]:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
                    scene.cam.move_z(0.01)
        if keys[pygame.K_DOWN]:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if not keys[pygame.K_LCTRL] and not keys[pygame.K_RCTRL]:
                    scene.cam.move_z(-0.01)
        # rotate controls
        if keys[pygame.K_LEFT] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            scene.cam.rotate_y(0.01)
        if keys[pygame.K_RIGHT] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            scene.cam.rotate_y(-0.01)
        if keys[pygame.K_UP] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            scene.cam.rotate_x(-0.01)
        if keys[pygame.K_DOWN] and not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT] and keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            scene.cam.rotate_x(0.01)
        if keys[pygame.K_LEFT]:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                    scene.cam.rotate_z(-0.01)
        if keys[pygame.K_RIGHT]:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                    scene.cam.rotate_z(0.01)

    #screen.blit()
    #screen.blit(fps_font.render("FPS: " + str(round(clock.get_fps(), 2)), True, (255, 0, 255)), (20, 20))
    #pygame.display.flip()

    clock.tick(60)
    pygame.display.set_caption("FPS: " + str(round(clock.get_fps(), 2)))

pygame.quit()
