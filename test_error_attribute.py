from manim import *

class AttributeErrorScene(Scene):
    def construct(self):
        square = Square(color=RED)
        # Call a non-existent method
        square.definitely_not_a_method()
        self.play(Create(square))
        self.wait()
