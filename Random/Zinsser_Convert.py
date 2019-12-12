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


importFile = pd.read_csv('/Users/kmcginley/Downloads/EXP19000598 QR codes.csv')

a = importFile[(importFile['Agent']=='water') | (importFile['Agent']=='rifampicin')]
b = importFile[(importFile['Agent']!='water') & (importFile['Agent']!='rifampicin')]
mydf = pd.concat([b,a])

agentRef = mydf[['Agent', 'QR Code']].drop_duplicates()
agentRef = agentRef.rename(columns={'QR Code':'DestBC'})
agentRef['SourcePos'] = agentRef.groupby(['Agent'], sort = False).ngroup()
agentRef['SourcePos'] = agentRef['SourcePos'] + 1


qrCodes = mydf.loc[:, 'QR Code']
barcodes = []
wells = []
vials = []
sourceRack = []
destRack = []

x = 1
k = 1
for code in qrCodes:
    if barcodes:
        if code != barcodes[-1]:
            x += 1
    barcodes.extend([code]*12)
    if code.split('_')[2]=='1':
        # if the treatment number is 26/52 this indicates to use the next vial holder
        if int(code.split('_')[1]) in [27, 52]:
            k += 1
    # add 12 dest wells
    wells.extend(i for i in range(1,13))  
    sourceRack.extend(['Source_' + str(k)]*12)
    destRack.extend(['Dest_'+ str(x)]*12)




outputDf = pd.DataFrame(data = {'SourceRack': sourceRack,'DestRack': destRack, 'DestBC': barcodes, 'DestPos': wells})
outputDf['SourceTyp'] = 'Rack_8ml'
outputDf['SourceVol[ul]'] = 5000
outputDf['DestTyp'] = 'Plate_12'
outputDf['SprayVol'] = 84
outputDf = outputDf[['SourceRack','SourceTyp','SourceVol[ul]', 'DestRack', 'DestBC', 'DestTyp', 'DestPos', 'SprayVol']]

print(agentRef)
outputDf = pd.merge(outputDf, agentRef, how='left', on='DestBC')
sourcepositions = outputDf['SourcePos']
newpos = []
newrack = []
rackcounter = 1
counter = 0

for pos in sourcepositions:
    if pos in [25, 49]:
        if pos >= 25:
            rackcounter = 2
        elif pos >= 49:
            rackcounter = 3
        pos = 1
        counter += 1
        newpos.append(pos) 
        newrack.append('Source_'+str(rackcounter))    
    elif counter > 0:
        newpos.append(pos-24)
        newrack.append('Source_'+str(rackcounter))
        
    else:
        newpos.append(pos)
        newrack.append('Source_'+str(rackcounter))
        
print(rackcounter)
outputDf['SourcePos'] = newpos
outputDf['SourceRack'] = newrack
outputDf = outputDf[['SourceRack','SourceTyp','SourcePos','SourceVol[ul]', 'DestRack', 'DestBC', 'DestTyp', 'DestPos', 'SprayVol', 'Agent']]
print(outputDf)
path = '/Users/kmcginley/Downloads/{}_Zinsser_Input.csv'.format(qrCodes[0].split('_')[0])
outputDf.to_csv(path, index=False)


