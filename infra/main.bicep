@description('The location for all resources. Defaulting to South Africa North for POPIA compliance.')
param location string = 'southafricanorth'

@description('The name of the environment (e.g., prod, staging).')
param envName string = 'prod'

@description('The name of the Kopano Context core application.')
param appName string = 'kopano-context'

var uniqueSuffix = uniqueString(resourceGroup().id)
var vaultName = 'kv-${appName}-${uniqueSuffix}'
var planName = 'asp-${appName}-${envName}'
var webAppName = 'app-${appName}-${envName}-${uniqueSuffix}'

// --- KEY VAULT (SECRET ANCHOR) ---
resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: vaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enabledForDeployment: true
    enabledForTemplateDeployment: true
  }
}

// --- APP SERVICE PLAN ---
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: planName
  location: location
  sku: {
    name: 'S1'
    tier: 'Standard'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// --- APP SERVICE (CORE CONTROL PLANE) ---
resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: webAppName
  location: location
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'KOPANO_ENV'
          value: envName
        }
        {
          name: 'AZURE_OPENAI_KEY'
          value: '@Microsoft.KeyVault(SecretUri=${keyVault.properties.vaultUri}secrets/AZURE-OPENAI-KEY/)'
        }
        {
          name: 'MONGODB_URI'
          value: '@Microsoft.KeyVault(SecretUri=${keyVault.properties.vaultUri}secrets/MONGODB-URI/)'
        }
        {
          name: 'CLERK_SECRET_KEY'
          value: '@Microsoft.KeyVault(SecretUri=${keyVault.properties.vaultUri}secrets/CLERK-SECRET-KEY/)'
        }
      ]
    }
  }
}

output webAppUrl string = webApp.properties.defaultHostName
output vaultUri string = keyVault.properties.vaultUri
