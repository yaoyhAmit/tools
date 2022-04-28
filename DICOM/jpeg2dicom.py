from pydicom.uid import ImplicitVRLittleEndian
from pydicom.dataset import Dataset, FileDataset
import cv2
import datetime
import pydicom
import numpy as np

# Create the metadata for the dataset
file_meta = Dataset()
file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
file_meta.MediaStorageSOPInstanceUID = '1.2.3'
file_meta.ImplementationClassUID = '1.2.3.4'

# Create the dataset
# ds = FileDataset("Test4.dcm", {}, file_meta=file_meta, preamble=b'\x00'*128)
ds = FileDataset("Test4.dcm", {}, file_meta=file_meta, preamble=b"\0"*128)

# Add some of the data elements
ds.PatientName = "Dicom^Anony"
ds.PatientID = "123456"

# Set the transfer syntax
ds.is_little_endian = True
ds.is_implicit_VR = True

# Set creation date/time
dt = datetime.datetime.now()
ds.ContentDate = dt.strftime('%Y%m%d')
timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
ds.ContentTime = timeStr

# Read in the JPG file
img = cv2.imread("./data/TestImage.jpg")

# Get the numpy array
arr = np.asarray(img,dtype=np.uint8)

ds.Modality = "US"
ds.SerierInstanceUID = pydicom.uid.generate_uid()
ds.StudyInstanceUID = pydicom.uid.generate_uid()
ds.FrameOfReferenceUID = pydicom.uid.generate_uid()

# (8-bit pixels, black and white)
ds.Rows, ds.Columns, dummy = arr.shape
# ds.PhotometricInterpretation = "MONOCHROME1"
# ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "RGB"
ds.SamplesPerPixel = 3
ds.BitsStored = 8
ds.BitsAllocated = 8
ds.HighBit = 7
# ds.PixelRepresentation = 0
ds.PlanarConfiguration = 0

ds.InstanceNumber = "1"
ds.ImagePositionPatient = r"0\0\1"
ds.ImageOrientationPatient = r"1\0\0\0\-1\0"

ds.ImagesInAcquistion = "1"
ds.PixeSpacing = [1,1]
ds.PixelRepresentation = 0

# Reassign back to the image data
# ds.PixelData = arr.tobytes()
ds.PixelData = arr.tostring()

# Save DICOM
ds.save_as("Test4.dcm")

# reopen the data just for checking
# for filename in (filename_little_endian, filename_big_endian):
# print('Load file {} ...'.format(filename))
ds = pydicom.dcmread("Test4.dcm")
print(ds)

# # remove the created file
# print('Remove file {} ...'.format(filename))
# os.remove(filename)