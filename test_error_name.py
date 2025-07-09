from manim import *

class NameErrorScene(Scene):
    def construct(self):
        # Incorrect Mobject name
        my_object = circel(radius=1, color=BLUE) # circel should be Circle
        self.play(Create(my_object))
        self.wait()
