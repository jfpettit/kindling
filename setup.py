from setuptools import setup

setup(
    name="kindling",
    version="0.1.0",
    author="Jacob Pettit",
    author_email="jfpettit@gmail.com",
    description="Helper functions for building RL algorithms.",
    install_requires=[
        "numpy",
        "torch",
        "scipy",
        "gym[box2d]",
        "mpi4py"
    ]
)
