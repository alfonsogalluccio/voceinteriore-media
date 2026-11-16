import sys; sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from brand import *
out = sys.argv[1]
V = "«Non temere, perché io sono con te; non smarrirti, perché io sono il tuo Dio. Ti rendo forte e anche ti vengo in aiuto.»"
verse_card(1080, 1350, "Parola per oggi", V, "Isaia 41,10", seed=3).convert("RGB").save(f"{out}/post.jpg", quality=93)
# Storia: preghiera breve, complementare al post
img = background(1080, 1920, seed=7, glow_y=0.95).convert("RGBA"); frame(img, 50)
spaced(img, "UNA PREGHIERA PER TE", SANS, 30, 540, 360, track=8); ornament(img, 540, 430)
text_block(img, "Signore,\nquando le forze mi mancano,\nprendimi per mano.\nInsegnami a fidarmi di Te\nanche quando\nnon vedo la strada.\nAmen.", SERIF_I, 76, 540, 900, 880)
spaced(img, "CONDIVIDILA CON CHI NE HA BISOGNO", SANS, 24, 540, 1500, fill=CREAM, track=4)
brand_footer(img, 1920 - 260)
img.convert("RGB").save(f"{out}/story.jpg", quality=93)
