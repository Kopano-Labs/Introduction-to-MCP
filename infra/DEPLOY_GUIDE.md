---
title: Infrastructure Deployment Guide (azd / Bicep)
created: 2026-04-11
updated: 2026-04-11
author: Germini (Lead - Elite)
tags:
  - azure
  - azd
  - bicep
  - infra
status: active
---

# Deployment Guide: Kopano Context Cloud Rollout

> This guide explains how to use the `infra/` templates to deploy Kopano Context to **Azure South Africa North**.

## 🛠️ Prerequisites
- **Azure CLI:** `az login`
- **Azure Developer CLI (azd):** `azd login`
- **Permissions:** You must have `Owner` or `Contributor` + `User Access Administrator` rights on the subscription to configure Key Vault RBAC.

---

## 🚀 The Core Workflow

### 1. Initialize
Navigate to the root and ensure the `azure.yaml` (if present) points to the correct services.

### 2. Provision & Deploy
Run the following command to provision the hardware and deploy the code in one motion:
```powershell
azd up
```
*Note: `azd` will prompt for a location. Select `southafricanorth`.*

### 3. Hydrate Secrets
The Bicep template creates the Key Vault, but you must manually inject the secrets (unless using `azd env set`):
```powershell
az keyvault secret set --vault-name <vault-name> --name "AZURE-OPENAI-KEY" --value "<your-key>"
az keyvault secret set --vault-name <vault-name> --name "MONGODB-URI" --value "<your-uri>"
az keyvault secret set --vault-name <vault-name> --name "CLERK-SECRET-KEY" --value "<your-key>"
```

### 4. Verify Identity Access
The App Service uses a **Managed Identity**. Ensure the `Key Vault Secrets User` role is assigned to the App Service Identity for the production vault.

---

## 📈 Monitoring
Once deployed, check the **Log Stream** in the Azure Portal or use **Application Insights** to monitor neural traffic and API latency.

## ✅ SafeSkill Production Rule
Never deploy with `SCM_DO_BUILD_DURING_DEPLOYMENT=false` in production unless using a pre-baked Docker image, as this ensures all dependencies are validated during the cloud build phase.
