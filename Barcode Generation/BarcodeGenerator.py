'''Script to generate file for printing lab barcodes'''
'''  This script assumes 23 pages of 80 labels '''

import pandas as pd
import os

def generateBarcodeFile():
    #os.chmod('/Users/kmcginley/VL43/Laboratory Operations - Documents/Barcode Labels/SMP_Barcodes.csv', 444)
    df = pd.read_csv('/Users/kmcginley/VL43/Laboratory Operations - Documents/Barcode Labels/SMP_Barcodes.csv')
    lastBarcode = df['Barcode'].iloc[0]
    #lastBarcode = 'SMP002999'
    barcodeList = []

    x = 1
    for i in range(1,461):
        for v in range(1,5):
            bc = 'SMP00'+ str(int(lastBarcode[-4::]) + x)
            barcodeList.append(bc)
        x += 1

    contents = pd.DataFrame({'Barcode':barcodeList})
    '''reverse the order of rows for label rolls'''
    #contents = contents.iloc[::-1]
    
    outFile = contents.to_csv('/Users/kmcginley/VL43/Laboratory Operations - Documents/Barcode Labels/SMP_Barcodes.csv', index=False)
    outFile2 = contents.to_csv('/Users/kmcginley/Documents/Programming/Personal/Python/Barcode Generation/SMP_Barcodes.csv', index=False)
    
    return outFile, outFile2

# def change_perms():
#     os.chmod('/Users/kmcginley/VL43/Laboratory Operations - Documents/Barcode Labels/SMP_Barcodes.csv', 0o444)


if __name__ == '__main__':
    
    generateBarcodeFile()
    
   # change_perms()