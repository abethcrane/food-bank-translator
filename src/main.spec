# -*- mode: python -*-

NAME = 'FoodBankTranslator'

import os
import kivy
from os.path import join, exists
from kivy.utils import platform

if platform == 'win':
    from kivy.deps import sdl2, glew, gstreamer
else:
    glew = sdl2 = None

block_cipher = None

a = Analysis(['main.py', 'main.spec'],
             pathex=['C:\\Users\\becrane\\Dropbox\\projects\\PikeMarketFoodBankTranslator\\src'],
             binaries=[],
             datas=[],
             hiddenimports=['win32timezone'],
			 hookspath=[],
			 runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
			 
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe, Tree('C:\\Users\\becrane\\Dropbox\\projects\\PikeMarketFoodBankTranslator\\src'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *([Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + gstreamer.dep_bins)] if sdl2 else []),
               strip=False,
               upx=True,
               name=NAME)
