#  Copyright 2019 Alorium Technology, LLC.
#
#  This utility is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as
#  published by the Free Software Foundation, either version 3 of
#  the License, or (at your option) any later version.
#
#  This utility is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this file.  If not, see
#  <http://www.gnu.org/licenses/>.
"""
`hinj_pmod_converter`
================================================================================

Utility for converting libraries that use standard SPI interface to one of the 
PMOD SPI interfaces on Alorium's Hinj board.

* Author(s): Bryan Craker

"""

# This script requires Python 3, so check for it and error out if not
import sys
if sys.version_info[0] < 3:
    raise Exception("\n\nMust be using Python 3\n\n")

# Other imports - only do after Python 3 check to avoid errors
import tkinter
from tkinter.filedialog import askdirectory
import os
from shutil import copyfile


def replaceHeaderReferences(filename):

  print(filename)

  file = open(filename, 'r')

  try:
    lines = file.readlines()
  except UnicodeDecodeError:
    file.close()
    file = open(filename, 'r', encoding='latin1')
    lines = file.readlines()

  file.close()

  for idx in range(len(lines)):
    if (lines[idx].find('SPI.h') != -1):
      lines[idx] = lines[idx]
    elif (lines[idx].find('SPI.') != -1):
      lines[idx] = lines[idx].replace('SPI.', 'XLR8PmodSPI.', 1)
      
  for idx in range(len(lines)):
    if (lines[idx].find('Wire.h') != -1):
      lines[idx] = lines[idx]
    elif (lines[idx].find('Wire.') != -1):
      lines[idx] = lines[idx].replace('Wire.', 'XLR8PmodWire.', 1)
      
  for idx in range(len(lines)):
    # Serial is included by default in Arduino so we don't need to search for the include
    if (lines[idx].find('Serial.') != -1):
      lines[idx] = lines[idx].replace('Serial.', 'XLR8PmodSerial.', 1)
      
  with open(filename,'w') as f:
    for line in lines:
      f.write("%s" % line)


def replaceSourceReferences(filename):

  print(filename)

  file = open(filename, 'r')

  try:
    lines = file.readlines()
  except UnicodeDecodeError:
    file.close()
    file = open(filename, 'r', encoding='latin1')
    lines = file.readlines()

  file.close()
  serialFound = -1
  i2cFound = -1
  spiFound = -1

  for idx in range(len(lines)):
    if (lines[idx].find('SPI.h') != -1):
      print('SPI library include found on line ' + str(idx))
      lines[idx] = lines[idx].replace('SPI.h', 'XLR8SPI.h', 1)
      spiFound = idx
    elif (lines[idx].find('SPI.') != -1):
      lines[idx] = lines[idx].replace('SPI.', 'XLR8PmodSPI.', 1)
    elif (lines[idx].find('SPDR = ') != -1):
      lines[idx] = lines[idx].replace('SPDR = ', 'XLR8PmodSPI.writeSPDR(', 1)
      lines[idx] = lines[idx].replace(';', ');', 1)
    elif (lines[idx].find('SPDR') != -1):
      lines[idx] = lines[idx].replace('SPDR', 'XLR8PmodSPI.readSPDR()', 1)
    elif (lines[idx].find('SPSR = ') != -1):
      lines[idx] = lines[idx].replace('SPSR = ', 'XLR8PmodSPI.writeSPSR(', 1)
      lines[idx] = lines[idx].replace(';', ');', 1)
    elif (lines[idx].find('SPSR') != -1):
      lines[idx] = lines[idx].replace('SPSR', 'XLR8PmodSPI.readSPSR()', 1)
    elif (lines[idx].find('SPCR = ') != -1):
      lines[idx] = lines[idx].replace('SPCR = ', 'XLR8PmodSPI.writeSPCR(', 1)
      lines[idx] = lines[idx].replace(';', ');', 1)
    elif (lines[idx].find('SPCR') != -1):
      lines[idx] = lines[idx].replace('SPCR', 'XLR8PmodSPI.readSPCR()', 1)

  for idx in range(len(lines)):
    if (lines[idx].find('Wire.h') != -1):
      print('I2C library include found on line ' + str(idx))
      lines[idx] = lines[idx].replace('Wire.h', 'XLR8Wire.h', 1)
      i2cFound = idx
    elif (lines[idx].find('Wire.') != -1):
      lines[idx] = lines[idx].replace('Wire.', 'XLR8PmodWire.', 1)

  for idx in range(len(lines)):
    if (lines[idx].find('Serial.') != -1):
      if (serialFound == -1):
        print('Serial library include found on line ' + str(idx))
        serialFound = idx
      lines[idx] = lines[idx].replace('Serial.', 'XLR8PmodSerial.', 1)

  if (spiFound >= 0):
    lines.insert(spiFound+1, '#include <XLR8HinjAddrPack.h>\n')
    lines.insert(spiFound+2, 'XLR8SPIClass XLR8PmodSPI(0xAC, 0xAD, 0xAE);\n')

  if (i2cFound >= 0):
    lines.insert(i2cFound+1, '#include <XLR8HinjAddrPack.h>\n')
    lines.insert(i2cFound+2, 'XLR8TwoWire XLR8PmodWire(0xE5, 0xE0, 0xE1, 0xE2, 0xE3, 0xE4);\n')

  if (serialFound >= 0):
    lines.insert(serialFound+1, '#include <XLR8HinjAddrPack.h>\n')
    lines.insert(serialFound+2, 'XLR8Serial XLR8PmodSerial(0xEB, 0xEA, 0xE7, 0xE8, 0xE9, 0xE6);\n')

  with open(filename,'w') as f:
    for line in lines:
      f.write("%s" % line)


tkinter.Tk().withdraw()
directory = askdirectory(initialdir=os.path.expanduser('~/Documents/Arduino/libraries/'))
print(directory)

originalName = os.path.basename(directory)
outputDirectory = "HinjPMOD_"+originalName

if not os.path.exists(outputDirectory):
  print("Creating: " + outputDirectory)
  os.makedirs(outputDirectory)
  os.makedirs(outputDirectory+'/src')
else:
  print(outputDirectory+' already exists')

lpFile = open(outputDirectory+'/library.properties', 'w')
lpFile.write('name='+outputDirectory+"\n")
lpFile.write('version=0.0.1'+"\n")
lpFile.write('author=Alorium Technology PMOD Conversion Script'+"\n")
lpFile.write('maintainer=User'+"\n")
lpFile.write('sentence=Hinj PMOD library'+"\n")
lpFile.write('paragraph=Library generated by converting '+originalName+' for use with Hinj PMOD'+"\n")
lpFile.write('architectures=avr'+"\n")
lpFile.write('category=Uncategorized'+"\n")

fileList = []

for r, d, f in os.walk(directory):
  for file in f:
    if (file.endswith(".h")):
      fileList.append(file)
      print("Header File: " + os.path.join(r, file))
      copyfile(os.path.join(r, file), outputDirectory+'/src/HinjPMOD_'+file)
      replaceHeaderReferences(outputDirectory+'/src/HinjPMOD_'+file)
    elif (file.endswith(".cpp")):
      fileList.append(file)
      print("Source File: " + os.path.join(r, file))
      copyfile(os.path.join(r, file), outputDirectory+'/src/HinjPMOD_'+file)
      replaceSourceReferences(outputDirectory+'/src/HinjPMOD_'+file)
  #for dir in d:
    #print("Dir: " + os.path.join(r, dir))

print(fileList)
