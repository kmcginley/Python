# Script to output the Zinsser file from Benchling files
'''
Take file from Benchling. Determine how many destination barcodes there are to be sprayed.
Multiply that by 12 wells and add that many rows to the zinsser file.
For every 12 rows, increment DestRack by 1.
Add the plate barcodes to the zinsser file DestBC column.
Take agent number from barcode and apply that to the sourcepos column of the zinsser file
If there are > 24 agents, make sure the source rack increases by 1 and the source pos resets to 1
'''



import pandas as pd


importFile = pd.read_csv('/Users/kmcginley/Downloads/Experiment QR (1).csv')



mydf = pd.DataFrame(importFile)

mydf['SourcePos'] = [x.split('_')[1] for x in mydf.loc[:, 'QR Code']]
agentRef = mydf[['Agent', 'SourcePos']].drop_duplicates()


qrCodes = mydf.loc[:, 'QR Code']
barcodes = []
wells = []
vials = []
sourceRack = []
destRack = []

x = 1
k = 0
for code in qrCodes:
    if barcodes:
        if code != barcodes[-1]:
            x += 1
    barcodes.extend([code]*12)
    if code.split('_')[2]=='1':
        if int(code.split('_')[1]) % 24 == 1:
            k += 1
    # add 12 dest wells
    wells.extend(i for i in range(1,13))
    if k > 1:
        vials.extend(int(code.split('_')[1]) - (24*(k-1)) for i in range(1, 13))
    else:
        vials.extend(code.split('_')[1] for i in range(1, 13))
    sourceRack.extend(['Source_' + str(k)]*12)
    destRack.extend(['Dest_'+ str(x)]*12)


outputDf = pd.DataFrame(data = {'SourceRack': sourceRack, 'SourcePos': vials, 'DestRack': destRack, 'DestBC': barcodes, 'DestPos': wells})
outputDf['SourceTyp'] = 'Rack_8ml'
outputDf['SourceVol[ul'] = 5000
outputDf['DestTyp'] = 'Plate_12'
outputDf['SprayVol'] = 84
outputDf = outputDf[['SourceRack','SourceTyp','SourcePos','SourceVol[ul', 'DestRack', 'DestBC', 'DestTyp', 'DestPos', 'SprayVol']]

outputDf = pd.merge(outputDf, agentRef, how='left', on='SourcePos')

outputDf.to_csv('/Users/kmcginley/Downloads/Zinsser_Output.csv', index=False)


