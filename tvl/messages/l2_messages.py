from typing import Any, ContextManager, Tuple

from typing_extensions import Annotated

from ..crypto.hash import crc16
from .datafield import AUTO, U8Scalar, U16Scalar, params
from .exceptions import UnauthorizedInstantiationError
from .message import Message


class L2Frame(Message, is_base=True):
    """Base class for L2 messages"""

    length: Annotated[U8Scalar, params(is_data=False)] = AUTO  # type: ignore
    crc: Annotated[U16Scalar, params(priority=999, is_data=False)] = AUTO  # type: ignore

    def set_length_if_auto(self) -> ContextManager[None]:
        """Update the LENGTH field of the message if set to AUTO."""
        if (length_save := self.length.value) is AUTO:
            _length = 0
            for _, field in self:
                if not field.params.is_data:
                    continue
                try:
                    _length += len(field.value) * field.params.dtype.nb_bytes
                except TypeError:
                    _length += field.params.dtype.nb_bytes
            self.length.value = _length
        return self._restore(self.length, length_save)

    def has_valid_crc(self) -> bool:
        """Check the CRC field of the message.

        Returns:
            True if the crc is valid, False otherwise
        """
        return self.crc.value is AUTO or self.crc.value == self.compute_crc()

    def update_crc(self) -> None:
        """Update crc of the message."""
        self.crc.value = self.compute_crc()

    def compute_crc(self) -> int:
        """Compute crc of the message.

        Returns:
            crc of the message
        """
        return self._get_data_and_crc(force_auto_crc=True)[1]

    def _get_data_and_crc(self, *, force_auto_crc: bool = False) -> Tuple[bytes, int]:
        with self.set_length_if_auto():
            data = b"".join(field.to_bytes() for name, field in self if name != "crc")

            if (crc := self.crc.value) is AUTO or force_auto_crc:
                crc = crc16(data)

            return data, crc

    def to_bytes(self) -> bytes:
        """Serialize the message to bytes.

        Returns:
            bytes representation of the message
        """
        with self._restore(self.crc, self.crc.value):
            data, self.crc.value = self._get_data_and_crc()
            return data + self.crc.to_bytes()


class L2Request(L2Frame):
    """Base class for L2 messages sent to the TROPIC01"""

    id: Annotated[U8Scalar, params(priority=-999, is_data=False)] = AUTO  # type: ignore

    def __init__(self, **kwargs: Any) -> None:
        try:
            self.ID
        except AttributeError:
            raise UnauthorizedInstantiationError(
                f"Instantiating {self.__class__} forbidden: ID undefined."
            ) from None
        super().__init__(**kwargs)

    def set_id_if_auto(self) -> ContextManager[None]:
        """Update the ID field of the message if set to AUTO."""
        if (id_save := self.id.value) is AUTO:
            self.id.value = self.ID
        return self._restore(self.id, id_save)

    def has_valid_id(self) -> bool:
        """Check if the ID field is valid.

        Returns:
            True if the instance id matches with that of the class
        """
        return self.id.value is AUTO or self.id.value == self.ID

    def _get_data_and_crc(self, *, force_auto_crc: bool = False) -> Tuple[bytes, int]:
        with self.set_id_if_auto():
            return super()._get_data_and_crc(force_auto_crc=force_auto_crc)


class L2Response(L2Frame):
    """Base class for L2 messages sent from the TROPIC01"""

    status: Annotated[U8Scalar, params(priority=-999, is_data=False)]
