# Stickman Cartoon Factory (Android setup, free starter)

This starter makes two original, simple animated stickman videos (Short + long) with two characters, English male/female eSpeak voices, a thumbnail and metadata. GitHub Actions renders them in the cloud. It is a starter/demo, not a guaranteed viral-content system.

## What it does / limitations
- Research: optional YouTube Data API search for recent popular topic titles. It uses titles only as inspiration and never copies scripts. If no API key or request fails, it selects a topic from a built-in list.
- Stories: rule-based original dialogue templates. No paid LLM or unlimited AI.
- Animation: generated frame-by-frame with Pillow; deliberately simple stick figures.
- Voices: eSpeak NG `en-us+m3` and `en-us+f3` (synthetic/robotic English voices).
- Editing: FFmpeg; exports `short.mp4` and `long.mp4` in 9:16.
- Upload: optional YouTube OAuth. Default is OFF and private. Review output before public release.
- Free-tier limits, API quota, workflow delays, and Google verification/OAuth restrictions can change.

## Android-only setup
Use Chrome and turn on **Desktop site** on GitHub pages; the mobile editor is awkward. Create a public GitHub repository named `stickman-cartoon-factory`, then upload these files/folders preserving their paths. Do not put credentials in code.

### 1. Optional topic research key
In Google Cloud Console, create a project, enable **YouTube Data API v3**, create an API key, then add it in GitHub:
`Repository → Settings → Secrets and variables → Actions → New repository secret`
Name: `YT_API_KEY`.

If omitted, the workflow uses built-in topics. Search API results are a rough trend signal, not proof a topic will go viral.

### 2. First render (no YouTube credentials needed)
Open `Actions → Daily Stickman Factory → Run workflow`. Wait for completion. Open the run and download the `stickman-videos-...` artifact. It contains both MP4s, thumbnails, scripts and metadata. The scheduled run is 09:00 India time; GitHub may delay scheduled workflows.

### 3. Optional automatic YouTube upload
Uploads are OFF by default. First create OAuth credentials in Google Cloud for YouTube Data API v3 using an OAuth client suitable for a desktop/native app. A practical way to obtain a refresh token is Google's OAuth 2.0 Playground:
1. Open https://developers.google.com/oauthplayground/
2. Open settings (gear), enable **Use your own OAuth credentials**, enter your OAuth client ID and secret.
3. In Step 1 enter/select scope `https://www.googleapis.com/auth/youtube.upload`, authorize with the Google account that owns the channel.
4. In Step 2 exchange the authorization code.
5. In Step 3, use the refresh token response. Create a JSON object containing `client_id`, `client_secret`, `refresh_token`, and `token_uri` set to `https://oauth2.googleapis.com/token`. Example:
   `{"client_id":"...","client_secret":"...","refresh_token":"...","token_uri":"https://oauth2.googleapis.com/token"}`
6. Base64-encode that one-line JSON using a trusted local/offline encoder if available. Never paste secrets into chats or public sites. Add the Base64 output as GitHub Actions secret `YT_TOKEN_JSON_B64`.
7. In `Repository → Settings → Secrets and variables → Actions → Variables`, add variable `AUTO_UPLOAD` with value `true`.
8. The workflow checks the repository variable `AUTO_UPLOAD`; set it to `true`. The upload step will then upload both videos as **private**.
9. Review the first uploads in YouTube Studio. Do not switch to public until you have checked rights, quality, captions and metadata.

OAuth Playground may require adding its redirect URI to the OAuth client. Google may require test-user configuration or app verification depending on account/app status. If you cannot obtain a refresh token, use artifact download and upload manually in YouTube Studio.

### 4. Change settings
Edit `config.json` to adjust target duration and categories. The initial script templates are in `story_engine.py`. Character colors, poses, and layout are in `render.py`.

## Important
- Do not commit API keys, OAuth secrets, refresh tokens, or channel passwords.
- Never make your Google account password available to GitHub Actions.
- YouTube upload API projects may be subject to audit/verification and quota rules. Some unverified API projects may have uploads restricted to private visibility.
- YouTube monetization is not guaranteed. Repetitive or mass-produced low-value content may not qualify.
- Check that your content is suitable for your audience and accurately set the made-for-kids option.
