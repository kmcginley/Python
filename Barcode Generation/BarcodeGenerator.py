'''Script to generate file for printing lab barcodes'''

import pandas as pd
import os

def generateBarcodeFile():
    #os.chmod('/Users/kmcginley/VL43/Laboratory Operations - Documents/Barcode Labels/SMP_Barcodes.csv', 444)
    df = pd.read_csv('/Users/kmcginley/VL43/Laboratory Operations - Documents/Barcode Labels/SMP_Barcodes.csv')
    lastBarcode = df['Barcode'].iloc[0]
    
    barcodeList = []

    x = 1
    for i in range(1,121):
        for v in range(1,6):
            bc = 'SMP00'+ str(int(lastBarcode[-4::]) + x)
            barcodeList.append(bc)
        x += 1

    contents = pd.DataFrame({'Barcode':barcodeList})
    contents = contents.iloc[::-1]
    
    outFile = contents.to_csv('/Users/kmcginley/VL43/Laboratory Operations - Documents/Barcode Labels/SMP_Barcodes.csv', index=False)
    outFile2 = contents.to_csv('/Users/kmcginley/Documents/Programming/Personal/Python/Barcode Generation/SMP_Barcodes.csv', index=False)
    
    return outFile, outFile2

# def change_perms():
#     os.chmod('/Users/kmcginley/VL43/Laboratory Operations - Documents/Barcode Labels/SMP_Barcodes.csv', 0o444)


if __name__ == '__main__':
    
    generateBarcodeFile()
    
   # change_perms()