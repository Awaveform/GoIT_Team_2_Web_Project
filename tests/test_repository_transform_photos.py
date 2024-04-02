import unittest
from typing import Type
from unittest.mock import MagicMock, patch

import cloudinary
import pydantic
from fastapi import HTTPException, status
from qrcode.image.styledpil import StyledPilImage
from sqlalchemy.orm import Session

from src.database.models import User, Photo
from src.enums import PhotoEffect, PhotoGravity, QrModuleDrawer, QrColorMask
from src.repository.transform_photos import (
    apply_transformation,
    _save_transformed_photo_to_db,
    _update_orig_photo_with_transformed_photo,
    _create_transformed_photo_in_db,
    generate_photo_qr_code
)
from src.schemas import TransformPhotoModel, PhotoQrCodeModel
from src.utils.qr_code import module_drawer_map, color_mask_map


class TestTransformPhotos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.photo_url = "https://res.cloudinary.com/image/upload/6AQ8KKI6.jpg"
        self.transformed_url = "https://res.cloudinary.com/image/upload/7TGHVBVBV.jpg"
        self.photo_id = 1

    async def test_create_transformed_photo_in_db(self):
        exp_transformed_photo: Photo = Photo(
            url=self.transformed_url,
            description="Transformed photo",
            created_by=self.user.id,
            original_photo_id=self.photo_id,
            is_transformed=True,
        )
        transformed_photo: Photo = await _create_transformed_photo_in_db(
            db=self.session,
            orig_photo=Photo(id=self.photo_id),
            photo_url=self.transformed_url,
            updated_by=self.user.id,
            photo_description="Transformed photo",
        )
        assert exp_transformed_photo.is_transformed == transformed_photo.is_transformed
        assert exp_transformed_photo.url == transformed_photo.url
        assert exp_transformed_photo.created_by == transformed_photo.created_by

    async def test_update_orig_photo_with_transformed_photo(self):
        orig_photo_desc, transformed_photo_desc = (
            "Original photo",
            "Transformed photo",
        )
        orig_photo: Photo = Photo(
            id=self.photo_id,
            url=self.photo_url,
            description=orig_photo_desc,
            created_by=self.user.id,
            original_photo_id=self.photo_id,
            is_transformed=False,
        )
        self.session.query().filter().first.return_value = orig_photo
        transformed_photo: Photo = await _update_orig_photo_with_transformed_photo(
            db=self.session,
            orig_photo=orig_photo,
            photo_url=self.transformed_url,
            updated_by=self.user.id,
            photo_description=transformed_photo_desc,
        )
        assert transformed_photo.is_transformed is True
        assert transformed_photo.description == transformed_photo_desc
        assert transformed_photo is orig_photo

    async def test_save_transformed_photo_to_db_when_to_override_true(self):
        orig_photo_desc, transformed_photo_desc = (
            "Original photo",
            "Transformed photo",
        )

        orig_photo: Photo = Photo(
            id=self.photo_id,
            url=self.photo_url,
            description=orig_photo_desc,
            created_by=self.user.id,
            original_photo_id=self.photo_id,
            is_transformed=False,
        )
        self.session.query().filter().first.return_value = orig_photo
        transformed_photo: Photo = await _save_transformed_photo_to_db(
            db=self.session,
            transformed_photo_url=self.transformed_url,
            updated_by=self.user.id,
            to_override_orig_photo=True,
            photo_description=transformed_photo_desc,
            orig_photo=orig_photo,
        )
        assert orig_photo is transformed_photo
        assert transformed_photo.is_transformed is True
        assert transformed_photo.url == self.transformed_url

    async def test_save_transformed_photo_to_db_when_to_override_false(self):
        orig_photo_desc, transformed_photo_desc = (
            "Original photo",
            "Transformed photo",
        )
        orig_photo: Photo = Photo(
            url=self.photo_url,
            description="Transformed photo",
            created_by=self.user.id,
            original_photo_id=self.photo_id,
            is_transformed=False,
        )
        transformed_photo: Photo = await _save_transformed_photo_to_db(
            db=self.session,
            transformed_photo_url=self.transformed_url,
            updated_by=self.user.id,
            to_override_orig_photo=False,
            photo_description=transformed_photo_desc,
            orig_photo=orig_photo,
        )
        assert transformed_photo.is_transformed
        assert orig_photo.created_by == transformed_photo.created_by
        assert orig_photo is not transformed_photo
        assert orig_photo.url != transformed_photo.url

    @patch("cloudinary.uploader.upload")
    async def test_apply_transformation_to_override_true(self, mock_cloud_upload):
        mock_cloud_upload.return_value = {"secure_url": self.transformed_url}

        orig_photo_desc, transformed_photo_desc = (
            "Original photo",
            "Transformed photo",
        )
        orig_photo: Photo = Photo(
            id=self.photo_id,
            url=self.photo_url,
            description=orig_photo_desc,
            created_by=self.user.id,
            original_photo_id=self.photo_id,
            is_transformed=False,
        )
        self.session.query().filter().first.return_value = orig_photo
        transform_body = TransformPhotoModel(
            to_override=True,
            description=transformed_photo_desc,
            effect=PhotoEffect.BLUR.value,
            gravity=PhotoGravity.FACES.value
        )
        transformed_photo: Type[Photo] = await apply_transformation(
            photo=orig_photo,
            updated_by=self.user,
            body=transform_body,
            db=self.session,
        )
        assert transformed_photo is orig_photo
        assert transformed_photo.url == self.transformed_url
        assert transformed_photo.is_transformed is True

    @patch("cloudinary.uploader.upload")
    async def test_apply_transformation_to_override_false(self, mock_cloud_upload):
        mock_cloud_upload.return_value = {"secure_url": self.transformed_url}

        orig_photo_desc, transformed_photo_desc = (
            "Original photo",
            "Transformed photo",
        )
        orig_photo: Photo = Photo(
            id=self.photo_id,
            url=self.photo_url,
            description=orig_photo_desc,
            created_by=self.user.id,
            original_photo_id=self.photo_id,
            is_transformed=False,
        )
        self.session.query().filter().first.return_value = orig_photo
        transform_body = TransformPhotoModel(
            to_override=False,
            description=transformed_photo_desc,
            effect=PhotoEffect.SEPIA.value,
            gravity=PhotoGravity.AUTO.value,
            angle=20,
        )
        transformed_photo: Type[Photo] = await apply_transformation(
            photo=orig_photo,
            updated_by=self.user,
            body=transform_body,
            db=self.session,
        )
        assert transformed_photo is not orig_photo
        assert transformed_photo.url == self.transformed_url
        assert transformed_photo.is_transformed is True

    @patch("cloudinary.uploader.upload")
    async def test_apply_transformation_to_override_error_upload(
            self, mock_cloud_upload
    ):
        mock_cloud_upload.side_effect = cloudinary.exceptions.Error("upload error")

        orig_photo_desc, transformed_photo_desc = (
            "Original photo",
            "Transformed photo",
        )
        orig_photo: Photo = Photo(
            id=self.photo_id,
            url=self.photo_url,
            description=orig_photo_desc,
            created_by=self.user.id,
            original_photo_id=self.photo_id,
            is_transformed=False,
        )
        self.session.query().filter().first.return_value = orig_photo
        transform_body = TransformPhotoModel(
            to_override=False,
            description=transformed_photo_desc,
            effect=PhotoEffect.SEPIA.value,
            gravity=PhotoGravity.AUTO.value,
            angle=20,
        )
        try:
            await apply_transformation(
                photo=orig_photo,
                updated_by=self.user,
                body=transform_body,
                db=self.session,
            )
        except HTTPException as actual_http_err:
            exp_http_err = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error occurred during image transformation: 'upload error'",
            )
            assert exp_http_err.status_code == actual_http_err.status_code
            assert exp_http_err.detail == actual_http_err.detail
        else:
            raise AssertionError("The error wasn't raised when expected")


class TestGenerateQrCodeForPhotos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.photo_url = "https://res.cloudinary.com/image/upload/6AQ8KKI6.jpg"
        self.photo_id = 1

    async def test_generate_photo_qr_code(self):
        photo: Photo = Photo(
            id=self.photo_id, url=self.photo_url
        )
        params = [PhotoQrCodeModel(module_drawer=QrModuleDrawer.VERTICAL,
                                   color_mask=QrColorMask.VERTICAL, box_size=10),
                  PhotoQrCodeModel(module_drawer=QrModuleDrawer.SQUARE,
                                   color_mask=QrColorMask.RADIAL, box_size=5),
                  PhotoQrCodeModel(module_drawer=QrModuleDrawer.CIRCLE,
                                   color_mask=QrColorMask.SOLID, box_size=100.5)
                  ]
        for param_set in params:
            img: StyledPilImage = await generate_photo_qr_code(photo=photo,
                                                               params=param_set)
            assert isinstance(img, StyledPilImage)
            assert img.box_size == param_set.box_size
            assert isinstance(img.color_mask, color_mask_map[param_set.color_mask.value])
            assert isinstance(img.module_drawer, module_drawer_map[
                param_set.module_drawer.value])

    async def test_generate_photo_qr_code_w_incorrect_params(self):
        params = [{"module_drawer": "Test module drawer",
                   "color_mask": QrColorMask.VERTICAL, "box_size": 10},
                  {"module_drawer": QrModuleDrawer.SQUARE,
                   "color_mask": "Test color mask", "box_size": 10},
                  {"module_drawer": QrModuleDrawer.CIRCLE,
                   "color_mask": QrColorMask.RADIAL, "box_size": -1},
                  ]
        for param_set in params:
            try:
                PhotoQrCodeModel(**param_set)
            except pydantic.error_wrappers.ValidationError as err:
                print(err)
            else:
                raise AssertionError("Error wasn't raised when expected")
