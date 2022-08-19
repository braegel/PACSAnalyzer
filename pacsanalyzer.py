import argparse
from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind

parser = argparse.ArgumentParser()
parser.add_argument("host", help="Hostaddress of the pacs server",
                    type=str)
parser.add_argument("port", help="Port of the pacs server",
                    type=int)
parser.add_argument("aet", help="AET of the pacs server",
                    type=str)
args = parser.parse_args()
#print("Querying :",args.host)

#debug_logger()

ae = AE()
ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

# Create our Identifier (query) dataset
ds = Dataset()
ds.QueryRetrieveLevel = 'SERIES'
ds.StudyDate = '20220819'
ds.StudyDescription = '*'
ds.StudyTime = ''
#ds.PatientName = '*'
ds.InstitutionName = '*'

identifiers=[]
# Associate with the peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate(args.host, args.port)
if assoc.is_established:
    # Send the C-FIND request
    responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
    for (status, identifier) in responses:
        if status:
#            print('C-FIND query status: 0x{0:04X}'.format(status.Status))
            identifiers.append(identifier)
        else:
            print('Connection timed out, was aborted or received invalid response')
    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')

for(identifier) in identifiers:
    print(identifier)
