from googletrans import Translator

translator = Translator()

# no enum type ):
LANGID_ENG, LANGID_FR, LANGID_GER = 0, 1, 2

def translate_txt(txt, srclang, destlang):
    return translator.translate(txt, src=srclang, dest=destlang)