from .sandbox import sandbox_create_api_key, sandbox_create_user

class MomoProduct():
    access_token: str | None = None
    last_generated: float | None = None
    expires_in = .1
    
    def __init__(self, subscription_key, sandbox, user_id, apikey=None) -> None:
        self.subscription_key = subscription_key
        self.user_id = user_id
        
        if sandbox or apikey == None:
            self.apikey = self.get_apikey_sandbox()
            self.target_environment = "sandbox"

        else:
            self.target_environment = "production"
            self.apikey = apikey

    def get_apikey_sandbox(self):
        try: 
            if sandbox_create_user(self.user_id, self.subscription_key):
                ...
            else:
                raise Exception("Failed to create a Sandbox user")
            
            api_key = sandbox_create_api_key(self.user_id, self.subscription_key)

            if api_key:
                return api_key

            else:
                raise Exception("Could not get api key")                

        except Exception as e:
            ...