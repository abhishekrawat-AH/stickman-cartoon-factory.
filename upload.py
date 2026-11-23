import os, json, base64, pathlib, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def upload(kind):
    token=os.environ.get("YT_TOKEN_JSON_B64")
    if not token:
        print("YT_TOKEN_JSON_B64 not set; leaving rendered video for manual upload.")
        return
    info=json.loads(base64.b64decode(token).decode())
    creds=Credentials.from_authorized_user_info(info,scopes=["https://www.googleapis.com/auth/youtube.upload"])
    if creds.expired and creds.refresh_token: creds.refresh(Request())
    youtube=build("youtube","v3",credentials=creds)
    meta=json.load(open(f"output/{kind}_metadata.json"))
    body={"snippet":{"title":meta["title"][:100],"description":meta["description"],"tags":meta["tags"],"categoryId":"23"},"status":{"privacyStatus":"private","selfDeclaredMadeForKids":False}}
    media=MediaFileUpload(f"output/{kind}.mp4",mimetype="video/mp4",chunksize=-1,resumable=True)
    req=youtube.videos().insert(part="snippet,status",body=body,media_body=media)
    response=None
    while response is None:
        status,response=req.next_chunk()
        if status: print(f"{kind}: upload {int(status.progress()*100)}%")
    vid=response["id"]
    print("Uploaded",kind,"https://youtu.be/"+vid)
    try:
        youtube.thumbnails().set(videoId=vid,media_body=MediaFileUpload(f"output/{kind}_thumbnail.jpg",mimetype="image/jpeg")).execute()
        print("Thumbnail set for",vid)
    except Exception as e: print("Thumbnail upload skipped:",e)

if __name__=="__main__":
    for k in sys.argv[1:] or ["short","long"]: upload(k)
