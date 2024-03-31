import qrcode
from qrcode.image.styledpil import StyledPilImage

from src.enums import QrColorMask, QrModuleDrawer
from qrcode.image.styles.moduledrawers.pil import (
    RoundedModuleDrawer,
    CircleModuleDrawer,
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    HorizontalBarsDrawer,
    VerticalBarsDrawer,
)
from qrcode.image.styles.colormasks import (
    RadialGradiantColorMask,
    SquareGradiantColorMask,
    HorizontalGradiantColorMask,
    SolidFillColorMask,
    VerticalGradiantColorMask,
)

module_drawer_map = {
    QrModuleDrawer.ROUNDED.value: RoundedModuleDrawer,
    QrModuleDrawer.CIRCLE.value: CircleModuleDrawer,
    QrModuleDrawer.SQUARE.value: SquareModuleDrawer,
    QrModuleDrawer.GAPPED.value: GappedSquareModuleDrawer,
    QrModuleDrawer.HORIZONTAL.value: HorizontalBarsDrawer,
    QrModuleDrawer.VERTICAL.value: VerticalBarsDrawer,
}

color_mask_map = {
    QrColorMask.RADIAL.value: RadialGradiantColorMask,
    QrColorMask.SQUARE.value: SquareGradiantColorMask,
    QrColorMask.HORIZONTAL.value: HorizontalGradiantColorMask,
    QrColorMask.SOLID.value: SolidFillColorMask,
    QrColorMask.VERTICAL.value: VerticalGradiantColorMask,
}


def generate_qr_code(
    photo_url: str, module_drawer: QrModuleDrawer, color_mask: QrColorMask, box_size: int
) -> StyledPilImage:
    """
    Method generates QR code with passed parameters and holds the photo URL.

    :param box_size: The size of QR code image box.
    :type box_size: int.
    :param photo_url: Photo URL.
    :type photo_url: str.
    :param module_drawer: QR code param that defines the shape of the image.
    :type module_drawer: QrModuleDrawer.
    :param color_mask: QR code param that defines the color of the image.
    :type color_mask: QrColorMask.
    :return: QR code image.
    :rtype: StyledPilImage.
    """
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=box_size)
    qr.add_data(photo_url)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=module_drawer_map[module_drawer.value](),
        color_mask=color_mask_map[color_mask.value](),
    )
    return img
