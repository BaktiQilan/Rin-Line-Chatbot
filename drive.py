from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
import auth
import re

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
authInst = auth.auth(SCOPES)
creds = authInst.getCredentials()
service = build('drive', 'v3', credentials=creds)

def listFiles():
    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

def createFolder(name):
    file_metadata = {
    'name': name,
    'mimeType': 'application/vnd.google-apps.folder'
    }
    file = service.files().create(body=file_metadata,
                                        fields='id').execute()
    print ('Folder ID: %s' % file.get('id'))

def copyFileDrive(fileId):
    fileOriginMetaData = service.files().get(fileId=fileId).execute()
    copiedFileMetaData = {'title': fileOriginMetaData}
    copiedFile = service.files().copy(
        fileId=fileId,
        body=copiedFileMetaData
    ).execute()
    return copiedFile
  
def copyFileDriveGetLink(fileId):
    fileOriginMetaData = service.files().get(fileId=fileId).execute()
    folderID = "1939R2jzzBJuEpvUkXM74gig9NoJvMepg" #Folder mirror Rin Bot
    copiedFileMetaData = {'title': fileOriginMetaData, 'parents': [folderID]}
    copiedFile = service.files().copy(
        fileId=fileId,
        body=copiedFileMetaData
    ).execute()
    user_permission = {
    'type': 'anyone',
    'role': 'reader'
    }
    fileIdNew = copiedFile['id']
    service.permissions().create(fileId=fileIdNew,body=user_permission,fields='id').execute()
    fileLink = "https://drive.google.com/open?id=" + fileIdNew
    return fileLink

def uploadFile(filename,filepath,mimetype):
    folderId = "1939R2jzzBJuEpvUkXM74gig9NoJvMepg" #Folder mirror Rin Bot
    file_metadata = {'name': filename, 'parents': [folderId]}
    media = MediaIoBaseUpload(filepath, mimetype='image/jpeg',
              chunksize=1024*1024, resumable=True)
    file = service.files().create(body=file_metadata,
                                          media_body=media,
                                          fields='id').execute()
    fileId = file['id']
    user_permission = {'type': 'anyone','role': 'reader'}
    service.permissions().create(fileId=fileId,body=user_permission,fields='id').execute()
    fileLink = "https://drive.google.com/open?id=" + fileId
    return fileLink
  
def extract_files_id(links):
    # copy of google drive file from google drive link :
    links = re.findall(r"\b(?:https?:\/\/)?(?:drive\.google\.com[-_&?=a-zA-Z\/\d]+)", links)  # extract google drive links
    try:
        fileIDs = [re.search(r"(?<=/d/|id=|rs/).+?(?=/|$)", link)[0] for link in links]  # extract the fileIDs
        for fileID in fileIDs:
            if service.files().get(fileId=fileID).execute()['mimeType'] == "application/vnd.google-apps.folder":
                fileIDs.extend(extract_file_ids_from_folder(fileID))
                fileIDs.remove(fileID)
        return fileIDs
    except Exception as error:
        textError = "error : " + str(error) + "Link is probably invalid"
        return textError

def extract_file_ids_from_folder(folderID):
    files = service.ListFile({'q': "'" + folderID + "' in parents"}).GetList()
    fileIDs = []
    for file in files :
        fileIDs.append(file['id'])
    return fileIDs

def getSpaceInfo():
  space = service.about().get().execute()
  return space['quotaBytesUsed']