import argparse
from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind
import pandas as pd
from tabulate import tabulate
import re
import datetime
import matplotlib.pyplot as plt
import numpy as np

ds = Dataset()


parser = argparse.ArgumentParser()
parser.add_argument("host", help="Hostaddress of the pacs server",
                    type=str)
parser.add_argument("port", help="Port of the pacs server",
                    type=int)
# parser.add_argument("aet", help="AET of the pacs server",
#                     type=str)
args = parser.parse_args()
print("Querying :",args.host)

#debug_logger()

ae = AE()
ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

# Create our Identifier (query) dataset
ds.QueryRetrieveLevel = 'SERIES'
#ds.StudyDate = '202211*'
ds.StudyDate = '2021*'
ds.StudyDescription = ''
ds.StudyTime = ''
#ds.PatientName = '*'
ds.InstitutionName = ''


#print(tabulate(df))

#quit();

queryresult=[]
# Associate with the peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate(args.host, args.port)
if assoc.is_established:
    # Send the C-FIND request
    responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
    for (status, identifier) in responses:
        if status:
#            print('C-FIND query status: 0x{0:04X}'.format(status.Status))
            if isinstance(identifier,type(Dataset())):
                queryresult.append(identifier)
        else:
            print('Connection timed out, was aborted or received invalid response')
    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')

#print("Total count of Series on PACS: ",len(queryresult))


timestamps = []
workingdays = []
for result in queryresult:
    datestring=result[0x00080020].value + result[0x00080030].value
    datestring=re.sub(r'\..*' ,"",datestring)
#    print(datestring)
    timestamp=datetime.datetime.strptime(datestring, "%Y%m%d%H%M%S")
    timestamps.append(timestamp)

    if int(timestamp.strftime('%w'))>4:
        workingdays.append(False)
    else:
        workingdays.append(True)
    
df = pd.DataFrame(data={"Timestamp": timestamps, "Workingday":workingdays})

workingdays=df[df['Workingday']==True]
nonworkingdays=df[df['Workingday']==False]

#df["Timestamp"]=df["Timestamp"].astype("datetime64")
#df.groupby(df["Timestamp"].dt.hour).count().plot(kind="bar")


workingdays["Timestamp"]=df["Timestamp"].astype("datetime64")
workingdays.groupby(workingdays["Timestamp"].dt.hour).count().plot(title="Working Days",kind="bar")

nonworkingdays["Timestamp"]=df["Timestamp"].astype("datetime64")
nonworkingdays.groupby(nonworkingdays["Timestamp"].dt.hour).count().plot(title="Non Working Days",kind="bar")

plt.show()
