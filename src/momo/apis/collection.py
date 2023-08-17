from ..momo import MomoProduct
import requests
from .. import BASE_URL
from datetime import datetime
from ..exceptions import APICallError


class Collection(MomoProduct):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def get_token(self):
        if self.last_generated != None:
            last = self.last_generated
            should_refresh: bool = datetime.now().timestamp() - last > self.expires_in

        else:
            should_refresh = True
        
        if self.access_token == None or should_refresh:
            url = f"{BASE_URL}/collection/token/"
            res = requests.post(url=url, 
                headers={
                    "Ocp-Apim-Subscription-Key": self.subscription_key,
                    "X-Target-Environment": self.target_environment
                },
                auth=(self.user_id, self.apikey),
            )

            if res.status_code == 200: 
                self.last_generated = datetime.now().timestamp()

                json = res.json()
                self.expires_in = float(json["expires_in"])
                self.access_token = json["access_token"]

            else:
                raise APICallError(res.status_code, res.text)

        return self.access_token


    def request_to_pay(self, transaction_id, amount, currency, external_id, party_type, 
                       party_id, payer_message="", payee_note="", callback_url=None):
        data = {
            "amount": amount,
            "currency": currency,
            "externalId": external_id,
            "payer": {
                "partyIdType": party_type,
                "partyId": party_id
            },
            "payerMessage": payer_message,
            "payeeNote": payee_note
        }

        headers={
            "Authorization": f"Bearer {self.get_token()}",
            "X-Target-Environment": self.target_environment,
            "X-Reference-Id": transaction_id,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }

        if callback_url != None:
            headers["X-Callback-Url"] = callback_url
        
        url = f"{BASE_URL}/collection/v1_0/requesttopay"
        res = requests.post(url=url, headers=headers, json=data)

        if res.status_code == 202:
            return 

        else:
            raise APICallError(res.status_code, res.text)
        

    def request_to_pay_transaction_status(self, transaction_id):
        url = f"{BASE_URL}/collection/v1_0/requesttopay/{transaction_id}"
        headers={
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Authorization": f"Bearer {self.get_token()}",
        }

        res = requests.get(url=url, headers=headers)

        if res.status_code == 200:
            return res.json()

        else:
            raise APICallError(res.status_code, res.text)

    
    def request_to_pay_delivery_notification(self, transaction_id, notification_message):
        url = f"{BASE_URL}/collection/v1_0/requesttopay/{transaction_id}/deliverynotification"

        headers={
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json",
            "notificationMessage": notification_message
        }

        data = {"notificationMessage": notification_message}
        res = requests.post(url=url, headers=headers, json=data)

        if res.status_code == 200:
            return 

        else:
            raise APICallError(res.status_code, res.text)
        

    def bc_authorize(self):
        raise NotImplementedError("bc_authorize method is not implemented yet")


    def cancel_invoice(self, 
                       invoice_id, 
                       reference_id, 
                       external_id, 
                       callback_url=None
                    ):
        
        url = f"{BASE_URL}/collection/v2_0/invoice/{invoice_id}"

        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json",
            "X-Reference-Id": reference_id
        }

        if callback_url:
            headers["X-Callback-Url"] = callback_url

        data = {"externalId": external_id}

        res = requests.get(url, headers=headers, json=data)
        if res.status_code == 200:
            return res.json()  
        else:
            raise APICallError(res.status_code, res.text)
        

    def create_invoice(self,
                       invoice_id,
                       external_id,
                       amount,
                       currency,
                       valid_duration,
                       intended_party_type,
                       intended_party_id,
                       payee_party_type,
                       payee_party_id,
                       description="",
                       callback_url=None
                       ):
        
        url = f"{BASE_URL}/collection/v2_0/invoice"
        data = {
            "externalId": external_id,
            "amount": amount,
            "currency": currency,
            "validityDuration": valid_duration,
            "intendedPayer": {
                "partyIdType": intended_party_type,
                "partyId": intended_party_id
            },
            "payee": {
                "partyIdType": payee_party_type,
                "partyId": payee_party_id
            },
            "description": description
        }

        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json",
            "X-Reference-Id": invoice_id
        }

        if callback_url:
            headers["X-Callback-Url"] = callback_url

        res = requests.get(url, headers=headers, json=data)
        if res.status_code == 202:
            return 
        else:
            raise APICallError(res.status_code, res.text)


    def create_oauth2_token(self, auth_req_id):
        url = f"{BASE_URL}/collection/oauth2/token/"
        
        headers = {
            "Authorization": f"Basic {self.get_token()}",
            "X-Target-Environment": self.target_environment,
            "Content-Type": "application/x-www-form-urlencoded",
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }

        data = {
            "grant_type": "urn:openid:params:grant-type:ciba",
            "auth_req_id": auth_req_id
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise APICallError(response.status_code, response.text)

    def create_payments(self, 
                        external_transaction_id, 
                        amount, 
                        currency, 
                        customer_reference, 
                        service_provider_user_name,
                        callback_url=None):
        
        url = f"{BASE_URL}/collection/v2_0/payment"
        
        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "X-Reference-Id": external_transaction_id,
            "X-Target-Environment": self.target_environment,
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }

        data = {
            "externalTransactionId": external_transaction_id,
            "money": {
                "amount": amount,
                "currency": currency
            },
            "customerReference": customer_reference,
            "serviceProviderUserName": service_provider_user_name
        }

        if callback_url:
            headers["X-Callback-Url"] = callback_url

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 202:
            return 
        else:
            raise APICallError(response.status_code, response.json()["message"])


    def get_account_balance(self):
        url = f"{BASE_URL}/collection/v1_0/account/balance"

        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }

        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()  
        else:
            raise APICallError(res.status_code, res.text)


    def get_account_balance_in_specific_currency(self, currency):
        url = f"{BASE_URL}/collection/v1_0/account/balance/{currency}"

        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }
        
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()  
        else:
            raise APICallError(res.status_code, res.text)


    def get_basic_userinfo(self, account_holder_msisdn):
        url = f"{BASE_URL}/collection/v1_0/accountholder/msisdn/{account_holder_msisdn}/basicuserinfo"
        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }

        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()  
        else:
            raise APICallError(res.status_code, res.text)
        

    def get_invoice_status(self):
        raise NotImplementedError("get_invoice_status method is not implemented yet")

    def get_payment_status(self):
        raise NotImplementedError("get_payment_status method is not implemented yet")

    def get_pre_approval_status(self):
        raise NotImplementedError("get_pre_approval_status method is not implemented yet")

    def get_user_info_with_consent(self):
        raise NotImplementedError("get_user_info_with_consent method is not implemented yet")

    def pre_approval(self):
        raise NotImplementedError("pre_approval method is not implemented yet")

    def request_to_withdraw_transaction_status(self, transaction_id):
        url = f"{BASE_URL}/collection/v1_0/requesttowithdrawal/{transaction_id}"
        headers={
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Authorization": f"Bearer {self.get_token()}",
        }

        res = requests.get(url=url, headers=headers)

        if res.status_code == 200:
            return res.json()

        else:
            raise APICallError(res.status_code, res.text)


    def request_to_withdraw_v1(self, transaction_id, amount, currency, external_id,
                            party_type, party_id, payer_message="", payee_note=""):
        
        url = f"{BASE_URL}/collection/v1_0/requesttowithdraw"

        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "X-Reference-Id": transaction_id,
            "X-Target-Environment": self.target_environment,
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }

        data = {
            "payeeNote": payee_note,
            "externalId": external_id,
            "amount": amount,
            "currency": currency,
            "payer": {
                "partyIdType": party_type,
                "partyId": party_id
            },
            "payerMessage": payer_message
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 202:
            return 
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        

    def request_to_withdraw_v2(self, transaction_id, amount, currency, external_id,
                            party_type, party_id, payer_message="", payee_note=""):
        
        url = f"{BASE_URL}/collection/v2_0/requesttowithdraw"

        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "X-Reference-Id": transaction_id,
            "X-Target-Environment": self.target_environment,
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }

        data = {
            "payeeNote": payee_note,
            "externalId": external_id,
            "amount": amount,
            "currency": currency,
            "payer": {
                "partyIdType": party_type,
                "partyId": party_id
            },
            "payerMessage": payer_message
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 202:
            return 
        
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        

    def validate_account_holder_status(self, account_holder_id_type, account_holder_id):
        url = f"{BASE_URL}/collection/v1_0/accountholder/{account_holder_id_type}/{account_holder_id}/active"
        
        headers = {
            "Authorization": f"Bearer { self.get_token()}",
            "X-Target-Environment": self.target_environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        
        else:
            raise APICallError(response.status_code, response.text)


