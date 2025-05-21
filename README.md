# wetherapp-TSG

A flask web app that displays a 7-day weather forecast for a given country using the Visual Crossing API.  
Secrets (API keys) are securely loaded from HashiCorp Vault.

This application also gets the SuperSecret from the Vault. and displays it on the website

This repo is used by An agent in azure devops to run a pipeline via azure devops pipeline.
it bulids the docker image automatically and uploads it to a docker repo. 

Then it sets the new version of the image built in another repo call helm-weather-tsg for auto deployment on azure aks via argocd.

The pull cycle for argocd is every 10 min. 

