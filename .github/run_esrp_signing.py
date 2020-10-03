import json
import os
import glob
import pprint
import subprocess


esrp_tool = os.path.join("esrp", "Microsoft.EsrpClient.1.2.40", "tools", "EsrpClient.exe")

aad_id = os.environ['AZURE_AAD_ID'].strip()
workspace = os.environ['GITHUB_WORKSPACE'].strip()

source_root_location = os.path.join(workspace, "deb", "Release")
destination_location = os.path.join(workspace)

files = glob.glob(os.path.join(source_root_location, "*.deb"))

print("Found files:")
pprint.pp(files)

if len(files) < 1 or not files[0].endswith(".deb"):
	print("Error: cannot find .deb to sign")
	exit(1)

file_to_sign = os.path.basename(files[0])

auth_json = {
	"Version": "1.0.0",
	"AuthenticationType": "AAD_CERT",
	"TenantId": "72f988bf-86f1-41af-91ab-2d7cd011db47",
	"ClientId": aad_id,
	"AuthCert": {
		"SubjectName": f"CN={aad_id}.microsoft.com",
		"StoreLocation": "LocalMachine",
		"StoreName": "My",
	},
	"RequestSigningCert": {
		"SubjectName": f"CN={aad_id}",
		"StoreLocation": "LocalMachine",
		"StoreName": "My",
	}
}

input_json = {
	"Version": "1.0.0",
	"SignBatches": [
		{
			"SourceLocationType": "UNC",
			"SourceRootDirectory": source_root_location,
			"DestinationLocationType": "UNC",
			"DestinationRootDirectory": destination_location,
			"SignRequestFiles": [
				{
					"CustomerCorrelationId": "01A7F55F-6CDD-4123-B255-77E6F212CDAD",
					"SourceLocation": file_to_sign,
					"DestinationLocation": os.path.join("Signed", file_to_sign),
				}
			],
			"SigningInfo": {
				"Operations": [
					{
						"KeyCode": "CP-450778-Pgp",
						"OperationCode": "LinuxSign",
						"Parameters": {},
						"ToolName": "sign",
						"ToolVersion": "1.0",
					}
				]
			}
		}
	]
}

configs = [
	("auth.json", auth_json),
	("input.json", input_json),
]

for filename, data in configs:
	with open(filename, 'w') as fp:
		json.dump(data, fp)

# Run ESRP Client
esrp_out = "esrp_out.json"
subprocess.run([esrp_tool, "-a", "auth.json", "-i", "input.json", "-o", esrp_out], cwd=workspace)

if os.path.isfile(esrp_out):
	print("ESRP output json:")
	with open(esrp_out, 'r') as fp:
		pprint.pp(json.load(fp))

signed_file = os.path.join(destination_location, "Signed", file_to_sign)
if os.path.isfile(signed_file):
	print(f"SUccess!\nSigned {signed_file}")
