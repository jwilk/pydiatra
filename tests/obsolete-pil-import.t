import Image

Image.open("a")

try:
    import Image
except ImportError:
    from PIL import Image

Image.open("b")

try:
    import Image as PIL
except ImportError:
    import PIL.Image as PIL

PIL.open("c")

## 1: obsolete-pil-import Image

# vim:ts=4 sts=4 sw=4 et syntax=python
