# 🚀 Cloud Deployment Guide

## Prerequisites
- Google Cloud account with billing enabled
- Google Cloud SDK installed
- Docker installed (for local testing)

## Step 1: Setup Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace with your actual project ID)
gcloud config set project your-project-id-123456

# Enable required services
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com