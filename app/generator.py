import requests
import json
from . import config
import base64
import time

class CodeGenerator:  # Changed from AIPipeGenerator to CodeGenerator
    def __init__(self):
        self.token = config.OPENAI_API_KEY  # Your AIPipe token
        self.email = config.AIPIPE_EMAIL    # Your email for AIPipe
        self.base_url = "https://aipipe.org/openrouter/v1"
        print("🔄 Initializing AIPipe client...")
        
        # Validate that we have the required credentials
        if not self.token or not self.email:
            print("❌ AIPipe token or email missing in environment variables")
    
    def generate_app(self, brief: str, attachments: list) -> dict:
        """Generate application code using AIPipe with GPT-4.1-nano"""
        print(f"📝 Generating app with brief: {brief[:50]}...")
        
        # If in MOCK_MODE, use fallback
        if config.MOCK_MODE:
            print("🔄 Using mock code generation")
            return self._create_fallback_app(brief)
        
        try:
            # Build the messages for the chat completion
            messages = self._build_messages(brief, attachments)
            
            # Call AIPipe API
            response = self._call_aipipe(messages)
            
            # Parse the response
            if response and "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                print("✅ AIPipe response received successfully")
                return self._parse_code_response(content, brief)
            else:
                print("❌ AIPipe returned empty response")
                if response:
                    print(f"Response structure: {response}")
                return self._create_fallback_app(brief)
                
        except Exception as e:
            print(f"❌ AIPipe generation failed: {e}")
            return self._create_fallback_app(brief)
    
    def _build_messages(self, brief: str, attachments: list) -> list:
        """Build the messages array for the chat completion"""
        
        # Process attachments for context
        attachment_context = ""
        for att in attachments:
            if att['name'].endswith(('.txt', '.md', '.csv', '.json')):
                try:
                    if att['url'].startswith('data:'):
                        header, data = att['url'].split(',', 1)
                        content = base64.b64decode(data).decode('utf-8')
                        attachment_context += f"\n\nFile: {att['name']}\n```\n{content}\n```"
                except Exception as e:
                    print(f"⚠️ Failed to process attachment {att['name']}: {e}")
        
        system_message = {
            "role": "system",
            "content": """You are an expert web developer. Generate minimal, complete web applications based on requirements.

Requirements:
- Single HTML file with embedded CSS and JavaScript
- MIT License in LICENSE file
- Professional README.md
- Bootstrap 5 for styling (loaded from CDN)
- Vanilla JavaScript, no frameworks
- Mobile responsive
- Handle errors gracefully

Return ONLY a JSON object with filenames as keys and file content as values.

Example format:
{
  "index.html": "<!DOCTYPE html>...",
  "README.md": "# App Name...",
  "LICENSE": "MIT License..."
}"""
        }

        user_content = f"""Create a web application with these requirements:

BRIEF: {brief}

{attachment_context}

Required files:
- index.html (main application with Bootstrap 5)
- README.md (professional documentation)
- LICENSE (MIT License)

Generate the complete file structure as JSON."""

        user_message = {
            "role": "user",
            "content": user_content
        }
        
        return [system_message, user_message]
    
    def _call_aipipe(self, messages: list):
        """Make API call to AIPipe OpenRouter endpoint"""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-User-Email": self.email,  # Include email in headers
            "User-Agent": "LLM-Code-Deployer/1.0"  # Identify your application
        }
        
        payload = {
            "model": "openai/gpt-4.1-nano",  # Using the specific model you mentioned
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            print("🌐 Calling AIPipe API with GPT-4.1-nano...")
            print(f"📧 Using email: {self.email}")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120  # 120 second timeout for larger responses
            )
            
            print(f"📊 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ AIPipe API call successful")
                
                # Debug: Print token usage if available
                if "usage" in result:
                    usage = result["usage"]
                    print(f"📈 Token usage: {usage.get('prompt_tokens', 'N/A')} prompt, {usage.get('completion_tokens', 'N/A')} completion")
                
                return result
            else:
                print(f"❌ AIPipe API error: {response.status_code}")
                print(f"Error details: {response.text}")
                
                # Provide more specific error messages
                if response.status_code == 401:
                    print("🔐 Authentication failed. Check your token and email.")
                elif response.status_code == 429:
                    print("⏳ Rate limit exceeded. Try again later.")
                elif response.status_code == 500:
                    print("🔧 Server error. The AIPipe service might be down.")
                
                return None
                
        except requests.exceptions.Timeout:
            print("❌ AIPipe API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ AIPipe connection failed: {e}")
            return None
    
    def _parse_code_response(self, content: str, brief: str) -> dict:
        """Parse the AI response into file structure"""
        try:
            # Clean the content - remove markdown code blocks if present
            cleaned_content = content.strip()
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.startswith('```'):
                cleaned_content = cleaned_content[3:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            # Try to parse as JSON
            generated_files = json.loads(cleaned_content)
            
            # Validate required files
            required_files = ['index.html', 'README.md', 'LICENSE']
            for req_file in required_files:
                if req_file not in generated_files:
                    print(f"⚠️ Missing required file: {req_file}, using default")
                    generated_files[req_file] = self._get_default_file(req_file, brief)
            
            print(f"✅ Successfully parsed {len(generated_files)} files from AI response")
            return generated_files
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw content received: {content[:200]}...")
            
            # If JSON parsing fails, try to extract code blocks
            return self._extract_files_from_text(content, brief)
    
    def _extract_files_from_text(self, content: str, brief: str) -> dict:
        """Extract files from text response when JSON parsing fails"""
        print("🔄 Attempting to extract files from text response...")
        
        files = {
            "index.html": self._get_default_file("index.html", brief),
            "README.md": self._get_default_file("README.md", brief),
            "LICENSE": self._get_default_file("LICENSE", brief)
        }
        
        # Simple heuristic: look for HTML content
        if "<!DOCTYPE html>" in content or "<html>" in content:
            start = content.find("<!DOCTYPE html>")
            if start == -1:
                start = content.find("<html>")
            end = content.find("</html>") + 7 if content.find("</html>") != -1 else len(content)
            files["index.html"] = content[start:end]
            print("✅ Extracted HTML from response")
        
        return files
    
    def _get_default_file(self, filename: str, brief: str) -> str:
        """Get default content for missing files"""
        if filename == "index.html":
            return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated App</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Generated Application</h1>
        <p class="lead">{brief}</p>
        <div class="alert alert-success">✅ Application generated with AIPipe + GPT-4.1-nano</div>
    </div>
</body>
</html>'''
        elif filename == "README.md":
            return f'''# Generated Application

## Description
{brief}

## Setup
1. Open index.html in a web browser
2. Or deploy to any static hosting service

## Features
- Responsive design with Bootstrap 5
- Modern web standards
- Generated using AIPipe with GPT-4.1-nano

## License
MIT'''
        elif filename == "LICENSE":
            return '''MIT License

Copyright (c) 2024 Generated App

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''
        return ""
    
    def _create_fallback_app(self, brief: str) -> dict:
        """Fallback app if everything fails"""
        return {
            "index.html": self._get_default_file("index.html", brief),
            "README.md": self._get_default_file("README.md", brief),
            "LICENSE": self._get_default_file("LICENSE", brief)
        }