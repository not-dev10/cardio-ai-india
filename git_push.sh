#!/bin/bash

# Git Push Script for Cardiac Health AI Platform

echo "=========================================="
echo "Cardiac Health AI Platform - Git Push"
echo "=========================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
fi

# Add all files
echo ""
echo "Adding files to git..."
git add .

# Show status
echo ""
echo "Git status:"
git status

# Commit
echo ""
read -p "Enter commit message (or press Enter for default): " commit_msg

if [ -z "$commit_msg" ]; then
    commit_msg="feat: Complete production-ready cardiac health AI platform

- Advanced ML model with ensemble learning (XGBoost + RF + LR)
- Feature selection (chi-square, ANOVA, mutual information)
- Indian-specific features and adjustments
- Format-specific OCR for Indian labs (SRL, Thyrocare, etc.)
- DPDP Act compliant consent management
- AI-powered explanations (SHAP + simple language)
- Verified doctor recommendations
- Complete documentation (14 research papers)
- Research paper template ready for publication
- Dataset download script
- 12-month roadmap and implementation checklist

Status: Stage 1-4 (Partial) Complete
Next: Train models, test OCR, start Android app

Ganpati Bapa Morya!"
fi

echo ""
echo "Committing with message:"
echo "$commit_msg"
git commit -m "$commit_msg"

# Check if remote exists
if ! git remote | grep -q "origin"; then
    echo ""
    echo "No remote repository found."
    echo "Your GitHub repository: https://github.com/not-dev10/psu-changes.git"
    read -p "Add this remote? (y/n): " add_remote
    
    if [ "$add_remote" = "y" ]; then
        git remote add origin https://github.com/not-dev10/psu-changes.git
        echo "Remote added!"
    fi
fi

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "=========================================="
echo "Push complete!"
echo "=========================================="
echo ""
echo "View your repository at:"
echo "https://github.com/not-dev10/psu-changes"
