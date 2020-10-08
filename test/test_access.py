from init import untrusted
from init import consumer
from access import *
from consent import role_reg
import random
import string

init_provider()

# use consumer certificate to register
email   = "barun@iisc.ac.in"
assert reset_role(email) == True
org_id = add_organization("iisc.ac.in")

# delete all old policies using acl/set API
policy = "x can access x"
r = untrusted.set_policy(policy)
assert r['success'] is True

# provider ID of abc.xyz@rbccps.org
provider_id = 'rbccps.org/f3dad987e514af08a4ac46cf4a41bd1df645c8cc'

##### consumer #####

resource_group = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
resource_id = provider_id + '/rs.example.com/' + resource_group

def test_consumer_no_rule_set():
        # token request should fail
        body = {"id" : resource_id + "/someitem", "apis" : ["/ngsi-ld/v1/entities"] }
        r = consumer.get_token(body)
        assert r['success']     is False

def test_consumer_reg():
        r = role_reg(email, '9454234223', name , ["consumer"], None, csr)
        assert r['success']     == True
        assert r['status_code'] == 200

def test_no_caps():
        # No capabilities
        r = untrusted.provider_access(email, 'consumer', resource_id, 'resourcegroup')
        assert r['success']     == False
        assert r['status_code'] == 400

def test_invalid_caps():
        # Invalid capabilities
        caps = ["hello", "world"]
        r = untrusted.provider_access(email, 'consumer', resource_id, 'resourcegroup', caps)
        assert r['success']     == False
        assert r['status_code'] == 400

def test_get_temporal_cap():
        caps = ['temporal'];
        r = untrusted.provider_access(email, 'consumer', resource_id, 'resourcegroup', caps)
        assert r['success']     == True
        assert r['status_code'] == 200

def test_get_same_cap():
        # same capability
        caps = ['temporal'];
        r = untrusted.provider_access(email, 'consumer', resource_id, 'resourcegroup', caps)
        assert r['success']     == False
        assert r['status_code'] == 403

def test_get_token_no_api():
        # token request will not pass without API
        body    = { "id"    : resource_id + "/someitem"}
        r       = consumer.get_token(body)
        assert r['success']     is False

def test_get_temporal_token():
        body = {"id" : resource_id + "/someitem", "apis" : ["/ngsi-ld/v1/entities/" + resource_id] }
        r = consumer.get_token(body)
        assert r['success']     is True

        body = {"id" : resource_id + "/someitem", "apis" : ["/ngsi-ld/v1/temporal/entities"] }
        r = consumer.get_token(body)
        assert r['success']     is True

def test_get_token_no_access():
        # temporal does not have /entities
        body = {"id" : resource_id + "/someitem", "apis" : ["/ngsi-ld/v1/entities", "/ngsi-ld/v1/temporal/entities"] }
        r = consumer.get_token(body)
        assert r['success']     is False

def test_get_complex_api_token():
        # will not work for other APIs
        body = {"id" : resource_id + "/someitem", "apis" : ["/ngsi-ld/v1/entityOperations/query"] }
        r = consumer.get_token(body)
        assert r['success']     is False

def test_get_same_cap_in_set():
        # temporal rule already exists
        caps = ['subscription', 'temporal'];
        r = untrusted.provider_access(email, 'consumer', resource_id, 'resourcegroup', caps)
        assert r['success']     == False
        assert r['status_code'] == 403

def test_get_subscription_cap():
        caps = ['subscription'];
        r = untrusted.provider_access(email, 'consumer', resource_id, 'resourcegroup', caps)
        assert r['success']     == True
        assert r['status_code'] == 200

def test_get_subscription_token():
        body = {"id" : resource_id + "/someitem", "apis" : ["/ngsi-ld/v1/subscription"] }
        r = consumer.get_token(body)
        assert r['success']     is True

def test_get_complex_cap():
        # complex
        caps = ['complex']
        r = untrusted.provider_access(email, 'consumer', resource_id, 'resourcegroup', caps)
        assert r['success']     == True
        assert r['status_code'] == 200

def test_get_complex_token():
        body = {"id" : resource_id + "/someitem", "apis" : ["/ngsi-ld/v1/entityOperations/query"] }
        r = consumer.get_token(body)
        assert r['success']     is True

        body = {"id" : resource_id + "/someitem", "apis" : ["/ngsi-ld/v1/entities", "/ngsi-ld/v1/temporal/entities"] }
        r = consumer.get_token(body)
        assert r['success']     is True

def test_get_all_caps():
        # try all 3 caps
        resource_id = provider_id + '/rs.example.co.in/' + resource_group
        caps = ['complex','subscription', 'temporal']
        r = untrusted.provider_access(email, 'consumer', resource_id, 'resourcegroup', caps)
        assert r['success']     == True
        assert r['status_code'] == 200

def get_token_all_apis():
        apis = ["/ngsi-ld/v1/entityOperations/query", "/ngsi-ld/v1/entities", "/ngsi-ld/v1/temporal/entities","/ngsi-ld/v1/entities/" + resource_id, "/ngsi-ld/v1/subscription"]
        body = {"id" : resource_id + "/someitem", "apis" : apis }
        r = consumer.get_token(body)
        assert r['success']     is True

def test_set_existing_rule():
        # rule exists
        caps = ['complex','subscription', 'temporal']
        r = untrusted.provider_access(email, 'consumer', resource_id, 'resourcegroup', caps)
        assert r['success']     == False
        assert r['status_code'] == 403

def test_set_rule_for_invalid_user():
        # user does not exist
        r = untrusted.provider_access(email, 'onboarder', resource_id, 'resourcegroup')
        assert r['success']     == False
        assert r['status_code'] == 403

##### onboarder #####

def test_get_onboarder_token_fail():
        body = { "id"    : provider_id + "/catalogue.iudx.io/catalogue/crud" }

        # onboarder token request should fail
        r = consumer.get_token(body)
        assert r['success']     is False

def test_reg_onboarder():
        r = role_reg(email, '9454234223', name , ["onboarder"], org_id)
        assert r['success']     == True
        assert r['status_code'] == 200

def test_set_onboarder_rule():
        r = untrusted.provider_access(email, 'onboarder')
        assert r['success']     == True
        assert r['status_code'] == 200

def test_get_onboarder_token():
        body = { "id"    : provider_id + "/catalogue.iudx.io/catalogue/crud" }

        r = consumer.get_token(body)
        assert r['success']     is True
        assert None != r['response']['token']

def test_set_onboarder_rule_again():
        r = untrusted.provider_access(email, 'onboarder')
        assert r['success']     == False
        assert r['status_code'] == 403

##### data ingester #####

diresource_group = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
diresource_id = provider_id + "/rs.example.com/" + diresource_group

body        = {"id" : diresource_id + "/someitem", "api" : "/iudx/v1/adapter" }

def test_get_ingester_token_fail():
        # data ingester token request should fail
        r = consumer.get_token(body)
        assert r['success']     is False

def test_reg_ingester():
        r = role_reg(email, '9454234223', name , ["data ingester"], org_id)
        assert r['success']     == True
        assert r['status_code'] == 200

def test_invalid_resource_type():
        # invalid resource type
        r = untrusted.provider_access(email, 'data ingester', diresource_id, 'catalogue')
        assert r['success']     == False
        assert r['status_code'] == 400

def test_set_ingester_rule():
        r = untrusted.provider_access(email, 'data ingester', diresource_id, 'resourcegroup')
        assert r['success']     == True
        assert r['status_code'] == 200

def test_token_without_api():
        # without adapter API
        body = {"id"    : diresource_id + "/*" }

        r = consumer.get_token(body)
        assert r['success']     is False

def test_get_ingester_token():
        body = {"id"    : diresource_id + "/*" }
        body["api"] = "/iudx/v1/adapter"
        r = consumer.get_token(body)
        assert r['success']     is True

def test_token_for_item():
        # request for other items in resource group
        body = {"id" : diresource_id + "/someitem/someotheritem", "api" : "/iudx/v1/adapter" }
        r = consumer.get_token(body)
        assert r['success']     is True

def test_token_invalid_rid():
        # invalid resource ID
        r = untrusted.provider_access(email, 'data ingester', '/aaaaa/sssss/sada/', 'resourcegroup')
        assert r['success']     == False
        assert r['status_code'] == 400

        r = untrusted.provider_access(email, 'data ingester', '/aaaaa/sssss', 'resourcegroup')
        assert r['success']     == False
        assert r['status_code'] == 400

def test_get_access_rules():
        r = untrusted.get_provider_access()
        assert r['success']     == True
        assert r['status_code'] == 200
        rules = r['response']
        for r in rules:
                if r['email'] == email and r['role'] == 'consumer':
                        assert set(r['capabilities']).issubset(set(['temporal', 'subscription', 'complex']))
                        assert len(r['capabilities']) <= 3 and len(r['capabilities']) >= 1
                if r['email'] == email and r['role'] == 'onboarder':
                        assert r['item_type'] == 'catalogue'
                if r['email'] == email and r['role'] == 'data ingester':
                        assert r['policy'].endswith('"/iudx/v1/adapter"')
