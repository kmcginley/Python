import pandas as pd

myfile = '/Users/kmcginley/Downloads/Invaio Pipette Registry.xlsx'
xls = pd.ExcelFile(myfile)
mylist = [i for i in range(0,18)]
print(mylist)
mylist.remove(12)
print(mylist)
mylist.remove(13)
mylist.remove(14)
df = pd.read_excel(xls, mylist, skiprows = 0)
for d in df:
    df[d].columns = df[d].iloc[0]
    df[d] = df[d].iloc[1:32, 1:]
    df[d].dropna(how = 'all', inplace=True)
    print(df[d])
    print(df[d].columns)
mydf = pd.concat([df[d] for d in mylist],join='inner')
print(mydf)
mydf.to_excel('test.xlsx')