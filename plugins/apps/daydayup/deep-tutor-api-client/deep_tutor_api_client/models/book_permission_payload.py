from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.book_permission_payload_default import BookPermissionPayloadDefault, check_book_permission_payload_default
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.books import Books


T = TypeVar("T", bound="BookPermissionPayload")


@_attrs_define
class BookPermissionPayload:
    """
    Attributes:
        create (bool | Unset):  Default: True.
        default (BookPermissionPayloadDefault | Unset):  Default: 'none'.
        books (Books | Unset):
    """

    create: bool | Unset = True
    default: BookPermissionPayloadDefault | Unset = "none"
    books: Books | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        create = self.create

        default: str | Unset = UNSET
        if not isinstance(self.default, Unset):
            default = self.default

        books: dict[str, Any] | Unset = UNSET
        if not isinstance(self.books, Unset):
            books = self.books.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if create is not UNSET:
            field_dict["create"] = create
        if default is not UNSET:
            field_dict["default"] = default
        if books is not UNSET:
            field_dict["books"] = books

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.books import Books  # noqa: PLC0415

        d = dict(src_dict)
        create = d.pop("create", UNSET)

        _default = d.pop("default", UNSET)
        default: BookPermissionPayloadDefault | Unset
        if isinstance(_default, Unset):
            default = UNSET
        else:
            default = check_book_permission_payload_default(_default)

        _books = d.pop("books", UNSET)
        books: Books | Unset
        if isinstance(_books, Unset):
            books = UNSET
        else:
            books = Books.from_dict(_books)

        book_permission_payload = cls(
            create=create,
            default=default,
            books=books,
        )

        book_permission_payload.additional_properties = d
        return book_permission_payload

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
