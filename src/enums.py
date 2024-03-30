import enum


class Roles(enum.Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class PhotoEffect(enum.Enum):
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
    FILL = "fill"
    SCALE = "scale"
    PAD = "pad"


class PhotoGravity(enum.Enum):
    FACES = "faces"
    AUTO = "auto"
    CENTER = "center"
    SOUTH = "south"


class QrModuleDrawer(enum.Enum):
    ROUNDED = "RoundedModuleDrawer"
    CIRCLE = "CircleModuleDrawer"
    SQUARE = "SquareModuleDrawer"
    GAPPED = "GappedSquareModuleDrawer"
    HORIZONTAL = "HorizontalBarsDrawer"
    VERTICAL = "VerticalBarsDrawer"


class QrColorMask(enum.Enum):
    RADIAL = "RadialGradiantColorMask"
    SQUARE = "SquareGradiantColorMask"
    HORIZONTAL = "HorizontalGradiantColorMask"
    SOLID = "SolidFillColorMask"
    VERTICAL = "VerticalGradiantColorMask"
