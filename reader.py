
from typing import Optional

CHUNK_TILES = 1
CHUNK_SPRITES = 2
CHUNK_MAP = 4
CHUNK_CODE = 5
CHUNK_FLAGS = 6
CHUNK_SAMPLES = 9
CHUNK_WAVEFORM = 10
CHUNK_PALETTE = 12
CHUNK_MUSIC = 14
CHUNK_PATTERNS = 15
CHUNK_DEFAULT = 17
CHUNK_SCREEN = 18
CHUNK_BINARY = 19
CHUNK_COVER_DEP = 3     # Deprecated
CHUNK_PATTERNS_DEP = 13 # Deprecated
CHUNK_CODE_ZIP = 16     # Deprecated

CHUNK_TYPES = {
	1 	: "TILES",
	2 	: "SPRITES",
	4 	: "MAP",
	5 	: "CODE",
	6 	: "FLAGS",
	9 	: "SAMPLES",
	10 	: "WAVEFORM",
	12 	: "PALETTE",
	14 	: "MUSIC",
	15 	: "PATTERNS",
	17 	: "DEFAULT",
	18 	: "SCREEN",
	19 	: "BINARY",
	3 	: "COVER_DEP",
	13 	: "PATTERNS_DEP",
	16 	: "CODE_ZIP"
}

class Chunk :
	def __init__(self, cnk_type: int, cnk_bank: int, cnk_data: list[int]) -> None:
		self.type_int: int = cnk_type
		self.type_str: str = CHUNK_TYPES[cnk_type] if cnk_type in CHUNK_TYPES else "(reserved)"

		self.bank: int = cnk_bank

		self.data: list[int] = cnk_data

	def __str__(self) -> str:
		return f"{self.type_str} ({self.type_int}) bank {self.bank} size: {len(self.data)}B"

	def saveBytes(self) :
		save: list[bytes] = []

		save.append(
			((self.bank << 3) + self.type_int).to_bytes()
		)

		save.append(
			(len(self.data) & 0b0000000011111111).to_bytes()
		)
		save.append(
			(len(self.data) >> 8).to_bytes()
		)

		# This would be the reserved byte so we should
		# put 0 here but it's funnnier if we put a
		# random number
		save.append(
			(5).to_bytes()
		)

		if len(self.data) > 0 :
			rm_trailing_zeros: list[int] = self.data.copy()
			while rm_trailing_zeros[-1] == 0 :
				rm_trailing_zeros.pop(-1)

			save.extend(
				[x.to_bytes() for x in rm_trailing_zeros]
			)

		return save

class Tiles(Chunk) :
	def __init__(self, cnk_type: int, cnk_bank: int, cnk_data: list[int]) -> None:
		super().__init__(cnk_type, cnk_bank, cnk_data)

	def setPixelOfSprite(self, sprite_id: int, x: int, y: int, col: int) :
		if sprite_id < 0 or sprite_id > 255 :
			raise ValueError(f"Invalid sprite id: {sprite_id}")

		if x < 0 or x > 7 :
			raise ValueError(f"Invalid x position: {x}")
		if y < 0 or y > 7 :
			raise ValueError(f"Invalid y position: {y}")

		if col < 0 or col > 15 :
			raise ValueError(f"Invalid color id: {col}")

		sprite_offset = 32 * sprite_id

		pixel_byte = sprite_offset + int(x / 2) + y * 4
		pixel_offset = x % 2

		while len(self.data) <= pixel_byte :
			self.data.append(0)

		if pixel_offset == 0 :
			self.data[pixel_byte] = (col) + (self.data[pixel_byte] & 0b11110000)
		else :
			self.data[pixel_byte] = (col << 4) + (self.data[pixel_byte] & 0b00001111)

	def getPixelOfSprite(self, sprite_id: int, x: int, y: int) -> int :
		if sprite_id < 0 or sprite_id > 255 :
			raise ValueError(f"Invalid sprite id: {sprite_id}")

		if x < 0 or x > 7 :
			raise ValueError(f"Invalid x position: {x}")
		if y < 0 or y > 7 :
			raise ValueError(f"Invalid y position: {y}")

		sprite_offset = 32 * sprite_id

		pixel_byte = sprite_offset + int(x / 2) + y * 4
		pixel_offset = x % 2

		if pixel_byte >= len(self.data) :
			return 0

		if pixel_offset == 0 :
			return self.data[pixel_byte] & 0b00001111
		else :
			return self.data[pixel_byte] >> 4

class Sprites(Chunk) :
	def __init__(self, cnk_type: int, cnk_bank: int, cnk_data: list[int]) -> None:
		super().__init__(cnk_type, cnk_bank, cnk_data)

	def setPixelOfSprite(self, sprite_id: int, x: int, y: int, col: int) :
		if sprite_id < 256 or sprite_id > 511 :
			raise ValueError(f"Invalid tile id: {sprite_id}")

		sprite_id -= 256

		if x < 0 or x > 7 :
			raise ValueError(f"Invalid x position: {x}")
		if y < 0 or y > 7 :
			raise ValueError(f"Invalid y position: {y}")

		if col < 0 or col > 15 :
			raise ValueError(f"Invalid color id: {col}")

		sprite_offset = 32 * sprite_id

		pixel_byte = sprite_offset + int(x / 2) + y * 4
		pixel_offset = x % 2

		while len(self.data) <= pixel_byte :
			self.data.append(0)

		if pixel_offset == 0 :
			self.data[pixel_byte] = (col) + (self.data[pixel_byte] & 0b11110000)
		else :
			self.data[pixel_byte] = (col << 4) + (self.data[pixel_byte] & 0b00001111)

	def getPixelOfSprite(self, sprite_id: int, x: int, y: int) -> int :
		if sprite_id < 256 or sprite_id > 511 :
			raise ValueError(f"Invalid sprite id: {sprite_id}")

		sprite_id -= 256

		if x < 0 or x > 7 :
			raise ValueError(f"Invalid x position: {x}")
		if y < 0 or y > 7 :
			raise ValueError(f"Invalid y position: {y}")

		sprite_offset = 32 * sprite_id

		pixel_byte = sprite_offset + int(x / 2) + y * 4
		pixel_offset = x % 2

		if pixel_byte >= len(self.data) :
			return 0

		if pixel_offset == 0 :
			return self.data[pixel_byte] & 0b00001111
		else :
			return self.data[pixel_byte] >> 4

class Palette(Chunk) :
	def __init__(self, cnk_type: int, cnk_bank: int, cnk_data: list[int]) -> None:
		super().__init__(cnk_type, cnk_bank, cnk_data)

	def getPaletteColor(self, col_id: int) -> tuple[int,int,int] :
		if col_id < 0 or col_id > 15 :
			raise ValueError(f"Invalid color id: {col_id}")

		col_r: int = self.data[col_id * 3]
		col_g: int = self.data[col_id * 3 + 1]
		col_b: int = self.data[col_id * 3 + 2]

		return (col_r, col_g, col_b)

	def setPaletteColor(self, col_id: int, col_r: Optional[int] = None, col_g: Optional[int] = None, col_b: Optional[int] = None) :
		if col_id < 0 or col_id > 15 :
			raise ValueError(f"Invalid color id: {col_id}")

		original = self.getPaletteColor(col_id)

		col_r = col_r if col_r != None else original[0]
		col_g = col_g if col_g != None else original[1]
		col_b = col_b if col_b != None else original[2]

		if col_r < 0 or col_r > 255 :
			raise ValueError(f"Invalid red value: {col_r}")
		if col_g < 0 or col_g > 255 :
			raise ValueError(f"Invalid green value: {col_g}")
		if col_b < 0 or col_b > 255 :
			raise ValueError(f"Invalid blue value: {col_b}")

		self.data[col_id * 3] = col_r
		self.data[col_id * 3 + 1] = col_g
		self.data[col_id * 3 + 2] = col_b

class CodeInfo :
	def __init__(self, code: str) -> None:
		headers = []
		actual = []

		for n,i in enumerate(code.splitlines()) :
			if not i.startswith("--") :
				break

			headers.append(i)
			actual = code.splitlines()[n+1:]

		self.code: str = "\n".join(actual)

		self.headers: dict[str, str] = {
			x[:x.find(":")].lstrip("-").strip():x[x.find(":")+1:].strip()
			for x in
			headers
		}

	def construct(self) :
		actual: list[str] = []

		longest = max(len(x) for x in self.headers)

		for i in self.headers :
			actual.append(f"-- {i}:{' ' * (longest - len(i))} {self.headers[i]}")

		return "\n".join(actual) + "\n" + self.code

class Code(Chunk) :
	def __init__(self, cnk_type: int, cnk_bank: int, cnk_data: list[int]) -> None:
		super().__init__(cnk_type, cnk_bank, cnk_data)

	def getCode(self) -> CodeInfo :
		code: str = ""

		for i in self.data :
			code += chr(i)

		return CodeInfo(code)

	def setCode(self, code: str) :
		info: CodeInfo = self.getCode()
		info.code = code

		txt = info.construct()

		self.data = [ord(x) for x in txt]

	def setHeaders(self, head: dict[str, str]) :
		info: CodeInfo = self.getCode()
		info.headers = head

		txt = info.construct()

		self.data = [ord(x) for x in txt]

class Map(Chunk) :
	def __init__(self, cnk_type: int, cnk_bank: int, cnk_data: list[int]) -> None:
		super().__init__(cnk_type, cnk_bank, cnk_data)

	def setMapPos(self, x: int, y: int, id: int) :
		if x < 0 or x > 239 :
			raise ValueError(f"Invalid x pos: {x}")
		if y < 0 or y > 239 :
			raise ValueError(f"Invalid y pos: {y}")

		if id < 0 or id > 255 :
			raise ValueError(f"Invalid tile id: {id}")

		while len(self.data) <= x + y * 240 :
			self.data.append(0)

		self.data[x + y * 240] = id

	def getMapPos(self, x: int, y: int) -> int :
		if x < 0 or x > 239 :
			raise ValueError(f"Invalid x pos: {x}")
		if y < 0 or y > 239 :
			raise ValueError(f"Invalid y pos: {y}")

		if len(self.data) <= x + y * 240 :
			return 0

		return self.data[x + y * 240]

class Flags(Chunk) :
	def __init__(self, cnk_type: int, cnk_bank: int, cnk_data: list[int]) -> None:
		super().__init__(cnk_type, cnk_bank, cnk_data)

	def setSpriteFlag(self, sprite_id: int, flags: list[bool]) :
		if sprite_id < 0 or sprite_id > 511 :
			raise ValueError(f"Invalid sprite id: {sprite_id}")

		if len(flags) > 8 :
			raise ValueError(f"There may be at most 8 flags assigned to a sprite")

		flg = 0
		for n,i in enumerate(flags) :
			if i :
				flg += 2 ** n

		while len(self.data) <= sprite_id :
			self.data.append(0)

		self.data[sprite_id] = flg

	def getSpriteFlag(self, sprite_id: int) -> list[bool]:
		if sprite_id < 0 or sprite_id > 511 :
			raise ValueError(f"Invalid sprite id: {sprite_id}")

		if len(self.data) <= sprite_id : return [
			False,
			False,
			False,
			False,
			False,
			False,
			False,
			False
		]

		flgs = []

		f = self.data[sprite_id]

		mult = 7
		while mult >= 0 :
			if f >= 2 ** mult :
				flgs.append(True)
				f -= 2 ** mult
			else :
				flgs.append(False)

			mult -= 1

		return flgs[::-1]

CHUNK_CLASSES = {
	1 	: Tiles,
	2 	: Sprites,
	4 	: Map,
	5 	: Code,
	6 	: Flags,
	9 	: Chunk,
	10 	: Chunk,
	12 	: Palette,
	14 	: Chunk,
	15 	: Chunk,
	17 	: Chunk,
	18 	: Chunk,
	19 	: Chunk,
	3 	: Chunk,
	13 	: Chunk,
	16 	: Chunk
}

class TicFile :
	def __init__(self, path: str) :
		self.path: str = path

		with open(path, "rb") as f :
			file = (x for x in f.read())

		def nextChunk() :
			try :
				cnk_info: int = next(file) # chunk info (bank & type)
			except StopIteration :
				return None

			cnk_bank: int = cnk_info >> 5
			cnk_type_id: int = cnk_info & 0b00011111

			cnk_size_low: int = next(file) # chunk size (little endian order)
			cnk_size_high: int = next(file)

			cnk_size: int = cnk_size_low + (cnk_size_high << 8)

			next(file) # reserved bytes

			cnk_data: list[int] = []

			for i in range(cnk_size) :
				cnk_data.append(next(file))

			cnk_class = CHUNK_CLASSES[cnk_type_id]

			return cnk_class(cnk_type_id, cnk_bank, cnk_data)

		self.chunks: list[Chunk] = []

		while cnk := nextChunk() :
			self.chunks.append(cnk)

	def __str__(self) -> str:
		return f"{repr(self.path)} {len(self.chunks)} chunk(s)"

	def getChunksOfType(self, cnk_type: int | str) -> list[Chunk] :
		give: list[Chunk] = []

		for i in self.chunks :
			if type(cnk_type) is int :
				if i.type_int == cnk_type :
					give.append(i)
			else :
				if i.type_str == cnk_type :
					give.append(i)

		return give

	def hasChunkOfType(self, cnk_type: int | str) -> bool :
		return len(self.getChunksOfType(cnk_type)) > 0

	def save(self, path: Optional[str] = None) :
		if path == None : path = self.path

		with open(path, "wb") as f :
			for c in self.chunks :
				for i in c.saveBytes() :
					f.write(i)

	def createChunk(self, cnk_type: int, cnk_bank: int, cnk_data: list[int]) :
		cnk_class = CHUNK_CLASSES[cnk_type]

		cnk = cnk_class(cnk_type, cnk_bank, cnk_data)

		self.chunks.append(cnk)
