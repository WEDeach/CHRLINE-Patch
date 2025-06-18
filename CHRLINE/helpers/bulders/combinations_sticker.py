from typing import List, Optional


class StickerLayoutInfo:
    def __init__(
        self,
        width: Optional[float] = None,
        height: Optional[float] = None,
        rotation: Optional[float] = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
    ):
        self.__width = width
        self.__height = height
        self.__rotation = rotation
        self.__x = x
        self.__y = y

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def rotation(self):
        return self.__rotation

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y
    
    def wrap(self):
        return [
            [4, 1, self.width],
            [4, 2, self.height],
            [4, 3, self.rotation],
            [4, 4, self.x],
            [4, 5, self.y],
        ]


class StickerLayoutStickerInfo:
    def __init__(
        self,
        stickerId: Optional[int] = None,
        productId: Optional[int] = None,
        stickerHash: Optional[str] = None,
        stickerOptions: Optional[str] = None,
        stickerVersion: Optional[int] = None,
    ):
        self.__stickerId = stickerId
        self.__productId = productId
        self.__stickerHash = stickerHash
        self.__stickerOptions = stickerOptions
        self.__stickerVersion = stickerVersion

    @property
    def sticker_id(self):
        return self.__stickerId

    @property
    def product_id(self):
        return self.__productId

    @property
    def sticker_hash(self):
        return self.__stickerHash

    @property
    def sticker_options(self):
        return self.__stickerOptions

    @property
    def sticker_version(self):
        return self.__stickerVersion

    def wrap(self):
        return [
            [10, 1, self.sticker_id],
            [10, 2, self.product_id],
            [11, 3, self.sticker_hash],
            [11, 4, self.sticker_options],
            [10, 5, self.sticker_version],
        ]

class StickerLayout:
    def __init__(
        self,
        layoutInfo: Optional[StickerLayoutInfo] = None,
        stickerInfo: Optional[StickerLayoutStickerInfo] = None,
    ):
        self.__layoutInfo = layoutInfo
        self.__stickerInfo = stickerInfo

    @property
    def layout_info(self):
        return self.__layoutInfo

    @property
    def sticker_info(self):
        return self.__stickerInfo

    def wrap(self):
        r = []
        if self.layout_info:
           r.append([12, 1, self.layout_info.wrap()]) 
        if self.sticker_info:
           r.append([12, 2, self.sticker_info.wrap()]) 
        return r


class CombinationStickerMetadata:
    def __init__(
        self,
        version: Optional[int] = None,
        canvasWidth: Optional[float] = None,
        canvasHeight: Optional[float] = None,
        stickerLayouts: Optional[List[StickerLayout]] = None,
    ):
        self.__version = version
        self.__canvasWidth = canvasWidth
        self.__canvasHeight = canvasHeight
        self.__stickerLayouts = stickerLayouts

    @property
    def version(self):
        return self.__version

    @property
    def canvas_width(self):
        return self.__canvasWidth

    @property
    def canvas_height(self):
        return self.__canvasHeight

    @property
    def sticker_layouts(self):
        return self.__stickerLayouts

    def set_version(self, new_version: int):
        self.__version = new_version

    def set_canvas_width(self, new_width: float):
        self.__canvasWidth = new_width

    def set_canvas_height(self, new_height: float):
        self.__canvasHeight = new_height

    def set_sticker_layouts(self, sticker_layouts: List[StickerLayout]):
        self.__stickerLayouts = sticker_layouts

    def add_sticker_layout(self, layout: StickerLayout):
        if not self.__stickerLayouts:
            self.__stickerLayouts = []
        self.__stickerLayouts.append(layout)

    @staticmethod
    def new():
        """Create new combination sticker metadata builder"""
        r = CombinationStickerMetadata()
        r.set_version(1)
        r.set_canvas_width(630.0)
        r.set_canvas_height(630.0)
        r.set_sticker_layouts([])
        return r
    
    def wrap(self):
        layouts = []
        if self.sticker_layouts:
            for i in self.sticker_layouts:
                layouts.append(i.wrap())
        return [
            [10, 1, self.version],
            [4, 2, self.canvas_width],
            [4, 3, self.canvas_height],
            [15, 4, [12, layouts]],
        ]


class CombinationStickerStickerData:
    def __init__(
        self,
        packageId: Optional[str] = None,
        stickerId: Optional[str] = None,
        version: Optional[int] = None,
    ):
        self.__packageId = packageId
        self.__stickerId = stickerId
        self.__version = version

    @property
    def package_id(self):
        return self.__packageId

    @property
    def sticker_id(self):
        return self.__stickerId

    @property
    def version(self):
        return self.__version

    def __eq__(self, other):
        if isinstance(other, CombinationStickerStickerData):
            return (
                self.package_id == other.package_id
                and self.sticker_id == other.sticker_id
                and self.version == other.version
            )
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def wrap(self):
        return [
            [11, 1, self.package_id],
            [11, 2, self.sticker_id],
            [10, 3, self.version],
        ]


class CombinationSticker:
    def __init__(
        self,
        metadata: Optional[CombinationStickerMetadata] = None,
        stickers: Optional[List[CombinationStickerStickerData]] = None,
        prev_id: Optional[str] = None,
    ):
        self.__metadata = metadata
        self.__stickers = stickers
        self.__idOfPreviousVersionOfCombinationSticker = prev_id

    @staticmethod
    def new():
        """Create new combination sticker builder"""
        meta = CombinationStickerMetadata.new()
        stickers = []
        return CombinationSticker(meta, stickers)

    @property
    def metadata(self):
        return self.__metadata

    @property
    def stickers(self):
        if self.__stickers:
            return self.__stickers
        return []

    @property
    def id_of_previous_version_of_combination_sticker(self):
        return self.__idOfPreviousVersionOfCombinationSticker

    def add_sticker_data(self, pkgId: int, stkId: int, ver: int):
        stk_data = CombinationStickerStickerData(str(pkgId), str(stkId), ver)
        if stk_data not in self.stickers:
            if not self.__stickers:
                self.__stickers = []
            self.__stickers.append(stk_data)

    def add_sticker_layout(
        self, layoutInfo: StickerLayoutInfo, stickerInfo: StickerLayoutStickerInfo
    ):
        l = StickerLayout(layoutInfo, stickerInfo)
        if not self.__metadata:
            self.__metadata = CombinationStickerMetadata.new()
        self.__metadata.add_sticker_layout(l)
        if (
            stickerInfo.product_id
            and stickerInfo.sticker_id
            and stickerInfo.sticker_version
        ):
            self.add_sticker_data(
                stickerInfo.product_id,
                stickerInfo.sticker_id,
                stickerInfo.sticker_version,
            )
        else:
            raise ValueError("StickerInfo not init.")

    def new_layout_info(
        self, width: float, height: float, rotation: float, x: float, y: float
    ):
        """Create new layout info."""
        return StickerLayoutInfo(width, height, rotation, x, y)

    def new_layout_sticker_info(
        self,
        stickerId: int,
        productId: int,
        stickerHash: Optional[str] = None,
        stickerOptions: Optional[str] = None,
        stickerVersion: int = 1,
    ):
        """Create new layout sticker info."""
        return StickerLayoutStickerInfo(
            stickerId, productId, stickerHash, stickerOptions, stickerVersion
        )
        
    def set_previous_combination_sticker_id(self, new_val: str):
        self.__idOfPreviousVersionOfCombinationSticker = new_val
    
    def wrap(self):
        r = []
        sl = []
        if self.metadata:
            r.append([12, 1, self.metadata.wrap()])
        if self.stickers:
            for i in self.stickers:
                sl.append(i.wrap())
        r.append([15, 2, [12, sl]])
        if self.id_of_previous_version_of_combination_sticker:
            r.append([11, 3, self.id_of_previous_version_of_combination_sticker])
        return r
