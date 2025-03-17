#!/bin/bash

# This script helps deploy the application to Railway

echo "Preparing to deploy to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null
then
    echo "Railway CLI is not installed. Would you like to install it? (y/n)"
    read -r install_cli
    if [ "$install_cli" = "y" ]; then
        npm i -g @railway/cli
    else
        echo "Please install Railway CLI to continue: npm i -g @railway/cli"
        exit 1
    fi
fi

# Login to Railway if not already logged in
echo "Logging in to Railway..."
railway login

# Link to the Railway project
echo "Linking to Railway project..."
railway link

# Deploy the application
echo "Deploying to Railway..."
railway up

echo "Deployment completed! Your application should now be available on Railway."
echo "Don't forget to configure the environment variables in the Railway dashboard."
echo "And update your Twilio webhook URL to point to your Railway application." 
