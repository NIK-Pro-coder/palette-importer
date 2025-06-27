
import sys
import os
import requests

from bs4 import BeautifulSoup, Tag

from reader import Palette, TicFile

def loadPalette(url: str) :
	r = requests.get(url)

	if not r.ok :
		print(f"Could not get palette, reason: {r.reason}")
		exit(1)

	soup = BeautifulSoup(r.text, "html.parser")

	pal_name = soup.find(
		"a",
		attrs = {
			"class": "palette-name"
		}
	)

	if not type(pal_name) is Tag :
		print("Could not get palette name")
		exit(1)

	print(f"Loading palette: {repr(pal_name.text)}")

	palette = soup.find(
		"div",
		attrs = {
			"class": "palette"
		}
	)

	if not type(palette) is Tag :
		print("Could not find palette colors")
		exit(1)

	colors: list[tuple[int, int, int]] = []

	for i in palette.find_all(
		"div",
		attrs = {
			"class": "color"
		}
	) :
		if not type(i) is Tag :
			print("Could not get color")
			exit(1)

		string: str = i.text.strip()

		r,g,b = int(string[1:3], 16), int(string[3:5], 16), int(string[5:7], 16)

		print(f"Loaded color: \033[38;2;{r};{g};{b}m{string}\033[0m")

		colors.append((r, g, b))

	print("Palette:")

	for r,g,b in colors :
		print(f"\033[38;2;{r};{g};{b}m■\033[0m", end = " ")
	print()

	return colors

def importPalette(url: str, path: str) :
	abs_path = os.path.abspath(path)

	palette = loadPalette(url)

	if len(palette) != 16 :
		print("Palette does not contain 16 colors")
		exit()

	tic = TicFile(abs_path)

	pal_chunks = tic.getChunksOfType(12)

	if len(pal_chunks) > 0 :
		palette_cnk = pal_chunks[0]
	else :
		tic.createChunk(
			12,
			0,
			[0 for _ in range(3 * 16)]
		)
		palette_cnk = tic.getChunksOfType(12)[0]

	for n,(r,g,b) in enumerate(palette) :
		palette_cnk.setPaletteColor(n,r,g,b)

	tic.save()

	print("Palette imported successfully")

if __name__ == "__main__" :
	if "--help" in sys.argv or len(sys.argv) != 3 :
		print("palette-importer [PALETTE_URL] [FILE]")
		print("")
		print("Options:")
		print(" [PALETTE_URL] A url to a Lospec palette (16 cols exactly)")
		print(" [FILE]        File path to the .tic file to import to")
		exit()

	importPalette(
		sys.argv[1],
		sys.argv[2]
	)
