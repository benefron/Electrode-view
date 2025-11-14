"""
This modules contains the functions and classes to handle the electrode map corresponding to the MEA chip

Author: Lukas Fan
"""

from collections import namedtuple
from collections.abc import Sequence, MutableSequence
from enum import Enum, auto
from functools import cached_property
from logging import Logger
from typing import Iterator, List, Optional, Any

import numpy as np
from numpy import typing
from typing_extensions import override
from typing import List, Union, Any



logger = Logger(__name__)

Coord = namedtuple("Coord", ["x", "y"])
_2DIndex = tuple["WellNumber", Coord]
_WELL_SIZE = Coord(16, 16)
NUM_PIXEL = _WELL_SIZE.x * _WELL_SIZE.y
MULTIPLEX_FACTOR = Coord(2, 2)
WELL_ELECTRODE = tuple([sz * mf for sz, mf in zip(_WELL_SIZE, MULTIPLEX_FACTOR)])
NUM_ELECTRODE = NUM_PIXEL * MULTIPLEX_FACTOR.x * MULTIPLEX_FACTOR.y


class WellNumber(Enum):
    WELL_1 = 1
    WELL_2 = 2
    WELL_3 = 3
    WELL_4 = 4
    WELL_5 = 5
    WELL_6 = 6
    WELL_7 = 7
    WELL_8 = 8
    WELL_9 = 9
    WELL_10 = 10
    WELL_11 = 11
    WELL_12 = 12
    WELL_13 = 13
    WELL_14 = 14
    WELL_15 = 15
    WELL_16 = 16

TOTAL_NUM_ELECTRODE = NUM_ELECTRODE * WellNumber.__len__()


class OpMode(Enum):
    VSTIM = auto()
    ISTIM = auto()
    REC = auto()


def _top_right_to_bottom_left_column(indices: np.ndarray) -> np.ndarray:
    return np.fliplr(indices.transpose())


def _bottom_right_to_top_left_column(indices: np.ndarray) -> np.ndarray:
    return np.flipud(np.fliplr(indices.transpose()))


def _top_left_to_bottom_right_column(indices: np.ndarray) -> np.ndarray:
    return indices.transpose()


def _bottom_left_to_top_right_column(indices: np.ndarray) -> np.ndarray:
    return np.flipud(indices.transpose())


def _to_well_shape(start: int, end: int) -> np.ndarray:
    assert (end - start) == 255
    return np.arange(start=start, stop=end + 1).reshape(_WELL_SIZE)


def _get_element_index(arr: typing.ArrayLike, val) -> list[Coord]:
    result = np.where(arr == val)
    return [Coord(result[0], result[1])]


def _dict_inversion(dict_: dict) -> dict:
    inv_dict: dict = {}

    for k, v in dict_.items():
        for x in v.flatten():
            idx = np.nonzero(v == x)
            inv_dict.setdefault(x, (k, idx))

    return inv_dict


_CONVERSION_DICT = {
    WellNumber.WELL_5: _top_right_to_bottom_left_column(_to_well_shape(1, 256)),  # noqa
    WellNumber.WELL_7: _top_right_to_bottom_left_column(
        _to_well_shape(257, 512)
    ),  # noqa
    WellNumber.WELL_6: _bottom_right_to_top_left_column(
        _to_well_shape(513, 768)
    ),  # noqa
    WellNumber.WELL_8: _bottom_right_to_top_left_column(
        _to_well_shape(769, 1024)
    ),  # noqa
    WellNumber.WELL_13: _bottom_right_to_top_left_column(
        _to_well_shape(1025, 1280)
    ),  # noqa
    WellNumber.WELL_15: _bottom_right_to_top_left_column(
        _to_well_shape(1281, 1536)
    ),  # noqa
    WellNumber.WELL_14: _top_right_to_bottom_left_column(
        _to_well_shape(1537, 1792)
    ),  # noqa
    WellNumber.WELL_16: _top_right_to_bottom_left_column(
        _to_well_shape(1793, 2048)
    ),  # noqa
    WellNumber.WELL_1: _top_left_to_bottom_right_column(
        _to_well_shape(2049, 2304)
    ),  # noqa
    WellNumber.WELL_3: _top_left_to_bottom_right_column(
        _to_well_shape(2305, 2560)
    ),  # noqa
    WellNumber.WELL_2: _bottom_left_to_top_right_column(
        _to_well_shape(2561, 2816)
    ),  # noqa
    WellNumber.WELL_4: _bottom_left_to_top_right_column(
        _to_well_shape(2817, 3072)
    ),  # noqa
    WellNumber.WELL_9: _bottom_left_to_top_right_column(
        _to_well_shape(3073, 3328)
    ),  # noqa
    WellNumber.WELL_11: _bottom_left_to_top_right_column(
        _to_well_shape(3329, 3584)
    ),  # noqa
    WellNumber.WELL_10: _top_left_to_bottom_right_column(
        _to_well_shape(3585, 3840)
    ),  # noqa
    WellNumber.WELL_12: _top_left_to_bottom_right_column(
        _to_well_shape(3841, 4096)
    ),  # noqa
}

_CONVERSION_DICT_INV = _dict_inversion(_CONVERSION_DICT)


def _index_to_pixel(w) -> List[Union[int, Any]]:
    return [4 * (x - 1) + i for x in w for i in range(4)]


WELL_PIXEL = {
    WellNumber.WELL_1: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_1].flat),
    WellNumber.WELL_2: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_2].flat),
    WellNumber.WELL_3: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_3].flat),
    WellNumber.WELL_4: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_4].flat),
    WellNumber.WELL_5: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_5].flat),
    WellNumber.WELL_6: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_6].flat),
    WellNumber.WELL_7: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_7].flat),
    WellNumber.WELL_8: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_8].flat),
    WellNumber.WELL_9: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_9].flat),
    WellNumber.WELL_10: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_10].flat),
    WellNumber.WELL_11: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_11].flat),
    WellNumber.WELL_12: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_12].flat),
    WellNumber.WELL_13: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_13].flat),
    WellNumber.WELL_14: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_14].flat),
    WellNumber.WELL_15: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_15].flat),
    WellNumber.WELL_16: _index_to_pixel(_CONVERSION_DICT[WellNumber.WELL_16].flat),
}


def get_canonical_index(index2d: _2DIndex) -> int:
    well_number = index2d[0]
    coordinate = tuple(list(map(lambda x: x - 1, index2d[1])))

    return _CONVERSION_DICT[well_number][coordinate.y, coordinate.x]


def get_well_index(canonical_idx: int) -> Optional[WellNumber]:
    return _CONVERSION_DICT_INV.get(canonical_idx)[0]


def get_well_coord(canonical_idx: int) -> Coord:
    return _CONVERSION_DICT_INV.get(canonical_idx)[1]

def get_2d_index(canonical_idx: int) -> _2DIndex:
    well_number = get_well_index(canonical_idx)
    if well_number is None:
        raise LookupError("Canonical Index does not exist")

    result = _get_element_index(_CONVERSION_DICT[well_number], canonical_idx)
    assert len(result) == 1
    coord = (result[0][0] + 1, result[0][1] + 1)

    return (well_number, coord)


class ElecMapIndex(object):
    # Canonical index are ordered in a way so that when we iterate through it,
    # it gives the top left electrode of the well to the bottom right of the
    # well.
    # e.g. | 9 8 7 |
    #      | 6 5 4 | -> [9, 8, 7, 6, 5, 4, 3, 2, 1]
    #      | 3 2 1 |

    __slot__ = ("_canonical_idx", "_index2d")

    version = "4.8.0.0"

    def __init__(
            self, index2d: Optional[_2DIndex] = None, canonical_idx: Optional[int] = None
    ) -> None:
        if canonical_idx is not None and index2d is not None:
            logger.error("Cannot have both canonical index and 2d index defined")
            raise RuntimeError("Both canonical and 2d index is defined")
        if canonical_idx is not None:
            self._canonical_idx = canonical_idx
            self._index2d = get_2d_index(self.canonical_idx)
        elif index2d is not None:
            self._index2d = index2d
            self._canonical_idx = get_canonical_index(self.index2d)

    @property
    def canonical_idx(self):
        return self._canonical_idx

    @property
    def index2d(self):
        return self._index2d

    @property
    def well_number(self) -> WellNumber:
        return self.index2d[0]

    @property
    def electrode_coordinate(self) -> tuple[int, int]:
        return self.index2d[1]

    @property
    def WELL_SIZE(self) -> tuple[int, int]:
        return _WELL_SIZE

    def __str__(self) -> str:
        return f"Well {self.well_number.value} {self.electrode_coordinate} [{self.canonical_idx}]"

    def __repr__(self) -> str:
        return f"pymea.model.elecmap.ElecMapIndex({self.index2d}, {self.canonical_idx})"


class Electrode(object):
    __slot__ = ("index", "state", "mode")

    def __init__(
            self,
            index: ElecMapIndex,
            multiplexer: int,
            state: Optional[bool] = None,
            mode: OpMode = OpMode.VSTIM,
    ) -> None:
        self.index = index
        self.multiplexer = multiplexer
        if state is None:
            self.state = False
        else:
            self.state = state
        self.mode = mode


class ElecWell(Sequence):
    __slot__ = ("well_number", "electrodes")

    def __init__(
            self, well_number: WellNumber, electrodes: np.ndarray[Electrode]
    ) -> None:
        self.well_number = well_number
        self.electrodes: np.ndarray[Electrode] = electrodes
        super().__init__()

    @override
    def __getitem__(self, key):
        return self.electrodes.flat[key]

    @override
    def __len__(self):
        return self.electrodes.flat.__len__()

    def change_well(self, well_number: WellNumber):
        self.well_number = well_number
        for electrode, idx in zip(
                self.electrodes.flat, _CONVERSION_DICT[well_number].flat
        ):
            # Loop multiplexed electrodes
            for e in electrode:
                e.index = ElecMapIndex(canonical_idx=idx)

def get_electrodes(indices) -> list[Electrode]:
    if indices is np.ndarray[ElecMapIndex]:
        return np.vectorize(lambda x: [Electrode(x, i) for i in range(4)])(indices)
    else:
        return [Electrode(indices, i) for i in range(4)]


def get_well(well_number: WellNumber) -> ElecWell:
    return ElecWell(
        well_number,
        np.vectorize(lambda x: get_electrodes(ElecMapIndex(canonical_idx=x)))(
            _CONVERSION_DICT[well_number]
        ),
    )
