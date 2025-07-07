from setuptools import setup, find_packages

setup(
    name="blendair",
    version="0.1.0",
    description="Blend(AI)r – Blender add-on for prompt & gesture controlled editing",
    author="Cascade AI",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "supabase",
        "opencv-python",
        "mediapipe",
    ],
)
