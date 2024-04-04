import unittest
from datetime import datetime

from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.database.models.photo import Photo
from src.database.models.user import User
from src.repository.comments import (
    create_comment,
    get_comments,
    update_comment,
    delete_comment,
)
from src.database.models.photo_comment import PhotoComment
from src.schemas import CommentSchema


class TestCommentPhoto(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = MagicMock(spec=Session)
        self.user = User(id=1)
        self.existing_photo = Photo(id=1)
        self.not_existing_photo = Photo(id=999)
        self.comment = CommentSchema(comment="Test comment")
        self.created_at = datetime.now()
        self.limit = 10
        self.valid_offset = 0
        self.invalid_offset = -10
        self.comments_list = [
            PhotoComment(
                id=1,
                comment="Test comment 1",
                created_at=self.created_at,
                updated_at=None,
                photo_id=self.existing_photo,
                created_by=self.user.id,
            ),
            PhotoComment(
                id=2,
                comment="Test comment 2",
                created_at=self.created_at,
                updated_at=None,
                photo_id=self.existing_photo,
                created_by=self.user.id,
            ),
        ]

    async def test_create_comment_success(self):
        result: PhotoComment = await create_comment(
            photo_id=self.existing_photo,
            comment=self.comment,
            current_user=self.user,
            db=self.db,
        )
        self.assertEqual(result.comment, "Test comment")

        self.assertEqual(result.created_by, self.user.id)
        self.db.add.assert_called_once_with(result)

    async def test_get_comments_valid_list(self):
        exp_comments = self.comments_list
        self.db.query().filter().order_by().offset().limit().all.return_value = (
            exp_comments
        )

        comments = await get_comments(
            photo_id=self.existing_photo.id,
            limit=self.limit,
            offset=0,
            db=self.db,
        )
        self.assertEqual(comments, exp_comments)
        self.assertEqual(comments[0].comment, "Test comment 1")
        self.assertEqual(comments[1].comment, "Test comment 2")

    async def test_get_comments_invalid_photo_id(self):
        self.db.query().filter().order_by().offset().limit().all.return_value = []

        comments = await get_comments(
            photo_id=self.not_existing_photo.id,
            limit=self.limit,
            offset=self.valid_offset,
            db=self.db,
        )
        self.assertEqual(comments, [])

    async def test_get_comments_invalid_offset(self):
        self.db.query().filter().order_by().offset().limit().all.return_value = []

        comments = await get_comments(
            photo_id=self.existing_photo.id,
            limit=self.limit,
            offset=self.invalid_offset,
            db=self.db,
        )
        self.assertEqual(comments, [])

    async def test_update_comments_sucess(self):
        existing_comment = self.comments_list[0]

        self.db.execute.return_value.scalar_one_or_none.return_value = existing_comment

        updated_comment_data = CommentSchema(comment="Updated comment")
        updated_comment = await update_comment(
            comment_id=existing_comment.id,
            photo_id=self.existing_photo.id,
            updated_comment=updated_comment_data,
            current_user=self.user,
            db=self.db,
        )

        self.assertEqual(updated_comment.comment, "Updated comment")
        self.assertIsNotNone(updated_comment.updated_at)
        self.assertEqual(updated_comment.updated_at, existing_comment.updated_at)

    async def test_update_comment_not_found(self):
        not_existing_comment = self.comments_list[0]

        self.db.execute.return_value.scalar_one_or_none.return_value = None

        updated_comment_data = CommentSchema(comment="Updated comment")
        updated_comment = await update_comment(
            comment_id=not_existing_comment.id,
            photo_id=self.existing_photo.id,
            updated_comment=updated_comment_data,
            current_user=self.user,
            db=self.db,
        )

        self.assertIsNone(updated_comment)

    async def test_delete_comment_existing(self):
        existing_comment = self.comments_list[0]

        self.db.execute.return_value.scalar_one_or_none.return_value = existing_comment

        deleted_comment = await delete_comment(
            comment_id=existing_comment.id, photo_id=self.existing_photo.id, db=self.db
        )

        self.assertEqual(deleted_comment, existing_comment)
        self.db.delete.assert_called_once_with(existing_comment)
        self.db.commit.assert_called_once()

    async def test_delete_comment_not_existing(self):
        not_existing_comment = self.comments_list[0]

        self.db.execute.return_value.scalar_one_or_none.return_value = None

        deleted_comment = await delete_comment(
            comment_id=not_existing_comment.id,
            photo_id=self.existing_photo.id,
            db=self.db,
        )

        self.assertIsNone(deleted_comment)
        self.db.delete.assert_not_called()
        self.db.commit.assert_not_called()
