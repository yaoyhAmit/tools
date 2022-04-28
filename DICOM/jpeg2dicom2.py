import os
import datetime
import numpy as np
from PIL import Image
import pydicom
from pydicom.dataset import Dataset, FileDataset

def save_to_dcm():
	img = np.asarray(Image.open('./data/TestImage.jpg'),dtype=np.uint8)
	print("Setting file meta information...")
	suffix = '.dcm'
	filename = 'test' + suffix

	# Populate required values for file meta information
	file_meta = Dataset()
	file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
	file_meta.MediaStorageSOPInstanceUID = "1.2.3"
	file_meta.ImplementationClassUID = "1.2.3.4"

	print("Setting dataset values...")
	# Create the FileDataset instance (initially no data elements, but file_meta
	# supplied)
	ds = FileDataset(filename, {},
					  file_meta=file_meta, preamble=b"\0" * 128)
				
   	# # Write as a different transfer syntax XXX shouldn't need this but pydicom
	# # 0.9.5 bug not recognizing transfer syntax
	ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
	# Set creation date/time
	dt = datetime.datetime.now()
	ds.ContentDate = dt.strftime('%Y%m%d')
	timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
	ds.ContentTime = timeStr

	ds.Modality = "US"
	ds.SeriesInstanceUID = pydicom.uid.generate_uid()
	ds.StudyInstanceUID = pydicom.uid.generate_uid()
	ds.FrameOfReferenceUID = pydicom.uid.generate_uid()

	ds.BitsStored = 8
	ds.BitsAllocated = 8
	ds.SamplesPerPixel = 3
	ds.HighBit = 7
	ds.PlanarConfiguration = 0

	ds.InstanceNumber = 1
	ds.ImagePositionPatient = r"0\0\1"
	ds.ImageOrientationPatient = r"1\0\0\0\-1\0"

	ds.ImagesInAcquisition = "1"
	ds.Rows,ds.Columns = img.shape[:2]
	ds.PixelSpacing = [1, 1]
	ds.PixelRepresentation = 0
	ds.PixelData= img.tostring()
	# import pdb;pdb.set_trace()
	ds.PhotometricInterpretation = 'RGB'
	
	print("Writing file",filename)
	ds.save_as(filename)
	print("File saved.")

if __name__ == '__main__':
	save_to_dcm()
