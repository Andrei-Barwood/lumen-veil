from setuptools import Extension, find_packages, setup


setup(
    name="lumen-veil",
    version="0.1.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    ext_modules=[
        Extension(
            "lumen_veil._lumen_native",
            sources=["physics/src/lumen_native.c"],
            extra_compile_args=["-std=c11"],
        )
    ],
)
