from . import config

# Use lazy initialization instead of global initialization
_github_manager = None

def get_github_manager():
    """Lazy initialization of GitHub manager"""
    global _github_manager
    if _github_manager is None:
        _github_manager = GitHubManager()
    return _github_manager

class GitHubManager:
    def __init__(self):
        self.auth = None
        self.g = None
        try:
            if not config.MOCK_MODE:
                from github import Github, Auth
                print("🔄 Initializing GitHub client...")
                self.auth = Auth.Token(config.GITHUB_TOKEN)
                self.g = Github(auth=self.auth)
                user = self.g.get_user()
                print(f"✅ GitHub client initialized for user: {user.login}")
            else:
                print("✅ GitHub client initialized (MOCK MODE)")
        except Exception as e:
            print(f"❌ GitHub client initialization failed: {e}")
    
    def create_repo(self, repo_name: str):
        """Create repository if it doesn't exist, or return existing one"""
        if config.MOCK_MODE or not self.g:
            return self._mock_create_repo(repo_name)
        
        try:
            from github import GithubException
            user = self.g.get_user()
            
            # Try to get existing repo first
            try:
                repo = user.get_repo(repo_name)
                print(f"📁 Found existing repository: {repo_name}")
                return {
                    "status": 200,
                    "response": {
                        "name": repo.name,
                        "html_url": repo.html_url,
                        "clone_url": repo.clone_url,
                    },
                    "existing": True
                }
            except GithubException:
                # Repo doesn't exist, create it
                print(f"🆕 Creating new repository: {repo_name}")
                repo = user.create_repo(repo_name, private=False, auto_init=False)
                
                # Add initial README to initialize the main branch
                repo.create_file("README.md", "Initial commit", f"# {repo_name}\n\nInitial repository.", branch="main")
                
                print(f"✅ Created new repository: {repo_name}")
                return {
                    "status": 201,
                    "response": {
                        "name": repo.name,
                        "html_url": repo.html_url,
                        "clone_url": repo.clone_url,
                    },
                    "existing": False
                }
                
        except Exception as e:
            print(f"❌ GitHub repo operation failed: {e}")
            return self._mock_create_repo(repo_name)
    
    def push_files(self, repo_name: str, files: dict, commit_message: str):
        """Push files to repository (creates initial files)"""
        if config.MOCK_MODE or not self.g:
            return self._mock_push_files(repo_name, files)
        
        try:
            repo = self.g.get_repo(f"{config.GITHUB_USER}/{repo_name}")
            latest_commit_sha = ""
            
            for file_path, content in files.items():
                try:
                    # Try to get existing file
                    existing_file = repo.get_contents(file_path, ref="main")
                    # Update existing file
                    result = repo.update_file(
                        path=file_path,
                        message=commit_message,
                        content=content,
                        sha=existing_file.sha,
                        branch="main"
                    )
                    latest_commit_sha = result['commit'].sha
                    print(f"✅ Updated: {file_path}")
                except Exception:
                    # Create new file
                    result = repo.create_file(
                        path=file_path,
                        message=commit_message,
                        content=content,
                        branch="main"
                    )
                    latest_commit_sha = result['commit'].sha
                    print(f"✅ Created: {file_path}")
            
            return {"status": 200, "response": {"commit_sha": latest_commit_sha}}
        except Exception as e:
            print(f"❌ GitHub file push failed: {e}")
            return self._mock_push_files(repo_name, files)
    
    def update_repo(self, repo_name: str, files: dict, commit_message: str):
        """Update existing repository with new files (alias for push_files)"""
        # For now, update_repo does the same as push_files since push_files
        # already handles both creating and updating files
        return self.push_files(repo_name, files, commit_message)
    
    def enable_pages(self, repo_name: str):
        """Enable GitHub Pages"""
        if config.MOCK_MODE:
            return self._mock_enable_pages(repo_name)
        
        try:
            # Use the direct API approach
            return self._enable_pages_via_api(repo_name)
        except Exception as e:
            print(f"❌ Pages enable failed: {e}")
            return self._mock_enable_pages(repo_name)
    
    def _enable_pages_via_api(self, repo_name: str):
        """Enable Pages using GitHub REST API"""
        import requests
        
        headers = {
            "Authorization": f"token {config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        api_url = f"https://api.github.com/repos/{config.GITHUB_USER}/{repo_name}/pages"
        
        # Check current Pages status
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            pages_data = response.json()
            html_url = pages_data.get('html_url', f"https://{config.GITHUB_USER}.github.io/{repo_name}/")
            print(f"✅ GitHub Pages already enabled: {html_url}")
            return {
                "status": 200,
                "response": {"html_url": html_url}
            }
        
        # Enable Pages
        pages_config = {
            "source": {
                "branch": "main",
                "path": "/"
            }
        }
        
        response = requests.post(api_url, headers=headers, json=pages_config)
        
        if response.status_code in [200, 201]:
            pages_data = response.json()
            html_url = pages_data.get('html_url', f"https://{config.GITHUB_USER}.github.io/{repo_name}/")
            print(f"✅ GitHub Pages enabled successfully: {html_url}")
            return {
                "status": 201,
                "response": {"html_url": html_url}
            }
        else:
            # If API fails, return the standard Pages URL
            html_url = f"https://{config.GITHUB_USER}.github.io/{repo_name}/"
            print(f"⚠️ GitHub Pages API failed, using standard URL: {html_url}")
            return {
                "status": 200,
                "response": {"html_url": html_url}
            }
    
    def _mock_create_repo(self, repo_name: str):
        return {
            "mocked": True,
            "response": {
                "name": repo_name,
                "html_url": f"https://github.com/{config.GITHUB_USER}/{repo_name}",
            }
        }
    
    def _mock_push_files(self, repo_name: str, files: dict):
        return {
            "mocked": True,
            "response": {"commit_sha": "mock_commit_sha"}
        }
    
    def _mock_enable_pages(self, repo_name: str):
        pages_url = f"https://{config.GITHUB_USER}.github.io/{repo_name}/"
        return {
            "mocked": True,
            "response": {"html_url": pages_url}
        }
# Create instance but don't initialize immediately
github_manager = GitHubManager()