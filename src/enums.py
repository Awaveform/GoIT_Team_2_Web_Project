import enum


class Roles(enum.Enum):
    """
    Enumeration representing user roles.
    """
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class PhotoEffect(enum.Enum):
    """
    Enumeration representing photo effects.
    """
    SHARPEN = "sharpen"
    ENHANCE = "enhance"
    GEN_RESTORE = "gen_restore"
    BACKGROUND_REMOVAL = "background_removal"
    BLUR = "blur_faces"
    UPSCALE = "upscale"
    DROPSHADOW = "dropshadow"
    SEPIA = "sepia"
    VIGNETTE = "vignette"
    CARTOONIFY = "cartoonify"


class PhotoCrop(enum.Enum):
    """
    Enumeration representing photo cropping options.
    """
    FILL = "fill"
    SCALE = "scale"
    PAD = "pad"


class PhotoGravity(enum.Enum):
    """
    Enumeration representing photo gravity options.
    """
    FACES = "faces"
    AUTO = "auto"
    CENTER = "center"
    SOUTH = "south"


class QrModuleDrawer(enum.Enum):
    """
    Enumeration representing QR module drawer types.
    """
    ROUNDED = "RoundedModuleDrawer"
    CIRCLE = "CircleModuleDrawer"
    SQUARE = "SquareModuleDrawer"
    GAPPED = "GappedSquareModuleDrawer"
    HORIZONTAL = "HorizontalBarsDrawer"
    VERTICAL = "VerticalBarsDrawer"


class QrColorMask(enum.Enum):
    """
    Enumeration representing QR color mask types.
    """
    RADIAL = "RadialGradiantColorMask"
    SQUARE = "SquareGradiantColorMask"
    HORIZONTAL = "HorizontalGradiantColorMask"
    SOLID = "SolidFillColorMask"
    VERTICAL = "VerticalGradiantColorMask"
