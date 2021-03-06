'''Script to generate file for printing lab barcodes
This will make an upload sheet for the Dymo printer 
that will print 121 labels in replicates of 5. The IDs are
printed in reverse order, so that the lowest number is the first one
after wrapping around the spool'''

import pandas as pd
import os

def generateBarcodeFile():
    localPath = '/Users/kmcginley/Documents/Programming/Personal/Python/Barcode Generation/SMP_Barcodes.csv'
    remotePath = '/Users/kmcginley/VL43/Laboratory Operations - Documents/Barcode Labels/SMP_Barcodes.csv'
    
    ''' open last generated barcode file, and get the last used ID'''
    df = pd.read_csv(remotePath)
    lastBarcode = df['Barcode'].iloc[0]
    #lastBarcode = 'SMP003134'
    barcodeList = []

    x = 1
    for i in range(1,121):
        for v in range(1,6):
            bc = 'SMP00'+ str(int(lastBarcode[-4::]) + x)
            barcodeList.append(bc)
        x += 1
    #barcodeList = ['SMP00'+ str(int(lastBarcode[-4::]) + x) for x in range(1,121)]

    contents = pd.DataFrame({'Barcode':barcodeList})

    '''reverse the order of rows for label rolls'''
    contents = contents.iloc[::-1]
    

    outFile = contents.to_csv(remotePath, index=False)
    outFile2 = contents.to_csv(localPath, index=False)
    
    return outFile, outFile2



if __name__ == '__main__':
    
    generateBarcodeFile()
