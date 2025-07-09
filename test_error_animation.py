from manim import *

class AnimationErrorScene(Scene):
    def construct(self):
        text_mobject = Text("Hello")
        self.play(Write(text_mobject))

        # Incorrect Transform usage: Target is a string, not a Mobject.
        # This should cause a TypeError.
        self.play(Transform(text_mobject, "World"))
        self.wait()
