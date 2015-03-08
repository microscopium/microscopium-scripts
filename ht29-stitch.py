from microscopium.screens import cellomics
from microscopium import pathutils
import os
from skimage import io
import cellom2tif

# load a directory of cellomics images, convert them to TIFs then stitch them
# together

image_dir = '/home/starcalibre/NIRHTa-001'
tif_out_dir = '/home/starcalibre/NIRHTa-001-tif'
files = pathutils.all_matching_files(image_dir, glob='*.DIB', full=False, case_sensitive=False)

cellom2tif.convert_files(tif_out_dir, image_dir, files)

tif_files = pathutils.all_matching_files(tif_out_dir, glob='*.tif', case_sensitive=False)

cellomics.batch_stitch_stack(file_dict=cellomics.make_key2file(tif_files),
                             output='/home/starcalibre/NIRHTa-001-tif-stitch',
                             stitch_order=[[2, 3, 4], [1, 0, 5]],
                             channel_order=[1, 2, 0],
                             target_bit_depth=8)



