$ErrorActionPreference = "Stop"
Write-Host "Downloading Google Cloud CLI... (this might take a minute)"
$ProgressPreference = 'SilentlyContinue'
$zipPath = "$env:TEMP\gcloud.zip"
$extractPath = "$env:TEMP\gcloud_cli"

if (-not (Test-Path "$extractPath\google-cloud-sdk\bin\gcloud.cmd")) {
    Invoke-WebRequest -Uri "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-windows-x86_64.zip" -OutFile $zipPath
    Write-Host "Extracting..."
    if (Test-Path $extractPath) { Remove-Item -Recurse -Force $extractPath }
    Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
}

$gcloud = "$extractPath\google-cloud-sdk\bin\gcloud.cmd"

Write-Host "`n==============================================`n"
Write-Host "⚠️ IMPORTANT: A BROWSER WINDOW WILL NOW OPEN."
Write-Host "Please select your Google Account and click 'Allow'."
Write-Host "`n==============================================`n"

& $gcloud auth login

Write-Host "Authentication successful! Setting up project..."
& $gcloud config set project dark-carport-494814-q1

Write-Host "Deploying your application to Cloud Run! (This will take ~2 minutes)..."
& $gcloud run deploy vote-guide-ai --source . --region us-central1 --allow-unauthenticated --quiet --set-env-vars="GEMINI_API_KEY=AIzaSyD4neEewnZwyZJ1O8apaDupn8Mw3iRWUMc"

Write-Host "DEPLOYMENT COMPLETE!"
