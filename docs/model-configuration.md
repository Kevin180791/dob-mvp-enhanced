# Model Configuration Guide

This guide explains how to configure and use different AI model providers in the DOB-MVP system.

## Overview

The DOB-MVP supports multiple AI model providers:

1. **OpenAI** - Cloud-based models like GPT-4, GPT-3.5, etc.
2. **Google Gemini** - Google's advanced AI models
3. **Ollama** - Local open-source models running on your network

The system allows you to:
- Configure multiple providers
- Add multiple models from each provider
- Assign specific models to different agents
- Test models directly from the UI
- Configure fallback models for reliability

## Provider Configuration

### OpenAI

To configure OpenAI as a provider:

1. Navigate to the **Model Configuration** page
2. Select the **Providers** tab
3. Click **Add Provider**
4. Enter the following information:
   - **Provider Name**: A descriptive name (e.g., "OpenAI API")
   - **Provider Type**: Select "OpenAI"
   - **API Key**: Your OpenAI API key
   - **Base URL**: (Optional) Custom API endpoint if using Azure OpenAI or a proxy
   - **Timeout**: Maximum time in seconds to wait for a response

### Google Gemini

To configure Google Gemini as a provider:

1. Navigate to the **Model Configuration** page
2. Select the **Providers** tab
3. Click **Add Provider**
4. Enter the following information:
   - **Provider Name**: A descriptive name (e.g., "Google Gemini")
   - **Provider Type**: Select "Gemini"
   - **API Key**: Your Google Gemini API key
   - **Timeout**: Maximum time in seconds to wait for a response

### Ollama (Local Models)

To configure Ollama for local models:

1. Navigate to the **Model Configuration** page
2. Select the **Providers** tab
3. Click **Add Provider**
4. Enter the following information:
   - **Provider Name**: A descriptive name (e.g., "Local Ollama")
   - **Provider Type**: Select "Ollama"
   - **Host**: The hostname or IP address where Ollama is running
   - **Port**: The port Ollama is listening on (default: 11434)
   - **Timeout**: Maximum time in seconds to wait for a response

## Model Configuration

After configuring providers, you can add models:

1. Navigate to the **Model Configuration** page
2. Select the **Models** tab
3. Click **Add Model**
4. Enter the following information:
   - **Model Name**: A descriptive name (e.g., "GPT-4 Turbo")
   - **Provider**: Select from your configured providers
   - **Model ID**: The specific model identifier (e.g., "gpt-4-turbo", "gemini-pro", "llama2")
   - **Model Type**: The type of model (text, embedding, image, multimodal)
   - **Parameters**: Configure default parameters like temperature and max tokens
   - **Active**: Enable/disable the model
   - **Default**: Set as the default model for new assignments

## Agent Assignments

To assign models to specific agents:

1. Navigate to the **Model Configuration** page
2. Select the **Assignments** tab
3. Click **Add Assignment**
4. Enter the following information:
   - **Agent ID**: The identifier of the agent (e.g., "rfi_analyst")
   - **Primary Model**: The main model to use for this agent
   - **Fallback Model**: (Optional) A backup model if the primary fails

## Testing Models

You can test models directly from the UI:

1. Navigate to the **Model Configuration** page
2. Select the **Models** tab
3. Find the model you want to test
4. Click on the "Test Model" accordion
5. Enter a test prompt
6. Click "Test Model"
7. View the response and performance metrics

## Troubleshooting

### Connection Issues

If you're having trouble connecting to a provider:

1. Check that the API key is correct
2. Verify network connectivity to the provider
3. Check if the provider service is running
4. Increase the timeout if the provider is slow to respond

### Model Performance

If a model is performing poorly:

1. Try adjusting the parameters (temperature, max tokens)
2. Check if the model is appropriate for the task
3. Consider using a different model or provider

### Ollama-Specific Issues

For Ollama:

1. Ensure Ollama is running on the specified host and port
2. Verify that the model is downloaded and available in Ollama
3. Check Ollama logs for any errors
4. Make sure the network allows connections to the Ollama server

## Best Practices

1. **Use appropriate models for each task**: 
   - Use powerful models like GPT-4 or Gemini Pro for complex reasoning
   - Use smaller models like GPT-3.5 or Llama2 for simpler tasks
   - Use specialized models for specific domains

2. **Configure fallback models**:
   - Always set a fallback model for critical agents
   - Choose a reliable fallback even if less capable

3. **Balance performance and cost**:
   - More powerful models are typically more expensive
   - Local models may be slower but have no usage costs
   - Consider caching for frequently repeated queries

4. **Security considerations**:
   - Store API keys securely
   - Be cautious about what data is sent to external providers
   - Consider using local models for sensitive information

