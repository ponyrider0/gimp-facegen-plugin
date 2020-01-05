GIMP-FaceGen-Tools, v1.4
2020-Jan-5

Description:
Gimp-Python based plugin for rendering, baking and reverse-calculating FaceGen Textures, Age maps, Detail maps.

Requirements:
GIMP 2.10
GIMP DDS plugin

Installation:
Copy the entire facegen-tools folder into the gimp plugins folder.  By default, this is "C:\Program Files\GIMP 2\lib\gimp\2.0\plug-ins" for GIMP 64bit.  Restart GIMP.

Usage:
Rendering/Baking a FaceGen Texture:
1. Start GIMP, and open a base face texture: from the main menu, select "File->Open..." and then select a base face texture such as "Oblivion\Textures\Data\characters\nuska\darkelf\headdarkelf_f.dds", from the Oblivion Character Overhaul v2 mod.  When asked, uncheck "Load mipmaps" and click OK.
2. Now load an age map: from the main menu, select "File->Open as Layers..." then select an age map such as "Oblivion\Textures\Data\characters\nuska\woodelf\headwoodelff20.dds".  When asked, uncheck "Load mipmaps" and click OK.
3. Make sure the agemap is scaled to the same size as the base face texture.  If it appears smaller, then select "Layer->Scale Layer..." and change the width and height to the size of the base face texture.
4. From the main menu, select "Filters->FaceGen Tools->Render FaceGen Texture...".
5. The plugin dialog pops up: select the proper layer corresponding for the Age Map and Base Texture.  Click OK.
6. Once the progress bar completes, you will have a face texture with all agemaps baked in.  You can now delete the other layers and export as a new DDS file.

Reverse-Calculating an AgeMap from a hand-painted/custom FaceGen Texture:
1. Start GIMP, open base texture like step 1 above.
2. Right-Click layer for base texture in the Layers window.  Select "Duplicate Layer".
3. Edit Duplicated layer by painting, image editing, importing images, etc.
4. Merge any created layers into the Duplicated layer (custom FaceGen Texture).
5. Select "Filters->FaceGen Tools->Calculate Age Map...".
6. Select proper layer corresponding to custom FaceGen Texture and Base Texture. Click OK.
7. Once the progress bar completes, copy/paste newly created age map to new file and export as new DDS file.

Change Log:
v1.4:
Added option for automatic save to PNG when splitting norm and spec maps.

v1.3:
Added automatic save and/or export of normal map operations to XCF and DDS files.

v1.2:
Added Oblivion combined RGBA normal map functions for splitting/combining component RGB normal maps + Alpha specular maps.

v1.1:
Modified reverse algorithm to decrease artifacts when reading zero values in Base textures.

