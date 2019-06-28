# -*- mode: python -*-

block_cipher = None


a = Analysis(['ProductionPlanner.py'],
             pathex=['/Users/ivanbudnikov/Documents/ProductionPlanner'],
             binaries=[],
             datas=[("Items","Items"), ("Icons","Icons"), ("Processes","Processes"), ("Schemas","Schemas")],
             hiddenimports=[],
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
          name='ProductionPlanner',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ProductionPlanner')
app = BUNDLE(coll,
             name='ProductionPlanner.app',
             icon=None,
             bundle_identifier=None,
	     info_plist={
		'NSPrincipleClass': 'NSApplication',
		'NSAppleScriptEnabled': False,
		'NSHighResolutionCapable': 'True'
	     })
