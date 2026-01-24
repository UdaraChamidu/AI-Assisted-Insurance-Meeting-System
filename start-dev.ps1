# Quick Start Script for Development

# Run this script to start everything for local development

Write-Host "🚀 Starting Insurance Agent System..." -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found! Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file. Please edit it with your API keys!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Press any key to continue after updating .env..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Start backend
Write-Host "📦 Starting Backend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python main.py"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "🎨 Starting Frontend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

# Wait a bit
Start-Sleep -Seconds 2

# Prompt for ngrok
Write-Host ""
Write-Host "🌐 Do you want to start ngrok tunnel? (Needed for Twilio webhooks)" -ForegroundColor Yellow
Write-Host "Press Y to start ngrok, or any other key to skip..." -ForegroundColor Yellow
$response = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

if ($response.Character -eq 'y' -or $response.Character -eq 'Y') {
    Write-Host ""
    Write-Host "🔗 Starting ngrok tunnel..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "ngrok http 8000"
    
    Start-Sleep -Seconds 3
    Write-Host ""
    Write-Host "✅ ngrok tunnel started!" -ForegroundColor Green
    Write-Host "📊 View ngrok requests at: http://localhost:4040" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access points:" -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
if ($response.Character -eq 'y' -or $response.Character -eq 'Y') {
    Write-Host "   ngrok Inspector: http://localhost:4040" -ForegroundColor White
}
Write-Host ""
Write-Host "📖 See docs/TWILIO_SETUP.md for Twilio configuration" -ForegroundColor Yellow
Write-Host ""
